import streamlit as st
import pandas as pd
import random
import competitorAnalysis
import os

#load data
df = pd.read_json("processed_reviews.json", orient="index")

rest1_name = "Oceana"
rest2_name = "The Smith - Nomad"

def displayReview(indx):
    st.write(f"## Review {indx + 1}")

    # Display stars and dining date
    stars = ' '.join('⭐' for _ in range(df.loc[indx, 'overall_rating']))

    date = df.loc[indx, 'date']
    if "day" in date.lower():
        st.write(f"{stars} | Dined {date} ")
    else:
        st.write(f"{stars} | Dined on {date} ")

    # Display ratings
    st.markdown(f"**Overall:** {df.loc[indx, 'overall_rating']} | "
                f"**Food:** {df.loc[indx, 'food_rating']} | "
                f"**Service:** {df.loc[indx, 'service_rating']}")

    # Highlighted review text
    review_text = df.loc[indx, 'cleaned_review']

    # Highlight food comments
    review_text = review_text.replace(
        df.loc[indx, 'food_comments'], 
        f'<mark style="background-color:yellow;">{df.loc[indx, "food_comments"]}</mark>'
    )

    # Highlight service comments
    review_text = review_text.replace(
        df.loc[indx, 'service_comments'], 
        f'<mark style="background-color:lightblue;">{df.loc[indx, "service_comments"]}</mark>'
    )

    # Display review text
    st.markdown(review_text, unsafe_allow_html=True)

    # Comments
    st.markdown(
        f'<mark style="background-color:yellow;"><b>Food Comments:</b> {df.loc[indx, "food_comments"]}</mark>', 
        unsafe_allow_html=True
    )
    st.markdown(
        f'<mark style="background-color:lightblue;"><b>Service Comments:</b> {df.loc[indx, "service_comments"]}</mark>', 
        unsafe_allow_html=True
    )

    # Sentiments
    st.markdown(
        f'<mark style="background-color:yellow;"><b>Food Sentiment:</b> {df.loc[indx, "food_sentiment"]}</mark>', 
        unsafe_allow_html=True
    )
    st.markdown(
        f'<mark style="background-color:lightblue;"><b>Service Sentiment:</b> {df.loc[indx, "service_sentiment"]}</mark>', 
        unsafe_allow_html=True
    )

    # Highlight overall sentiment based on value
    overall_sentiment = df.loc[indx, 'overall_sentiment']
    if overall_sentiment == "positive":
        st.markdown(
            f'<mark style="background-color:green;color:white"><b>Overall Sentiment:</b> {overall_sentiment}</mark>', 
            unsafe_allow_html=True
        )
    elif overall_sentiment == "negative":
        st.markdown(
            f'<mark style="background-color:red;color:white"><b>Overall Sentiment:</b> {overall_sentiment}</mark>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<mark style="background-color:gray;color:white"><b>Overall Sentiment:</b> {overall_sentiment}</mark>', 
            unsafe_allow_html=True
        )

st.title("Oceana Restaurant Reviews")
st.write("Browse through customer reviews of Oceana Restaurant with detailed ratings and sentiments.")

#sidebar
st.sidebar.header("Navigation")

#search bar
search_query = st.sidebar.text_input("🔍 Search for reviews", help="Search for reviews containing specific keywords.")

#scrap the competitor data
competitor_url = st.sidebar.text_input("🔍 Enter URL to scrap for competitor analysis")
#if the url is defined then get the restaurant name from the website
if competitor_url:
    comp_name = competitorAnalysis.getName(competitor_url)
scrap_till = st.sidebar.text_input("Scrap reviews till page number: ")

#if the scrapping inputs are defined and the reviews havent been scrapped already i.e. the file with the rest name doesnt exist
if competitor_url and scrap_till and not os.path.isfile(comp_name + ".csv"): 
    try:
        scrap_till = int(scrap_till)
        if scrap_till < 1:
            st.error("Please enter a page number greater than or equal to 1.")
        else:
            rest2_name = comp_name  # Get the name of the competitor through the URL
            st.write(f"Scraping reviews for {rest2_name}...")
            competitorAnalysis.scrape_reviews(competitor_url, from_page=1, to_page=scrap_till)
            st.success(f"Reviews for {rest2_name} scraped successfully!")
            scrap_till = ""
            competitor_url = ""
            competitorAnalysis.compare_graphs(rest1_name,rest2_name)

    except ValueError:
        st.error("Please enter a valid number for the page limit.")

#display 10 reviews per page
reviews_per_page = 10
num_pages = (len(df) + reviews_per_page - 1) // reviews_per_page  #total num of pages

#page selector
current_page = st.sidebar.selectbox("Select Page", range(1, num_pages + 1))
start_idx = (current_page - 1) * reviews_per_page
end_idx = min(start_idx + reviews_per_page, len(df))

st.write(f"### Page {current_page} of {num_pages}")

#generate a random index
if st.sidebar.button("🔀 Show Random Review"):
    start_idx = random.randint(0, df.shape[0] - 1)
    end_idx = start_idx + 1

if st.sidebar.button(f'Show competitor analysis of {rest1_name} with "{rest2_name}"'):
    competitorAnalysis.compare_graphs(rest1_name,rest2_name)


#if search query is defined
if search_query:
    matching_reviews = df[df['cleaned_review'].str.contains(search_query, case=False, na=False)]
    if not matching_reviews.empty:
        st.write(f"### Found {len(matching_reviews)} matching reviews for '{search_query}':")
        for idx, row in matching_reviews.iterrows():
            displayReview(idx)
    else:
        st.warning(f"No reviews found for '{search_query}'.")
#otherwise display using page indexes
else:
    for i in range(start_idx, end_idx):
        displayReview(i)


#make the background black with white text
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000;  /* Black background */
        color: #fff;             /* White text */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

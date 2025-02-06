import requests
from requests.exceptions import Timeout, ConnectionError, RequestException
from bs4 import BeautifulSoup
import pandas as pd
import re    
import string
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta
import datetime as dt

def scrape_reviews(url, from_page=1, to_page=5):

    # Add headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    reviews_data = []

    for page in range(from_page, to_page + 1):

        # Construct the paginated URL
        page_url = f"{url}&page={page}"

        try:
            response = requests.get(page_url, headers=headers, timeout=10)
        except Timeout as e:
            print("Request timed out:", e)
            continue
        except ConnectionError as e:
            print("Connection error:", e)
            continue
        except RequestException as e:
            print("An error occurred during the request:", e)
            continue

        
        print(f"Scraping page {page}")

        # Check if the response is successful
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
            break

        #if the page is invalid then it will automatically redirect to page 1
        if url + "&page=1" == response.url and page != 1:
            print("Max num of pages reached")
            break
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract review divs
        review_containers = soup.find_all("div", class_="MpiILQAMSSg-")
        if not review_containers:
            print(f"No reviews found on page {page}.")
            continue

        for container in review_containers:
            try:
                # Extract the date
                date_element = container.find("p", class_="iLkEeQbexGs-")
                date = date_element.text.strip() if date_element else None

                # Clean the date if needed
                if date:
                    words_to_remove = r'\b(Dined|on)\b'
                    date = re.sub(words_to_remove, '', date, flags=re.IGNORECASE).strip()

                # Extract the ratings
                ratings = container.find_all("span", class_="-y00OllFiMo-")
                overall_rating = int(ratings[0].text.strip()) if len(ratings) > 0 else None
                food_rating = int(ratings[1].text.strip()) if len(ratings) > 1 else None
                service_rating = int(ratings[2].text.strip()) if len(ratings) > 2 else None
                ambience_rating = int(ratings[3].text.strip()) if len(ratings) > 3 else None

                reviews_data.append({
                    "date": date,
                    "overall_rating": overall_rating,
                    "food_rating": food_rating,
                    "service_rating": service_rating,
                    "ambience_rating": ambience_rating
                })
            except AttributeError:
                continue

    # Return the DataFrame or None if no data was scraped
    if reviews_data:
        df = pd.DataFrame(reviews_data)
        name = getName(url)
        save(df,name + '.csv')
        return df
    else:
        print("No reviews scraped.")
        return None

def save(df, fileName):
    df = df.dropna().reset_index()
    df.to_csv(fileName, index=False)

def getName(url):


    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    #retry 5 times
    for _ in range(5):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            break
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
    else:
        raise RuntimeError(f"Failed to fetch URL {url} after multiple attempts")

    soup = BeautifulSoup(response.text, "html.parser")

    container = soup.find("h1", class_="E-vwXONV9nc-")
    if container:
        name = container.text.strip().lower()
        return name
    else:
        #if we didnt find the name from the website then extract it from the url
        #get the index of the first char after .com/
        start = url.find(".com/") + len(".com/")
        if start == -1:  #if ".com/" not found
            return ""

        #extract the part of the string after ".com/"
        segment = ""
        for char in url[start:]:
            if char != '?':  #extract the characters till we encounter '?'
                segment += char
            else:
                break

        return segment.replace("r/", "") #remove "r/" from the string

def convert_date(date):
    if "days ago" in date:
        #extract the number of days
        days_ago = int(date.split()[0])
        #calculate the absolute date
        return datetime.now() - timedelta(days=days_ago)
    else:
        #parse absolute date formats
        return pd.to_datetime(date, format="%B %d, %Y", errors='coerce')

def compare_graphs(res1_name, res2_name):

    try:
        #load
        res1_name = res1_name.lower()
        res2_name = res2_name.lower()
        df1 = pd.read_csv(f"{res1_name}.csv")
        df2 = pd.read_csv(f"{res2_name}.csv")
    except FileNotFoundError as e:
        st.error(f'Error: {e},\n Enter url on "Scrap Competitor" search bar to get the data')
        return

    #drop unnecessary columns
    df1 = df1.drop(columns=["review", "cleaned_review"], errors='ignore')
    df2 = df2.drop(columns=["review", "cleaned_review"], errors='ignore')

    #convert dates
    df1['date'] = df1['date'].apply(convert_date)
    df2['date'] = df2['date'].apply(convert_date)

    #sort by date
    df1 = df1.sort_values(by="date")
    df2 = df2.sort_values(by="date")

    st.title(f"Comparison of {res1_name} and {res2_name}")

    #histogram
    fig3, ax3 = plt.subplots()
    ax3.hist(df1['overall_rating'], bins=10, label=res1_name, color='blue')
    ax3.hist(df2['overall_rating'], bins=10, label=res2_name, color='orange')
    ax3.set_title("Histogram: Distribution of Overall Ratings")
    ax3.set_xlabel("Overall Rating")
    ax3.set_ylabel("Frequency")
    ax3.legend()
    st.pyplot(fig3)

    #bar plot
    fig4, ax4 = plt.subplots()
    grouped_df1 = df1.groupby(df1['date'].dt.date)['overall_rating'].mean()
    grouped_df2 = df2.groupby(df2['date'].dt.date)['overall_rating'].mean()
    ax4.bar(grouped_df1.index, grouped_df1.values, label=res1_name, color='blue')
    ax4.bar(grouped_df2.index, grouped_df2.values, label=res2_name, color='orange')
    ax4.set_title("Bar Plot: Average Daily Overall Ratings")
    ax4.set_xlabel("Date")
    ax4.set_ylabel("Average Overall Rating")
    ax4.legend()
    st.pyplot(fig4)

# Restaurant Reviews Web Scraping and Sentiment Analysis

## Summary

- [`Scrapped reviews`](./scrapping.ipynb) for "Oceana" on opentable.com using BeautifulSoup
- Cleaned the [`dataset`](./oceana.csv)
- Performed sentiment analysis using Anthropic's API. [`The dataset`](./processed_reviews.json)
- Made plots for [`competitor analysis`](./competitorAnalysis.py) using Matplotlib
- Made a [`streamlit app`](./app.py) to display the results in a user friendly format

## Run the Web App

Run the following command on your terminal to view the web app:

```bash
streamlit run app.py
```

## Web App:

### Reviews with highlighted negative and positive comments
![review](./imgs/review.png)

### Comparison Plots With Competitors Reviews
The default is "The Smith - Nomad. You can change it by entering the open table url of the desired restaurant. First the reviews will be scraped till the entered page number and then you can view the comparison graphs.
![plot](./imgs/plot_1.png)

![plot](./imgs/plot_2.png)

### Navigation Bar
![navigation](./imgs/navigation.png)

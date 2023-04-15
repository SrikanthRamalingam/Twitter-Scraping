import snscrape.modules.twitter as sntwitter
import pandas as pd
import streamlit as st
import base64
from pymongo import MongoClient

# connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['twitter']
collection = db['tweets']

def download_csv(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV</a>'
    return href

def download_json(df, filename):
    json = df.to_json(orient='records')
    b64 = base64.b64encode(json.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}.json">Download JSON</a>'
    return href

def scrape_tweets(keyword, start_date, end_date, limit):
    tweets_list = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'{keyword} since:{start_date} until:{end_date}').get_items()):
        if i > limit:
            break
        tweets_list.append({'date': tweet.date, 'id': tweet.id, 'url': tweet.url, 'content': tweet.content, 'user': tweet.user.username, 'reply_count': tweet.replyCount, 'retweet_count': tweet.retweetCount, 'language': tweet.lang, 'source': tweet.source, 'like_count': tweet.likeCount})
        # save to MongoDB
        collection.insert_one({'date': tweet.date, 'id': tweet.id, 'url': tweet.url, 'content': tweet.content, 'user': tweet.user.username, 'reply_count': tweet.replyCount, 'retweet_count': tweet.retweetCount, 'language': tweet.lang, 'source': tweet.source, 'like_count': tweet.likeCount})
    return pd.DataFrame(tweets_list)

def app():
    st.title("Twitter Data Analysis")
    keyword = st.text_input("Enter a keyword or hashtag")
    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")
    limit = st.number_input("Limit", min_value=1, max_value=1000, value=100)
    if st.button("Scrape"):
        df = scrape_tweets(keyword, start_date, end_date, limit)
        st.write(df)
        st.markdown(download_csv(df, f"{keyword}_tweets"), unsafe_allow_html=True)
        st.markdown(download_json(df, f"{keyword}_tweets"), unsafe_allow_html=True)
    if st.button("View Saved Data"):
        data = pd.DataFrame(list(collection.find()))
        st.write(data)

if __name__ == "__main__":
    app()


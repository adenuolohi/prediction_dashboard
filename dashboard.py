import streamlit as st
import pandas as pd
import feedparser
from datetime import datetime, timedelta

# -----------------------
# RSS feeds for crypto & meme coin news
# -----------------------
RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://cryptoslate.com/feed/",
    "https://news.google.com/rss/search?q=meme+coin&hl=en-US&gl=US&ceid=US:en"
]

# -----------------------
# Function: Fetch crypto news (last 7 days)
# -----------------------
def fetch_crypto_news(limit_per_feed=10, days=7):
    news = []
    cutoff = datetime.now() - timedelta(days=days)

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit_per_feed]:
            try:
                published = datetime(*entry.published_parsed[:6])
            except:
                published = datetime.now()
            
            if published < cutoff:
                continue
            
            news.append({
                "Title": entry.title,
                "Published": published.strftime("%Y-%m-%d %H:%M"),
                "Link": entry.link
            })
    return pd.DataFrame(news)

# -----------------------
# Function: Dummy crypto/meme coin market opportunities
# -----------------------
def fetch_markets():
    # Replace with live API later if available
    markets = [
        {"Market":"Bitcoin > $100k", "Market Probability":0.33, "URL":"https://coinmarketcap.com"},
        {"Market":"Shiba Inu next 30 days pump", "Market Probability":0.42, "URL":"https://coingecko.com"},
        {"Market":"Dogecoin > $0.10", "Market Probability":0.55, "URL":"https://coinmarketcap.com"},
        {"Market":"Ethereum > $5000", "Market Probability":0.47, "URL":"https://coingecko.com"},
        {"Market":"Meme coin new trending token", "Market Probability":0.38, "URL":"https://coinmarketcap.com"}
    ]
    return pd.DataFrame(markets)

# -----------------------
# Function: Generate simple BUY/SELL/HOLD signals
# -----------------------
def generate_signal(prob):
    if prob >= 0.6:
        return "BUY"
    elif prob <= 0.4:
        return "SELL"
    else:
        return "HOLD"

# -----------------------
# Streamlit Dashboard
# -----------------------
st.set_page_config(page_title="Crypto & Meme Coin Dashboard", layout="wide")
st.title("📈 Crypto & Meme Coin Opportunity Dashboard")

# Auto-refresh every 5 minutes
st.experimental_singleton.clear()
st_autorefresh = st.experimental_rerun if st.button("Refresh Now") else None

# -----------------------
# Market Opportunities
# -----------------------
with st.spinner("Fetching crypto/meme coin markets..."):
    markets_df = fetch_markets()
    markets_df["Signal"] = markets_df["Market Probability"].apply(generate_signal)

st.subheader("🔥 Market Opportunities")
st.dataframe(markets_df)

# -----------------------
# Recent Crypto News
# -----------------------
with st.spinner("Fetching crypto & meme coin news..."):
    news_df = fetch_crypto_news(limit_per_feed=10, days=7)

st.subheader("📰 Recent Crypto & Meme Coin News")
for idx, row in news_df.iterrows():
    st.markdown(f"- [{row['Title']}]({row['Link']}) — {row['Published']}")

# -----------------------
# Footer
# -----------------------
st.write("Dashboard auto-refreshes every 5 minutes. Stay updated on crypto and meme coin trends!")

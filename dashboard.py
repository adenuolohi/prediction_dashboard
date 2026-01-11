# ================================
# Prediction Market Dashboard
# Phase 2–4 + Dashboard
# ================================

import requests
import pandas as pd
import feedparser
import streamlit as st

# -------------------------------
# 1. FETCH MARKET DATA (Phase 2)
# -------------------------------
def fetch_markets(limit=10):
    # Dummy data for testing / cloud deployment
    markets = [
        {"Market":"US Election 2024", "Market Probability":0.52, "URL":"https://example.com"},
        {"Market":"Bitcoin > $100k", "Market Probability":0.33, "URL":"https://example.com"},
        {"Market":"NFL Super Bowl winner", "Market Probability":0.47, "URL":"https://example.com"},
    ]
    return pd.DataFrame(markets)


# -------------------------------
# 2. FETCH NEWS DATA (Phase 3)
# -------------------------------
RSS_FEEDS = [
    "https://www.reuters.com/rssFeed/worldNews",
    "https://news.google.com/rss/search?q=politics+Nigeria"
]

from datetime import datetime, timedelta

def fetch_news(limit_per_feed=10):
    news = []
    one_week_ago = datetime.now() - timedelta(days=7)

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit_per_feed]:
            # Convert published date
            try:
                published = datetime(*entry.published_parsed[:6])
            except:
                published = datetime.now()  # fallback
            if published < one_week_ago:
                continue  # skip old news
            news.append({
                "Title": entry.title,
                "Published": published.strftime("%Y-%m-%d %H:%M"),
                "Link": entry.link
            })

    return pd.DataFrame(news)


# ---------------------------------------
# 3. ESTIMATE PROBABILITY (Phase 4)
# ---------------------------------------
def estimate_probability(news_df):
    base_probability = 0.50
    score = 0

    for title in news_df["Title"]:
        title = title.lower()

        if "election" in title:
            score += 0.10
        if "supreme court" in title:
            score += 0.10
        if "postponed" in title or "delay" in title:
            score -= 0.10
        if "protest" in title:
            score -= 0.05
        if "approval" in title or "agreement" in title:
            score += 0.05

    estimated = base_probability + score
    estimated = max(0, min(1, estimated))  # clamp 0–1
    return round(estimated, 2)


# -------------------------------
# 4. STREAMLIT DASHBOARD (Phase 6)
# -------------------------------
st.set_page_config(page_title="Prediction Market Intelligence", layout="wide")
st.title("🧠 Prediction Market Intelligence Dashboard")

# Fetch data
with st.spinner("Fetching market data..."):
    markets_df = fetch_markets()

with st.spinner("Fetching news..."):
    news_df = fetch_news()

# Apply probability estimation
markets_df["Estimated Probability"] = estimate_probability(news_df)
markets_df["Gap"] = markets_df["Estimated Probability"] - markets_df["Market Probability"]

def classify_opportunity(gap):
    if gap > 0.10:
        return "BUY"
    elif gap < -0.10:
        return "SELL"
    else:
        return "HOLD"

markets_df["Signal"] = markets_df["Gap"].apply(classify_opportunity)

# -------------------------------
# DISPLAY MARKETS
# -------------------------------
st.subheader("📊 Market Opportunities")
st.dataframe(markets_df, use_container_width=True)

# -------------------------------
# DISPLAY ALERTS
# -------------------------------
st.subheader("⚠️ Alerts")

alerts = markets_df[markets_df["Signal"] != "HOLD"]

if alerts.empty:
    st.success("No strong opportunities right now.")
else:
    for _, row in alerts.iterrows():
        st.warning(
            f"{row['Market']} → {row['Signal']} | "
            f"Market: {row['Market Probability']} | "
            f"Estimated: {row['Estimated Probability']} | "
            f"Gap: {round(row['Gap'], 2)}"
        )

# -------------------------------
# DISPLAY NEWS
# -------------------------------
st.subheader("📰 Latest News Signals")

for _, row in news_df.iterrows():
    st.markdown(f"- [{row['Title']}]({row['Link']}) ({row['Published']})")

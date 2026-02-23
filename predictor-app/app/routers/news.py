import os
import requests
from fastapi import HTTPException
from datetime import date, timedelta

# API key from configuration
from app.settings import settings

FINNHUB_API_KEY = settings.finnhub_api_key

BASE_URL = "https://finnhub.io/api/v1/company-news"

positive_keywords = ['gain', 'growth', 'up', 'profit', 'surge', 'winner']
negative_keywords = ['loss', 'down', 'drop', 'decline', 'risk', 'disappointing']

def analyze_sentiment(headline: str) -> str:
    lower = headline.lower()
    positives = [kw for kw in positive_keywords if kw in lower]
    negatives = [kw for kw in negative_keywords if kw in lower]

    if len(positives) > len(negatives):
        return "Positive"
    elif len(negatives) > len(positives):
        return "Negative"
    return "Neutral"

def get_company_news(symbol: str):
    today = date.today()
    week_ago = today - timedelta(days=7)

    params = {
        "symbol": symbol,
        "from": str(week_ago),
        "to": str(today),
        "token": FINNHUB_API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        news_data = response.json()

        # Attach sentiment and return top 10
        results = []
        for item in news_data[:10]:
            results.append({
                "headline": item.get("headline"),
                "url": item.get("url"),
                "datetime": item.get("datetime"),
                "sentiment": analyze_sentiment(item.get("headline", ""))
            })

        return results

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"News API error: {str(e)}")

# tools/news_api.py

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_news(country: str = "in", page_size: int = 5) -> dict:
    start_time = time.time()

    try:
        if not NEWS_API_KEY:
            raise ValueError("NEWS_API_KEY not found in .env")

        url = "https://newsapi.org/v2/everything"

        params = {
            "q": "India",
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": page_size,
            "apiKey": NEWS_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        articles = [
            {
                "title": article["title"],
                "source": article["source"]["name"],
                "published_at": article["publishedAt"]
            }
            for article in data.get("articles", [])
        ]

        execution_time = round(time.time() - start_time, 4)

        return {
            "status": "success",
            "data": articles,
            "error": None,
            "execution_time": execution_time
        }

    except Exception as e:
        execution_time = round(time.time() - start_time, 4)

        return {
            "status": "error",
            "data": None,
            "error": str(e),
            "execution_time": execution_time
        }
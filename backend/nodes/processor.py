import os
import time
from typing import List
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from utils.trend_analyzer import detect_trends
from langchain_core.messages import HumanMessage
from utils.snapshot_reader import get_yesterday_snapshot

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

SEVERE_KEYWORDS = [
    "storm",
    "heavy rain",
    "heatwave",
    "flood",
    "cyclone",
    "extreme",
]


def calculate_percentage_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 2)


def detect_severe_weather(description: str) -> List[str]:
    alerts = []
    desc_lower = description.lower()

    for keyword in SEVERE_KEYWORDS:
        if keyword in desc_lower:
            alerts.append(f"Severe weather alert: {keyword}")

    return alerts


async def summarize_headlines(headlines: List[str]) -> str:
    """
    V2: LLM-powered news summarization using Groq.
    Summarizes top headlines into 5–6 sentences.
    """

    if not headlines:
        return "No major news headlines available."

    joined = "\n".join(headlines[:5])

    prompt = f"""
    Summarize the following news headlines into a concise 5-6 sentence news briefing.

    Headlines:
    {joined}
    """

    try:
        response = await llm.ainvoke([
            HumanMessage(content=prompt)
        ])
        return response.content.strip()

    except Exception as e:
        print(f"LLM summarization failed: {e}")

        # fallback summary
        return "Top headlines today:\n" + "\n".join(headlines[:5])

    response = await llm.ainvoke([
        HumanMessage(content=prompt)
    ])

    return response.content.strip()


async def processor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("Processor executing...")

    start_time = time.time()   # ✅ start timer

    updates = {}

    # -------------------------
    # 📈 Market Comparison
    # -------------------------
    market_data = state.get("market", {}).get("data", {})

    comparison = {}
    alerts = []

    for index_name in ["nifty", "sensex"]:
        index = market_data.get(index_name)
        if index:
            change_pct = calculate_percentage_change(
                index.get("current", 0),
                index.get("previous_close", 0),
            )

            comparison[index_name] = {
                "current": index.get("current"),
                "previous_close": index.get("previous_close"),
                "change_pct": change_pct,
            }

            if abs(change_pct) >= 2:
                alerts.append(f"{index_name.upper()} moved {change_pct}%")

    updates["comparison"] = comparison


    # -------------------------
    # 📅 Yesterday Comparison
    # -------------------------
    yesterday = get_yesterday_snapshot()

    comparison_text = None

    if yesterday:
        yesterday_weather = yesterday.get("weather", {})
        yesterday_market = yesterday.get("market", {})

        today_temp = weather_desc = (
            state.get("weather", {})
            .get("data", {})
            .get("temperature_c")
        )

        yesterday_temp = yesterday_weather.get("temperature_c")

        if today_temp and yesterday_temp:
            diff = round(today_temp - yesterday_temp, 2)

            if diff > 0:
                comparison_text = f"Temperature increased by {diff}°C compared to yesterday."
            elif diff < 0:
                comparison_text = f"Temperature decreased by {abs(diff)}°C compared to yesterday."
            else:
                comparison_text = "Temperature remained unchanged from yesterday."


    # -------------------------
    # 🌦 Weather Alerts
    # -------------------------
    weather_desc = (
        state.get("weather", {})
        .get("data", {})
        .get("condition", "")
    )

    weather_alerts = detect_severe_weather(weather_desc)
    alerts.extend(weather_alerts)

    # -------------------------
    # 📰 News Summary
    # -------------------------
    news_articles = state.get("news", {}).get("data", [])
    headlines = [article.get("title", "") for article in news_articles[:5]]

    summary = await summarize_headlines(headlines)

    # -------------------------
    # 📊 Trend Detection
    # -------------------------
    trends = detect_trends()

    updates["trends"] = trends
    
    updates["summary"] = summary
    updates["alerts"] = alerts
    updates["yesterday_comparison"] = comparison_text

    # ✅ calculate execution time
    execution_time = round(time.time() - start_time, 4)

    # ✅ add to updates so state receives it
    updates["processor_time"] = execution_time

    return updates
# tools/weather_api.py

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def fetch_weather(city: str = "Warangal") -> dict:
    start_time = time.time()

    try:
        if not WEATHER_API_KEY:
            raise ValueError("WEATHER_API_KEY not found in .env")

        url = "http://api.weatherapi.com/v1/current.json"

        params = {
            "key": WEATHER_API_KEY,
            "q": city,
            "aqi": "no"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if "error" in data:
            raise ValueError(data["error"].get("message"))

        current = data.get("current", {})
        location = data.get("location", {})

        execution_time = round(time.time() - start_time, 4)

        return {
            "status": "success",
            "data": {
                "location": location.get("name"),
                "region": location.get("region"),
                "country": location.get("country"),
                "temperature_c": current.get("temp_c"),
                "condition": current.get("condition", {}).get("text"),
                "humidity": current.get("humidity"),
                "wind_kph": current.get("wind_kph"),
                "last_updated": current.get("last_updated")
            },
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
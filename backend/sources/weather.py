"""WeatherAPI fetcher."""

import os

import httpx

from sources.types import SourceItem, SourceResult


async def fetch_weather(location: str = "Mumbai") -> SourceResult:
    """Fetch current weather for a location."""
    api_key = os.environ.get("WEATHER_API_KEY", "")
    if not api_key:
        return SourceResult(source_name="weatherapi", error="WEATHER_API_KEY not set")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.weatherapi.com/v1/forecast.json",
            params={"key": api_key, "q": location, "days": 1, "aqi": "no"},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

    current = data["current"]
    forecast = data["forecast"]["forecastday"][0]["day"]
    loc = data["location"]

    summary = (
        f"{current['temp_c']}°C, {current['condition']['text']}. "
        f"High {forecast['maxtemp_c']}°C / Low {forecast['mintemp_c']}°C. "
        f"Humidity {current['humidity']}%, Wind {current['wind_kph']} kph. "
        f"Rain chance: {forecast['daily_chance_of_rain']}%"
    )

    item = SourceItem(
        title=f"Weather in {loc['name']}, {loc['country']}",
        summary=summary,
        url=f"https://www.weatherapi.com/",
        source="weatherapi",
        raw=data,
    )
    return SourceResult(source_name="weatherapi", items=(item,))

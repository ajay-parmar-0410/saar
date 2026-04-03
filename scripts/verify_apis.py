"""Verify all external API keys are configured and reachable."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

import httpx

CHECKS: list[tuple[str, str, str]] = [
    ("WeatherAPI", "WEATHER_API_KEY", "https://api.weatherapi.com/v1/current.json?q=Mumbai&key={key}"),
    ("NewsAPI", "NEWS_API_KEY", "https://newsapi.org/v2/top-headlines?country=in&pageSize=1&apiKey={key}"),
    ("Groq", "GROQ_API_KEY", "https://api.groq.com/openai/v1/models"),
    ("Tavily", "TAVILY_API_KEY", "https://api.tavily.com/search"),
]

OPTIONAL: list[tuple[str, str]] = [
    ("Supabase", "SUPABASE_URL"),
    ("Reddit", "REDDIT_CLIENT_ID"),
    ("GitHub Token", "GITHUB_TOKEN"),
]


def check_api(name: str, env_var: str, url: str) -> bool:
    key = os.getenv(env_var, "")
    if not key:
        print(f"  {name}: FAIL (env var {env_var} not set)")
        return False

    try:
        if name == "Groq":
            resp = httpx.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=10)
        elif name == "Tavily":
            resp = httpx.post(url, json={"query": "test", "api_key": key}, timeout=10)
        else:
            resp = httpx.get(url.format(key=key), timeout=10)

        if resp.status_code == 200:
            print(f"  {name}: OK")
            return True
        else:
            print(f"  {name}: FAIL (HTTP {resp.status_code})")
            return False
    except Exception as e:
        print(f"  {name}: FAIL ({e})")
        return False


def check_optional(name: str, env_var: str) -> None:
    key = os.getenv(env_var, "")
    if key:
        print(f"  {name}: OK (configured)")
    else:
        print(f"  {name}: SKIP (not configured yet - optional for now)")


def main() -> None:
    print("\n=== Saar API Verification ===\n")

    print("Required APIs:")
    results = [check_api(name, env_var, url) for name, env_var, url in CHECKS]

    print("\nOptional APIs:")
    for name, env_var in OPTIONAL:
        check_optional(name, env_var)

    passed = sum(results)
    total = len(results)
    print(f"\n--- {passed}/{total} required APIs verified ---\n")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()

import os
import time
from datetime import datetime
from typing import Dict, Any


async def reporter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("Reporter executing...")
    start_time = time.time()
    today = datetime.now().strftime("%Y-%m-%d")

    weather = state.get("weather", {}).get("data", {})
    comparison = state.get("comparison", {})
    summary = state.get("summary", "")
    alerts = state.get("alerts", [])
    trends = state.get("trends", [])
    yesterday_comparison = state.get("yesterday_comparison")

    # -------------------------
    # 📄 Generate Markdown
    # -------------------------
    markdown = f"# Daily Briefing – {today}\n\n"

    # Weather Section
    markdown += "## 🌤 Weather\n"
    if weather:
        markdown += (
            f"- Location: {weather.get('location')}, {weather.get('region')}\n"
            f"- Temperature: {weather.get('temperature_c')}°C\n"
            f"- Condition: {weather.get('condition')}\n"
            f"- Humidity: {weather.get('humidity')}%\n"
            f"- Wind: {weather.get('wind_kph')} kph\n\n"
        )
    else:
        markdown += "No weather data available.\n\n"

    # Market Section
    markdown += "## 📈 Markets\n"
    if comparison:
        for name, data in comparison.items():
            markdown += (
                f"- {name.upper()}:\n"
                f"  - Current: {data.get('current')}\n"
                f"  - Previous Close: {data.get('previous_close')}\n"
                f"  - Change: {data.get('change_pct')}%\n\n"
            )
    else:
        markdown += "No market data available.\n\n"


    markdown += "## 📅 Yesterday Comparison\n"

    if yesterday_comparison:
        markdown += yesterday_comparison + "\n\n"
    else:
        markdown += "No historical comparison available.\n\n"
    

    markdown += "## 📊 Trends\n"

    if trends:
        for t in trends:
            markdown += f"- {t}\n"
    else:
        markdown += "No significant trends detected.\n"

    markdown += "\n"



    # News Summary
    markdown += "## 📰 News Summary\n"
    markdown += summary + "\n\n"

    # Alerts
    markdown += "## 🚨 Alerts\n"
    if alerts:
        for alert in alerts:
            markdown += f"- {alert}\n"
    else:
        markdown += "No critical alerts today.\n"

    # -------------------------
    # 💾 Save File
    # -------------------------
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    file_path = os.path.join(reports_dir, f"{today}.md")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    reporter_time = round(time.time() - start_time, 4)
    return {"report_path": file_path,
            "reporter_time": reporter_time}
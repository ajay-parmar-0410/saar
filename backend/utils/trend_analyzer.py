import json
import os

SNAPSHOT_FILE = "data/daily_snapshots.json"


def detect_trends():
    if not os.path.exists(SNAPSHOT_FILE):
        return []

    try:
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if len(data) < 3:
            return []

        last_three = data[-3:]

        trends = []

        # -------------------------
        # 📈 NIFTY Trend
        # -------------------------
        nifty_values = []

        for entry in last_three:
            market = entry.get("market", {})
            nifty = market.get("nifty", {}).get("current")
            if nifty is not None:
                nifty_values.append(nifty)

        if len(nifty_values) == 3:
            if nifty_values[0] < nifty_values[1] < nifty_values[2]:
                trends.append("📈 NIFTY rising for 3 consecutive days")

            elif nifty_values[0] > nifty_values[1] > nifty_values[2]:
                trends.append("📉 NIFTY declining for 3 consecutive days")

        # -------------------------
        # 🌡 Temperature Trend
        # -------------------------
        temps = []

        for entry in last_three:
            weather = entry.get("weather", {})
            temp = weather.get("temperature_c")
            if temp is not None:
                temps.append(temp)

        if len(temps) == 3:
            if temps[0] < temps[1] < temps[2]:
                trends.append("🌡 Temperature rising trend over last 3 days")

            elif temps[0] > temps[1] > temps[2]:
                trends.append("❄ Temperature falling trend over last 3 days")

        return trends

    except Exception:
        return []
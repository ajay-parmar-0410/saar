import os
import json
from datetime import datetime
from typing import Dict, Any


SNAPSHOT_FILE = "data/daily_snapshots.json"


async def action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("Action node executing...")

    os.makedirs("data", exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")

    snapshot = {
        "date": today,
        "weather": state.get("weather", {}).get("data", {}),
        "market": state.get("comparison", {}),
        "alerts": state.get("alerts", []),
    }

    # -------------------------
    # 📦 Load existing snapshots
    # -------------------------
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    # -------------------------
    # 🔄 Replace today's snapshot
    # -------------------------
    data = [entry for entry in data if entry.get("date") != today]

    data.append(snapshot)

    # -------------------------
    # 💾 Save file
    # -------------------------
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # -------------------------
    # 🚨 Print Alerts
    # -------------------------
    alerts = state.get("alerts", [])

    if alerts:
        print("\n⚠ ALERTS DETECTED:")
        for alert in alerts:
            print(f"- {alert}")
    else:
        print("\nNo critical alerts today.")

    return {}
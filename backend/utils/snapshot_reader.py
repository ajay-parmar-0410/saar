import json
import os

SNAPSHOT_FILE = "data/daily_snapshots.json"


def get_yesterday_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return None

    try:
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list) or len(data) < 2:
            return None

        # second last entry = yesterday
        return data[-2]

    except Exception:
        return None
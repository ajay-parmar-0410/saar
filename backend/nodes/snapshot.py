import json
import os
from datetime import datetime


SNAPSHOT_FILE = "data/daily_snapshots.json"


def append_snapshot(data: dict):
    snapshot_entry = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

    try:
        # If file doesn't exist → create it
        if not os.path.exists(SNAPSHOT_FILE):
            with open(SNAPSHOT_FILE, "w") as f:
                json.dump([], f)

        # Read existing data
        with open(SNAPSHOT_FILE, "r") as f:
            try:
                snapshots = json.load(f)
            except json.JSONDecodeError:
                snapshots = []

        # Append new snapshot
        snapshots.append(snapshot_entry)

        # Write back
        with open(SNAPSHOT_FILE, "w") as f:
            json.dump(snapshots, f, indent=4)

    except Exception as e:
        print(f"Snapshot write failed: {e}")
from nodes.snapshot import append_snapshot

sample_data = {
    "weather": {"temp": 36},
    "market": {"nifty": 24800},
    "news_count": 5
}

append_snapshot(sample_data)

print("Snapshot written successfully")
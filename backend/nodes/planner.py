from graph.state import PLOSState
import time
async def planner_node(state: PLOSState) -> PLOSState:
    print("Planner node executing...")
    start = time.time()
    plan = {
        "tasks": [
            "fetch_weather",
            "fetch_news",
            "fetch_market",
            "fetch_currency"
        ]
    }
    planner_time = round(time.time() - start, 4)
    return {
        "plan": plan,
        "planner_time": planner_time
    }
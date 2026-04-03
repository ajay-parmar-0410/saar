from tools.retry import retry_tool
from tools.weather_api import fetch_weather
from graph.state import PLOSState


async def fetch_weather_node(state: PLOSState) -> PLOSState:
    result = retry_tool(fetch_weather)

    return {
        "weather": result,
        "logs": state.get("logs", []) + ["weather"]
    }
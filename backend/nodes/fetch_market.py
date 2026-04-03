from tools.retry import retry_tool
from tools.finance_api import fetch_market_data
from graph.state import PLOSState


async def fetch_market_node(state: PLOSState) -> PLOSState:
    result = retry_tool(fetch_market_data)

    return {
        "market": result,
        "logs": state.get("logs", []) + ["market"]
    }
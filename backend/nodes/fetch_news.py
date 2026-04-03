from tools.retry import retry_tool
from tools.news_api import fetch_news
from graph.state import PLOSState


async def fetch_news_node(state: PLOSState) -> PLOSState:
    result = retry_tool(fetch_news)

    return {
        "news": result,
        "logs": state.get("logs", []) + ["news"]
    }
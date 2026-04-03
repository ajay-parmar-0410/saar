from langgraph.graph import StateGraph, END
from graph.state import PLOSState
from nodes.planner import planner_node
from nodes.fetch_weather import fetch_weather_node
from nodes.fetch_news import fetch_news_node
from nodes.fetch_market import fetch_market_node
from nodes.processor import processor_node
from nodes.reporter import reporter_node
from nodes.action import action_node
from nodes.logger import logger_node

def build_graph():
    builder = StateGraph(PLOSState)

    builder.add_node("planner", planner_node)
    builder.add_node("fetch_weather", fetch_weather_node)
    builder.add_node("fetch_news", fetch_news_node)
    builder.add_node("fetch_market", fetch_market_node)
    builder.add_node("processor", processor_node)
    builder.add_node("reporter", reporter_node)
    builder.add_node("action", action_node)
    builder.add_node("logger", logger_node)

    builder.set_entry_point("planner")

    # Parallel branches
    builder.add_edge("planner", "fetch_weather")
    builder.add_edge("planner", "fetch_news")
    builder.add_edge("planner", "fetch_market")

    # All converge to END
    builder.add_edge(
    ["fetch_weather", "fetch_news", "fetch_market"],
    "processor"
)

    builder.add_edge("processor", "reporter")
    builder.add_edge("reporter", "action")
    builder.add_edge("action", "logger")
    builder.add_edge("logger", END)

    return builder.compile()
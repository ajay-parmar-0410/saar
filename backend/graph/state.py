from typing import TypedDict, Dict, Any, List, Annotated
import operator


class PLOSState(TypedDict, total=False):
    command: str
    plan: Dict[str, Any]

    # Tools outputs
    weather: dict
    news: dict
    market: dict

    # Processor outputs
    summary: str
    comparison: Dict[str, Any]
    alerts: List[str]
    report_path: str
    yesterday_comparison:str
    trends: List[str]

    # Logging
    logs: Annotated[List[str], operator.add]

    # Node execution times (V2 observability)
    planner_time: float
    processor_time: float
    reporter_time: float
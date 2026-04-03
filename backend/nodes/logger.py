import os
from datetime import datetime
from typing import Dict, Any

LOG_FILE = "logs/execution.log"


async def logger_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("Logger executing...")

    timestamp = datetime.now().isoformat()

    tools_called = state.get("logs", [])
    failures = []

    # -------------------------
    # Tool Execution Times
    # -------------------------
    tool_times = {}
    total_tool_runtime = 0.0

    for tool_name in ["weather", "news", "market"]:
        tool_data = state.get(tool_name)

        if tool_data:
            exec_time = tool_data.get("execution_time", 0.0)
            tool_times[tool_name] = exec_time
            total_tool_runtime += exec_time

            if tool_data.get("status") == "error":
                failures.append(tool_name)

    tool_time_log = "\n".join(
        [f"{tool}: {time:.4f}s" for tool, time in tool_times.items()]
    )

    # -------------------------
    # Node Execution Times
    # -------------------------
    node_times = {
        "planner": state.get("planner_time"),
        "processor": state.get("processor_time"),
        "reporter": state.get("reporter_time"),
    }

    pipeline_runtime = (
    (state.get("planner_time") or 0) +
    (state.get("processor_time") or 0) +
    (state.get("reporter_time") or 0)
    )

    node_time_log = "\n".join(
        [f"{node}: {time:.4f}s" for node, time in node_times.items() if time is not None]
    )

    # -------------------------
    # Log Entry
    # -------------------------
    log_entry = (
    f"\n--- Execution Log ---\n"
    f"Timestamp: {timestamp}\n"
    f"Tools Called: {tools_called}\n\n"
    f"Node Execution Times:\n{node_time_log}\n\n"
    f"Tool Execution Times:\n{tool_time_log}\n\n"
    f"Failures: {failures}\n"
    f"Total Tool Runtime: {total_tool_runtime:.4f} seconds\n"
    f"Total Pipeline Runtime: {pipeline_runtime:.4f} seconds\n"
    f"----------------------\n"
    )

    os.makedirs("logs", exist_ok=True)

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Logging failed: {e}")

    return {}
from nodes.logger import log_execution

log_execution(
    tools_called=["weather", "news", "finance"],
    failures=[],
    total_runtime=2.34
)

print("Log written successfully")
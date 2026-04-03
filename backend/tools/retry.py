# tools/retry.py

import time


def retry_tool(tool_func, retries=3, delay=1, backoff=2, **kwargs):
    attempt = 0

    while attempt < retries:
        result = tool_func(**kwargs)

        if result.get("status") == "success":
            return result

        attempt += 1
        time.sleep(delay * (backoff ** attempt))

    return result  # return last failed result
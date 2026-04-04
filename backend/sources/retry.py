"""Retry wrapper with exponential backoff for source fetchers."""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import TypeVar

from sources.types import SourceResult

logger = logging.getLogger(__name__)

T = TypeVar("T")

MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds
TIMEOUT = 5.0  # seconds per source


async def with_retry(
    fn: Callable[..., Coroutine[None, None, SourceResult]],
    *args: object,
    max_retries: int = MAX_RETRIES,
    base_delay: float = BASE_DELAY,
    timeout: float = TIMEOUT,
    source_name: str = "unknown",
) -> SourceResult:
    """Execute an async source fetcher with retry and timeout.

    - Retries up to max_retries times with exponential backoff (1s, 2s, 4s)
    - Times out after `timeout` seconds per attempt
    - On total failure, returns empty SourceResult with error message
    """
    last_error = ""

    for attempt in range(max_retries + 1):
        try:
            result = await asyncio.wait_for(fn(*args), timeout=timeout)
            return result
        except asyncio.TimeoutError:
            last_error = f"Timeout after {timeout}s"
            logger.warning(
                "%s: attempt %d/%d timed out",
                source_name, attempt + 1, max_retries + 1,
            )
        except Exception as e:
            last_error = str(e)
            logger.warning(
                "%s: attempt %d/%d failed: %s",
                source_name, attempt + 1, max_retries + 1, e,
            )

        if attempt < max_retries:
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)

    logger.error("%s: all %d attempts failed: %s", source_name, max_retries + 1, last_error)
    return SourceResult(source_name=source_name, error=last_error)

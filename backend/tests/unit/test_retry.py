"""Tests for the retry wrapper."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sources.retry import with_retry
from sources.types import SourceResult


@pytest.mark.asyncio
async def test_successful_fetch():
    """Successful call should return result without retrying."""
    call_count = 0

    async def mock_fetch():
        nonlocal call_count
        call_count += 1
        return SourceResult(source_name="test", items=())

    result = await with_retry(mock_fetch, source_name="test", base_delay=0.01)
    assert result.source_name == "test"
    assert result.error is None
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_on_failure():
    """Should retry on exception and succeed on 2nd attempt."""
    call_count = 0

    async def mock_fetch():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("fail")
        return SourceResult(source_name="test", items=())

    result = await with_retry(mock_fetch, source_name="test", base_delay=0.01)
    assert result.error is None
    assert call_count == 2


@pytest.mark.asyncio
async def test_all_retries_fail():
    """Should return error after all retries exhausted."""
    async def mock_fetch():
        raise ConnectionError("always fails")

    result = await with_retry(
        mock_fetch, source_name="test", max_retries=2, base_delay=0.01
    )
    assert result.error is not None
    assert "always fails" in result.error


@pytest.mark.asyncio
async def test_timeout_handling():
    """Should handle timeouts and retry."""
    import asyncio

    async def slow_fetch():
        await asyncio.sleep(10)
        return SourceResult(source_name="test", items=())

    result = await with_retry(
        slow_fetch, source_name="test", max_retries=1, base_delay=0.01, timeout=0.1
    )
    assert result.error is not None
    assert "Timeout" in result.error

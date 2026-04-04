"""Tests for rate limiting middleware."""

import time

import pytest

from middleware.rate_limit import TokenBucket


class TestTokenBucket:
    def test_allows_requests_within_capacity(self):
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        for _ in range(5):
            assert bucket.consume() is True

    def test_rejects_after_capacity_exhausted(self):
        bucket = TokenBucket(capacity=3, refill_rate=0.0)
        for _ in range(3):
            bucket.consume()
        assert bucket.consume() is False

    def test_refills_over_time(self):
        bucket = TokenBucket(capacity=2, refill_rate=100.0)  # Fast refill
        bucket.consume()
        bucket.consume()
        assert bucket.consume() is False
        # Wait for refill
        time.sleep(0.05)
        assert bucket.consume() is True

    def test_does_not_exceed_capacity(self):
        bucket = TokenBucket(capacity=3, refill_rate=100.0)
        time.sleep(0.1)
        # Should not have more than capacity
        count = 0
        while bucket.consume():
            count += 1
        assert count == 3

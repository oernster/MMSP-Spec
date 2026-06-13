"""Tests for MMSP poll semantics (Section 8)."""

from datetime import datetime, timedelta, timezone

import pytest
from tests.validators.poll import (
    POLL_FLOOR_SECONDS,
    PollState,
    build_request_headers,
    can_poll,
    effective_min_interval,
    handle_rate_limit,
    handle_response_headers,
    validate_user_agent,
)


class TestEffectiveMinInterval:
    def test_none_returns_floor(self):
        assert effective_min_interval(None) == POLL_FLOOR_SECONDS

    def test_value_below_floor_returns_floor(self):
        assert effective_min_interval(60) == POLL_FLOOR_SECONDS

    def test_floor_value_returns_floor(self):
        assert effective_min_interval(300) == POLL_FLOOR_SECONDS

    def test_value_above_floor_returned(self):
        assert effective_min_interval(600) == 600

    def test_floor_is_300(self):
        assert POLL_FLOOR_SECONDS == 300


class TestCanPoll:
    def test_first_poll_always_allowed(self):
        state = PollState(feed_url="https://example.com/feed")
        allowed, reason = can_poll(state)
        assert allowed
        assert "no previous poll" in reason

    def test_poll_blocked_within_interval(self):
        now = datetime.now(timezone.utc)
        state = PollState(
            feed_url="https://example.com/feed",
            last_poll_time=now - timedelta(seconds=100),
            min_interval_seconds=300,
        )
        allowed, reason = can_poll(state, now=now)
        assert not allowed
        assert "min interval not elapsed" in reason

    def test_poll_allowed_after_interval(self):
        now = datetime.now(timezone.utc)
        state = PollState(
            feed_url="https://example.com/feed",
            last_poll_time=now - timedelta(seconds=400),
            min_interval_seconds=300,
        )
        allowed, reason = can_poll(state, now=now)
        assert allowed

    def test_poll_blocked_during_back_off(self):
        now = datetime.now(timezone.utc)
        state = PollState(
            feed_url="https://example.com/feed",
            back_off_until=now + timedelta(seconds=600),
        )
        allowed, reason = can_poll(state, now=now)
        assert not allowed
        assert "back-off active" in reason

    def test_poll_allowed_after_back_off(self):
        now = datetime.now(timezone.utc)
        state = PollState(
            feed_url="https://example.com/feed",
            last_poll_time=now - timedelta(seconds=400),
            back_off_until=now - timedelta(seconds=1),
            min_interval_seconds=300,
        )
        allowed, reason = can_poll(state, now=now)
        assert allowed

    def test_exactly_at_interval_boundary(self):
        now = datetime.now(timezone.utc)
        state = PollState(
            feed_url="https://example.com/feed",
            last_poll_time=now - timedelta(seconds=300),
            min_interval_seconds=300,
        )
        allowed, _ = can_poll(state, now=now)
        assert allowed


class TestUpdateFromFeed:
    def test_declared_interval_above_floor_used(self):
        state = PollState(feed_url="https://example.com/feed")
        feed = {"poll": {"min_interval_seconds": 600}}
        state.update_from_feed(feed)
        assert state.min_interval_seconds == 600

    def test_declared_interval_below_floor_clamped(self):
        state = PollState(feed_url="https://example.com/feed")
        feed = {"poll": {"min_interval_seconds": 60}}
        state.update_from_feed(feed)
        assert state.min_interval_seconds == POLL_FLOOR_SECONDS

    def test_no_poll_object_uses_floor(self):
        state = PollState(feed_url="https://example.com/feed")
        state.update_from_feed({})
        assert state.min_interval_seconds == POLL_FLOOR_SECONDS


class TestRequestHeaders:
    def test_user_agent_always_present(self):
        state = PollState(feed_url="https://example.com/feed")
        headers = build_request_headers(state)
        assert headers["User-Agent"] == "MMSP/1.0"

    def test_no_etag_no_conditional_header(self):
        state = PollState(feed_url="https://example.com/feed")
        headers = build_request_headers(state)
        assert "If-None-Match" not in headers

    def test_etag_included_as_conditional_header(self):
        state = PollState(feed_url="https://example.com/feed", etag='"abc123"')
        headers = build_request_headers(state)
        assert headers["If-None-Match"] == '"abc123"'

    def test_last_modified_included(self):
        state = PollState(feed_url="https://example.com/feed", last_modified="Mon, 01 Jun 2026 10:00:00 GMT")
        headers = build_request_headers(state)
        assert headers["If-Modified-Since"] == "Mon, 01 Jun 2026 10:00:00 GMT"

    def test_both_conditional_headers(self):
        state = PollState(
            feed_url="https://example.com/feed",
            etag='"abc"',
            last_modified="Mon, 01 Jun 2026 10:00:00 GMT",
        )
        headers = build_request_headers(state)
        assert "If-None-Match" in headers
        assert "If-Modified-Since" in headers


class TestHandleResponseHeaders:
    def test_etag_stored(self):
        state = PollState(feed_url="https://example.com/feed")
        handle_response_headers(state, {"ETag": '"newetag"'})
        assert state.etag == '"newetag"'

    def test_last_modified_stored(self):
        state = PollState(feed_url="https://example.com/feed")
        handle_response_headers(state, {"Last-Modified": "Mon, 01 Jun 2026 10:00:00 GMT"})
        assert state.last_modified == "Mon, 01 Jun 2026 10:00:00 GMT"

    def test_last_poll_time_updated(self):
        before = datetime.now(timezone.utc)
        state = PollState(feed_url="https://example.com/feed")
        handle_response_headers(state, {})
        assert state.last_poll_time is not None
        assert state.last_poll_time >= before

    def test_lowercase_etag_header(self):
        state = PollState(feed_url="https://example.com/feed")
        handle_response_headers(state, {"etag": '"lower"'})
        assert state.etag == '"lower"'

    def test_empty_headers_no_crash(self):
        state = PollState(feed_url="https://example.com/feed")
        handle_response_headers(state, {})
        assert state.etag is None


class TestRateLimitHandling:
    def test_retry_after_integer_sets_back_off(self):
        now = datetime.now(timezone.utc)
        state = PollState(feed_url="https://example.com/feed", min_interval_seconds=300)
        handle_rate_limit(state, "120", now=now)
        expected = now + timedelta(seconds=120)
        assert abs((state.back_off_until - expected).total_seconds()) < 1

    def test_no_retry_after_uses_doubled_interval(self):
        now = datetime.now(timezone.utc)
        state = PollState(feed_url="https://example.com/feed", min_interval_seconds=300)
        handle_rate_limit(state, None, now=now)
        expected = now + timedelta(seconds=600)
        assert abs((state.back_off_until - expected).total_seconds()) < 1

    def test_invalid_retry_after_uses_doubled_interval(self):
        now = datetime.now(timezone.utc)
        state = PollState(feed_url="https://example.com/feed", min_interval_seconds=300)
        handle_rate_limit(state, "invalid", now=now)
        assert state.back_off_until is not None

    def test_back_off_blocks_subsequent_poll(self):
        now = datetime.now(timezone.utc)
        state = PollState(feed_url="https://example.com/feed", min_interval_seconds=300)
        handle_rate_limit(state, "3600", now=now)
        allowed, reason = can_poll(state, now=now)
        assert not allowed


class TestUserAgentValidation:
    def test_exact_mmsp_token_valid(self):
        ok, _ = validate_user_agent("MMSP/1.0")
        assert ok

    def test_comment_appended_invalid(self):
        # Section 11 permits only a Name/Version product token, not a comment.
        ok, _ = validate_user_agent("MMSP/1.0 (debug-mode)")
        assert not ok

    def test_empty_string_invalid(self):
        ok, msg = validate_user_agent("")
        assert not ok
        assert "missing" in msg.lower()

    def test_wrong_protocol_invalid(self):
        ok, msg = validate_user_agent("MyApp/2.0")
        assert not ok
        assert "MMSP/1.0" in msg

    def test_product_token_appended_valid(self):
        # Section 11: clients SHOULD append a single product token.
        ok, _ = validate_user_agent("MMSP/1.0 Meridian/2.3")
        assert ok

    def test_product_token_superreader_valid(self):
        ok, _ = validate_user_agent("MMSP/1.0 SuperReader/3.0")
        assert ok

    def test_multiple_product_tokens_invalid(self):
        ok, _ = validate_user_agent("MMSP/1.0 Meridian/2.3 Extra/1.0")
        assert not ok

    def test_subscriber_identifying_token_invalid(self):
        # A per-install identifier appended as a third token must be rejected.
        ok, _ = validate_user_agent("MMSP/1.0 Meridian/2.3 user-install-abc123")
        assert not ok

    def test_malformed_product_token_invalid(self):
        # A trailing token without a Name/Version shape is not a product token.
        ok, _ = validate_user_agent("MMSP/1.0 NoSlashHere")
        assert not ok

    def test_version_suffix_invalid(self):
        ok, msg = validate_user_agent("MMSP/1.0-beta")
        assert not ok

    def test_lowercase_invalid(self):
        ok, _ = validate_user_agent("mmsp/1.0")
        assert not ok

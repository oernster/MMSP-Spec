"""Poll semantics enforcement for MMSP clients."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

POLL_FLOOR_SECONDS = 300


@dataclass
class PollState:
    """Tracks per-feed poll state for a client."""
    feed_url: str
    last_poll_time: datetime | None = None
    etag: str | None = None
    last_modified: str | None = None
    back_off_until: datetime | None = None
    min_interval_seconds: int = POLL_FLOOR_SECONDS

    def update_from_feed(self, feed: dict[str, Any]) -> None:
        poll = feed.get("poll", {})
        declared = poll.get("min_interval_seconds", POLL_FLOOR_SECONDS)
        self.min_interval_seconds = max(POLL_FLOOR_SECONDS, declared)


def effective_min_interval(declared: int | None) -> int:
    """Return effective minimum poll interval, enforcing the spec floor."""
    if declared is None:
        return POLL_FLOOR_SECONDS
    return max(POLL_FLOOR_SECONDS, declared)


def can_poll(state: PollState, now: datetime | None = None) -> tuple[bool, str]:
    """
    Determine whether a client may poll the given feed now.

    Returns (allowed: bool, reason: str).
    """
    now = now or datetime.now(timezone.utc)

    if state.back_off_until is not None and now < state.back_off_until:
        return False, f"back-off active until {state.back_off_until.isoformat()}"

    if state.last_poll_time is None:
        return True, "no previous poll"

    elapsed = (now - state.last_poll_time).total_seconds()
    min_interval = state.min_interval_seconds

    if elapsed < min_interval:
        return False, f"min interval not elapsed ({elapsed:.1f}s < {min_interval}s)"

    return True, "interval elapsed"


def build_request_headers(state: PollState) -> dict[str, str]:
    """Build HTTP headers for a poll request per MMSP spec."""
    headers: dict[str, str] = {"User-Agent": "MMSP/1.0"}
    if state.etag:
        headers["If-None-Match"] = state.etag
    if state.last_modified:
        headers["If-Modified-Since"] = state.last_modified
    return headers


def handle_response_headers(state: PollState, response_headers: dict[str, str]) -> None:
    """Update poll state from HTTP response headers."""
    etag = response_headers.get("ETag") or response_headers.get("etag")
    last_modified = response_headers.get("Last-Modified") or response_headers.get("last-modified")
    if etag:
        state.etag = etag
    if last_modified:
        state.last_modified = last_modified
    state.last_poll_time = datetime.now(timezone.utc)


def handle_rate_limit(
    state: PollState,
    retry_after: str | None,
    now: datetime | None = None,
) -> None:
    """Apply back-off after a 429 response per MMSP spec."""
    now = now or datetime.now(timezone.utc)
    if retry_after is not None:
        try:
            delay = int(retry_after)
            from datetime import timedelta
            state.back_off_until = now + timedelta(seconds=delay)
            return
        except ValueError:
            pass
    from datetime import timedelta
    state.back_off_until = now + timedelta(seconds=state.min_interval_seconds * 2)


def validate_user_agent(user_agent: str) -> tuple[bool, str]:
    """
    Validate a User-Agent header value per MMSP spec Section 11.

    MUST be exactly 'MMSP/1.0' or 'MMSP/1.0 (...)' where (...) is a comment.
    MUST NOT contain client software identification outside of a comment.
    """
    if not user_agent:
        return False, "User-Agent header is missing"
    if not user_agent.startswith("MMSP/1.0"):
        return False, f"User-Agent must start with 'MMSP/1.0', got: {user_agent!r}"
    remainder = user_agent[len("MMSP/1.0"):].strip()
    if remainder and not (remainder.startswith("(") and remainder.endswith(")")):
        return False, (
            f"User-Agent may only append a parenthesised comment after 'MMSP/1.0', "
            f"got: {user_agent!r}"
        )
    return True, "valid"

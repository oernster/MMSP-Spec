"""Poll semantics enforcement for MMSP clients."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

POLL_FLOOR_SECONDS = 300

# Section 11: the protocol token identifying this revision of MMSP.
PROTOCOL_TOKEN = "MMSP/1.0"

# A product token is a coarse {name, version} pair such as "Meridian/2.3".
# Section 11 permits at most one of these after the protocol token, and nothing
# else, so the User-Agent cannot carry subscriber-identifying information.
_PRODUCT_TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._+-]*$")


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
    headers: dict[str, str] = {"User-Agent": PROTOCOL_TOKEN}
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

    The first token MUST be the protocol token 'MMSP/1.0'. A client MAY append
    at most one product token identifying the client software and its version,
    for example 'MMSP/1.0 Meridian/2.3'. To preserve subscriber privacy, nothing
    else is permitted: no second product token, no free comment, and no
    operating-system, device, or per-install identifier.
    """
    tokens = user_agent.split()
    if not tokens:
        return False, "User-Agent header is missing"

    if tokens[0] != PROTOCOL_TOKEN:
        return False, (
            f"User-Agent first token must be {PROTOCOL_TOKEN!r}, got: {user_agent!r}"
        )

    if len(tokens) == 1:
        return True, "valid"

    if len(tokens) > 2:
        return False, (
            f"User-Agent may append at most one product token after "
            f"{PROTOCOL_TOKEN!r}, got: {user_agent!r}"
        )

    if not _PRODUCT_TOKEN_RE.match(tokens[1]):
        return False, (
            f"trailing token must be a Name/Version product token, "
            f"got: {tokens[1]!r}"
        )
    return True, "valid"

"""Tests for MMSP pagination rules (Section 5.5)."""

from __future__ import annotations

import pytest
from tests.validators.schema import (
    validate_feed,
    is_valid_feed,
    validate_pagination_consistency,
)


class TestPaginationSchema:
    """Structural schema rules: cursor and has_more are required."""

    def test_valid_pagination_with_next_url(self, minimal_feed: dict) -> None:
        minimal_feed["pagination"] = {"cursor": "tok_abc123", "has_more": True}
        minimal_feed["next_url"] = "https://example.com/.well-known/mmsp.json?before=tok_abc123"
        assert is_valid_feed(minimal_feed)

    def test_valid_pagination_has_more_false(self, minimal_feed: dict) -> None:
        minimal_feed["pagination"] = {"cursor": "tok_abc123", "has_more": False}
        assert is_valid_feed(minimal_feed)

    def test_pagination_cursor_required(self, minimal_feed: dict) -> None:
        minimal_feed["pagination"] = {"has_more": False}
        errors = validate_feed(minimal_feed)
        assert errors

    def test_pagination_has_more_required(self, minimal_feed: dict) -> None:
        minimal_feed["pagination"] = {"cursor": "tok_abc123"}
        errors = validate_feed(minimal_feed)
        assert errors

    def test_next_url_must_be_https(self, minimal_feed: dict) -> None:
        minimal_feed["next_url"] = "http://example.com/.well-known/mmsp.json?before=x"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_next_url_https_accepted(self, minimal_feed: dict) -> None:
        minimal_feed["next_url"] = "https://example.com/.well-known/mmsp.json?before=x"
        assert is_valid_feed(minimal_feed)


class TestPaginationConsistency:
    """Co-constraint: has_more=True requires next_url (Section 5.5.1)."""

    def test_no_pagination_no_errors(self, minimal_feed: dict) -> None:
        errors = validate_pagination_consistency(minimal_feed)
        assert errors == []

    def test_has_more_false_without_next_url_ok(self, minimal_feed: dict) -> None:
        minimal_feed["pagination"] = {"cursor": "x", "has_more": False}
        errors = validate_pagination_consistency(minimal_feed)
        assert errors == []

    def test_has_more_true_with_next_url_ok(self, minimal_feed: dict) -> None:
        minimal_feed["pagination"] = {"cursor": "x", "has_more": True}
        minimal_feed["next_url"] = "https://example.com/.well-known/mmsp.json?before=x"
        errors = validate_pagination_consistency(minimal_feed)
        assert errors == []

    def test_has_more_true_without_next_url_flagged(self, minimal_feed: dict) -> None:
        minimal_feed["pagination"] = {"cursor": "x", "has_more": True}
        errors = validate_pagination_consistency(minimal_feed)
        assert errors
        assert "next_url" in errors[0]

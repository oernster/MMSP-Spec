"""Tests for feed-level error handling rules (Sections 5.6 and 6.15)."""

from __future__ import annotations

import pytest
from tests.validators.schema import (
    is_valid_feed,
    validate_item_tolerant,
)


class TestMixedItemFeed:
    """Section 6.15: valid items are retained even when others are invalid."""

    def test_valid_items_pass_through(self, minimal_item: dict) -> None:
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is not None
        assert warnings == []

    def test_invalid_item_returns_none(self, minimal_item: dict) -> None:
        bad_item = {"type": "article", "title": "No ID or URL or published"}
        result, warnings = validate_item_tolerant(bad_item)
        assert result is None

    def test_mixed_feed_yields_only_valid_items(
        self, minimal_item: dict
    ) -> None:
        bad_item = {"type": "article"}  # missing id, title, url, published
        items = [minimal_item, bad_item]
        valid = [
            result
            for item in items
            for result, _ in [validate_item_tolerant(item)]
            if result is not None
        ]
        assert len(valid) == 1
        assert valid[0]["id"] == minimal_item["id"]


class TestUnknownTopLevelMember:
    """Section 5.6: unknown feed-level members MUST NOT reject the feed."""

    def test_unknown_member_does_not_reject_feed(self, minimal_feed: dict) -> None:
        minimal_feed["x-unknown-extension"] = {"some": "data"}
        assert is_valid_feed(minimal_feed)

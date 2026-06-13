"""Tests for item-level tolerance rules (Section 6.15)."""

from __future__ import annotations

import pytest
from tests.validators.schema import validate_item_tolerant


class TestValidItem:
    def test_valid_item_returned_unchanged(self, minimal_item: dict) -> None:
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is not None
        assert warnings == []
        assert result["type"] == "article"


class TestUnknownTypeDegradation:
    """Section 6.15 / Section 6.3: unknown type degrades to 'article'."""

    def test_unknown_type_becomes_article(self, minimal_item: dict) -> None:
        minimal_item["type"] = "webcomic"
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is not None
        assert result["type"] == "article"
        assert any("webcomic" in w for w in warnings)

    def test_degradation_warning_mentions_section(self, minimal_item: dict) -> None:
        minimal_item["type"] = "podcast"
        _, warnings = validate_item_tolerant(minimal_item)
        assert any("6.15" in w for w in warnings)


class TestMissingRequiredField:
    """Section 6.15: item is skipped (returns None) when a required field is absent."""

    def test_missing_id_returns_none(self, minimal_item: dict) -> None:
        del minimal_item["id"]
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is None
        assert warnings

    def test_missing_title_returns_none(self, minimal_item: dict) -> None:
        del minimal_item["title"]
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is None

    def test_missing_url_returns_none(self, minimal_item: dict) -> None:
        del minimal_item["url"]
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is None

    def test_missing_published_returns_none(self, minimal_item: dict) -> None:
        del minimal_item["published"]
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is None

    def test_missing_type_returns_none(self, minimal_item: dict) -> None:
        del minimal_item["type"]
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is None


class TestMalformedOptionalField:
    """Section 6.15: malformed optional field is stripped; item is not skipped."""

    def test_malformed_duration_stripped(self, minimal_item: dict) -> None:
        minimal_item["duration"] = "not-an-integer"
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is not None
        assert "duration" not in result
        assert any("duration" in w for w in warnings)

    def test_malformed_language_stripped(self, minimal_item: dict) -> None:
        minimal_item["language"] = 12345
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is not None
        assert "language" not in result
        assert any("language" in w for w in warnings)


class TestUnknownOptionalField:
    """Section 6.15: unknown members are preserved (forward-compat)."""

    def test_unknown_field_preserved(self, minimal_item: dict) -> None:
        minimal_item["x-custom"] = "some value"
        result, warnings = validate_item_tolerant(minimal_item)
        assert result is not None
        assert result["x-custom"] == "some value"

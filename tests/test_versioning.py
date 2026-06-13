"""Tests for MMSP protocol versioning rules (Section 5.7)."""

from __future__ import annotations

import pytest
from tests.validators.schema import validate_feed, is_valid_feed


class TestVersionAcceptance:
    """Section 5.7: a 1.x client MUST accept any 1.MINOR version."""

    def test_version_1_0_accepted(self, minimal_feed: dict) -> None:
        minimal_feed["mmsp"] = "1.0"
        assert is_valid_feed(minimal_feed)

    def test_version_1_1_accepted(self, minimal_feed: dict) -> None:
        minimal_feed["mmsp"] = "1.1"
        assert is_valid_feed(minimal_feed)

    def test_version_1_99_accepted(self, minimal_feed: dict) -> None:
        minimal_feed["mmsp"] = "1.99"
        assert is_valid_feed(minimal_feed)


class TestVersionRejection:
    """Non-1.x values MUST be rejected by the schema pattern."""

    def test_version_2_0_rejected(self, minimal_feed: dict) -> None:
        minimal_feed["mmsp"] = "2.0"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_version_0_1_rejected(self, minimal_feed: dict) -> None:
        minimal_feed["mmsp"] = "0.1"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_malformed_version_rejected(self, minimal_feed: dict) -> None:
        minimal_feed["mmsp"] = "not-a-version"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_missing_version_rejected(self, minimal_feed: dict) -> None:
        del minimal_feed["mmsp"]
        errors = validate_feed(minimal_feed)
        assert errors


class TestForwardCompatibility:
    """Section 5.7: unknown top-level members MUST NOT reject a 1.x feed."""

    def test_unknown_top_level_field_accepted(self, minimal_feed: dict) -> None:
        minimal_feed["mmsp"] = "1.1"
        minimal_feed["x-future-field"] = "some value added in 1.1"
        assert is_valid_feed(minimal_feed)

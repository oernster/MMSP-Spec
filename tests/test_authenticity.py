"""Regression tests for signature field reservation (Section 12.5).

Section 12.5 reserves the member name 'signature' at both feed and item
level for a future authenticity mechanism. Per Section 6.15 clients MUST
ignore it where present; the forward-compatible additionalProperties:true on
both schemas ensures it never causes a validation failure.
"""

from __future__ import annotations

import pytest
from tests.validators.schema import is_valid_feed, is_valid_item


class TestFeedSignatureReservation:
    """A feed-level 'signature' field MUST be accepted (ignored) by the schema."""

    def test_feed_with_signature_field_validates(self, minimal_feed: dict) -> None:
        minimal_feed["signature"] = {
            "algorithm": "ecdsa-p256-sha256",
            "value": "base64encodedvalue==",
        }
        assert is_valid_feed(minimal_feed)


class TestItemSignatureReservation:
    """An item-level 'signature' field MUST be accepted (ignored) by the schema."""

    def test_item_with_signature_field_validates(self, minimal_item: dict) -> None:
        minimal_item["signature"] = {
            "algorithm": "ecdsa-p256-sha256",
            "value": "base64encodedvalue==",
        }
        assert is_valid_item(minimal_item)


class TestFeedAndItemSignatureTogether:
    """Both feed and item carrying 'signature' fields MUST validate together."""

    def test_feed_and_item_both_signed_validate(
        self, minimal_feed: dict, minimal_item: dict
    ) -> None:
        minimal_item["signature"] = {"value": "itemsig=="}
        minimal_feed["items"] = [minimal_item]
        minimal_feed["signature"] = {"value": "feedsig=="}
        assert is_valid_feed(minimal_feed)

"""Tests for MMSP feed manifest schema validation (Section 5)."""

import pytest
from tests.validators.schema import validate_feed, is_valid_feed


class TestRequiredFields:
    def test_valid_minimal_feed(self, minimal_feed):
        assert is_valid_feed(minimal_feed)

    def test_valid_full_feed(self, full_feed):
        assert is_valid_feed(full_feed)

    def test_missing_mmsp_version(self, minimal_feed):
        del minimal_feed["mmsp"]
        errors = validate_feed(minimal_feed)
        assert any("mmsp" in e for e in errors)

    def test_wrong_mmsp_version(self, minimal_feed):
        minimal_feed["mmsp"] = "2.0"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_missing_id(self, minimal_feed):
        del minimal_feed["id"]
        errors = validate_feed(minimal_feed)
        assert errors

    def test_missing_title(self, minimal_feed):
        del minimal_feed["title"]
        errors = validate_feed(minimal_feed)
        assert errors

    def test_missing_feed_url(self, minimal_feed):
        del minimal_feed["feed_url"]
        errors = validate_feed(minimal_feed)
        assert errors

    def test_missing_items(self, minimal_feed):
        del minimal_feed["items"]
        errors = validate_feed(minimal_feed)
        assert errors

    def test_empty_items_allowed(self, minimal_feed):
        minimal_feed["items"] = []
        assert is_valid_feed(minimal_feed)

    def test_feed_url_must_be_https(self, minimal_feed):
        minimal_feed["feed_url"] = "http://example.com/.well-known/mmsp.json"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_id_must_be_uri(self, minimal_feed):
        minimal_feed["id"] = "not-a-uri"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_title_must_not_be_empty(self, minimal_feed):
        minimal_feed["title"] = ""
        errors = validate_feed(minimal_feed)
        assert errors


class TestOptionalFields:
    def test_description_accepted(self, minimal_feed):
        minimal_feed["description"] = "A test feed"
        assert is_valid_feed(minimal_feed)

    def test_icon_must_be_https(self, minimal_feed):
        minimal_feed["icon"] = "http://example.com/icon.png"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_icon_https_accepted(self, minimal_feed):
        minimal_feed["icon"] = "https://example.com/icon.png"
        assert is_valid_feed(minimal_feed)

    def test_language_bcp47_accepted(self, minimal_feed):
        minimal_feed["language"] = "en"
        assert is_valid_feed(minimal_feed)

    def test_language_subtag_accepted(self, minimal_feed):
        minimal_feed["language"] = "en-GB"
        assert is_valid_feed(minimal_feed)

    def test_contact_email_accepted(self, minimal_feed):
        minimal_feed["contact"] = "feed@example.com"
        assert is_valid_feed(minimal_feed)

    def test_tags_accepted(self, minimal_feed):
        minimal_feed["tags"] = ["tech", "media"]
        assert is_valid_feed(minimal_feed)

    def test_bundle_id_uri_accepted(self, minimal_feed):
        minimal_feed["bundle_id"] = "https://example.com/bundles/main"
        assert is_valid_feed(minimal_feed)

    def test_moved_to_must_be_https(self, minimal_feed):
        minimal_feed["moved_to"] = "http://new.example.com/.well-known/mmsp.json"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_moved_to_https_accepted(self, minimal_feed):
        minimal_feed["moved_to"] = "https://new.example.com/.well-known/mmsp.json"
        assert is_valid_feed(minimal_feed)

    def test_next_url_must_be_https(self, minimal_feed):
        minimal_feed["next_url"] = "http://example.com/.well-known/mmsp.json?before=x"
        errors = validate_feed(minimal_feed)
        assert errors

    def test_unknown_fields_permitted(self, minimal_feed):
        minimal_feed["x-custom-extension"] = "some value"
        assert is_valid_feed(minimal_feed)


class TestAuthorObject:
    def test_author_with_name_only(self, minimal_feed):
        minimal_feed["authors"] = [{"name": "Test Author"}]
        assert is_valid_feed(minimal_feed)

    def test_author_with_url(self, minimal_feed):
        minimal_feed["authors"] = [{"name": "Test Author", "url": "https://example.com/author"}]
        assert is_valid_feed(minimal_feed)

    def test_author_url_must_be_https(self, minimal_feed):
        minimal_feed["authors"] = [{"name": "Test Author", "url": "http://example.com/author"}]
        errors = validate_feed(minimal_feed)
        assert errors

    def test_author_missing_name(self, minimal_feed):
        minimal_feed["authors"] = [{"url": "https://example.com/author"}]
        errors = validate_feed(minimal_feed)
        assert errors

    def test_author_avatar_must_be_https(self, minimal_feed):
        minimal_feed["authors"] = [{"name": "A", "avatar": "http://example.com/a.jpg"}]
        errors = validate_feed(minimal_feed)
        assert errors


class TestPollObject:
    def test_poll_min_interval_300_accepted(self, minimal_feed):
        minimal_feed["poll"] = {"min_interval_seconds": 300}
        assert is_valid_feed(minimal_feed)

    def test_poll_min_interval_below_300_rejected(self, minimal_feed):
        minimal_feed["poll"] = {"min_interval_seconds": 60}
        errors = validate_feed(minimal_feed)
        assert errors

    def test_poll_recommended_interval_accepted(self, minimal_feed):
        minimal_feed["poll"] = {"recommended_interval_seconds": 3600}
        assert is_valid_feed(minimal_feed)

    def test_poll_ttl_accepted(self, minimal_feed):
        minimal_feed["poll"] = {"ttl_seconds": 86400}
        assert is_valid_feed(minimal_feed)


class TestCapabilities:
    def test_known_capabilities_accepted(self, minimal_feed):
        minimal_feed["capabilities"] = ["conditional-get", "pagination"]
        assert is_valid_feed(minimal_feed)

    def test_unknown_capability_rejected(self, minimal_feed):
        minimal_feed["capabilities"] = ["unknown-capability"]
        errors = validate_feed(minimal_feed)
        assert errors

    def test_filter_metadata_capability_accepted(self, minimal_feed):
        minimal_feed["capabilities"] = ["filter-metadata"]
        assert is_valid_feed(minimal_feed)


class TestPaginationObject:
    def test_valid_pagination(self, minimal_feed):
        minimal_feed["pagination"] = {"cursor": "abc123", "has_more": True}
        assert is_valid_feed(minimal_feed)

    def test_pagination_missing_cursor(self, minimal_feed):
        minimal_feed["pagination"] = {"has_more": False}
        errors = validate_feed(minimal_feed)
        assert errors

    def test_pagination_missing_has_more(self, minimal_feed):
        minimal_feed["pagination"] = {"cursor": "abc"}
        errors = validate_feed(minimal_feed)
        assert errors


class TestDeprecationObject:
    def test_valid_deprecation(self, minimal_feed):
        minimal_feed["deprecated"] = {
            "reason": "Shutting down",
            "sunset_date": "2027-01-01T00:00:00Z",
        }
        assert is_valid_feed(minimal_feed)

    def test_deprecation_reason_only(self, minimal_feed):
        minimal_feed["deprecated"] = {"reason": "Shutting down"}
        assert is_valid_feed(minimal_feed)

    def test_deprecation_empty_object(self, minimal_feed):
        minimal_feed["deprecated"] = {}
        assert is_valid_feed(minimal_feed)

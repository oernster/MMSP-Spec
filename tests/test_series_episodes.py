"""Tests for MMSP series and episode schema (Section 6.9)."""

import pytest
from tests.validators.schema import is_valid_item, validate_item


class TestSeriesField:
    def test_item_with_series_valid(self, minimal_item):
        minimal_item["series"] = {
            "id": "https://example.com/series/tech-talks",
            "title": "Tech Talks",
        }
        assert is_valid_item(minimal_item)

    def test_series_with_episode_number(self, minimal_item):
        minimal_item["series"] = {
            "id": "https://example.com/series/tech-talks",
            "title": "Tech Talks",
            "episode_number": 5,
        }
        assert is_valid_item(minimal_item)

    def test_series_with_season(self, minimal_item):
        minimal_item["series"] = {
            "id": "https://example.com/series/tech-talks",
            "title": "Tech Talks",
            "season_number": 2,
            "episode_number": 3,
        }
        assert is_valid_item(minimal_item)

    def test_series_with_total_episodes(self, minimal_item):
        minimal_item["series"] = {
            "id": "https://example.com/series/tech-talks",
            "title": "Tech Talks",
            "episode_number": 1,
            "season_number": 1,
            "total_episodes": 12,
        }
        assert is_valid_item(minimal_item)

    def test_series_episode_zero_accepted(self, minimal_item):
        minimal_item["series"] = {
            "id": "https://example.com/series/s1",
            "title": "S1",
            "episode_number": 0,
        }
        assert is_valid_item(minimal_item)

    def test_series_missing_id_rejected(self, minimal_item):
        minimal_item["series"] = {"title": "Tech Talks"}
        assert validate_item(minimal_item)

    def test_series_missing_title_rejected(self, minimal_item):
        minimal_item["series"] = {"id": "https://example.com/series/1"}
        assert validate_item(minimal_item)

    def test_series_season_below_one_rejected(self, minimal_item):
        minimal_item["series"] = {
            "id": "https://example.com/series/1",
            "title": "S",
            "season_number": 0,
        }
        assert validate_item(minimal_item)

    def test_series_total_episodes_below_one_rejected(self, minimal_item):
        minimal_item["series"] = {
            "id": "https://example.com/series/1",
            "title": "S",
            "total_episodes": 0,
        }
        assert validate_item(minimal_item)

    def test_series_id_must_be_uri(self, minimal_item):
        minimal_item["series"] = {
            "id": "not-a-uri",
            "title": "Tech Talks",
        }
        assert validate_item(minimal_item)


class TestSeriesAcrossItemTypes:
    @pytest.mark.parametrize("item_type", ["video", "audio", "course", "podcast"])
    def test_series_valid_on_media_types(self, minimal_item, item_type):
        if item_type == "podcast":
            minimal_item["type"] = "audio"
        else:
            minimal_item["type"] = item_type
        minimal_item["series"] = {
            "id": "https://example.com/series/1",
            "title": "My Series",
            "episode_number": 1,
        }
        assert is_valid_item(minimal_item)

    def test_series_on_article_type_valid(self, minimal_item):
        minimal_item["type"] = "article"
        minimal_item["series"] = {
            "id": "https://example.com/series/newsletter-1",
            "title": "Newsletter Series",
        }
        assert is_valid_item(minimal_item)


class TestCanonicalUrl:
    def test_canonical_url_deduplication_field(self, minimal_item):
        minimal_item["canonical_url"] = "https://original.example.com/items/1"
        assert is_valid_item(minimal_item)

    def test_canonical_url_must_be_https(self, minimal_item):
        minimal_item["canonical_url"] = "http://original.example.com/items/1"
        assert validate_item(minimal_item)

    def test_two_items_same_canonical_url(self):
        canonical = "https://original.example.com/videos/1"
        item_a = {
            "id": "https://source-a.example.com/v1",
            "type": "video",
            "title": "Video from Source A",
            "url": "https://source-a.example.com/v1",
            "published": "2026-06-01T00:00:00Z",
            "canonical_url": canonical,
        }
        item_b = {
            "id": "https://source-b.example.com/v1",
            "type": "video",
            "title": "Video from Source B",
            "url": "https://source-b.example.com/v1",
            "published": "2026-06-01T00:00:00Z",
            "canonical_url": canonical,
        }
        from tests.validators.schema import is_valid_item
        assert is_valid_item(item_a)
        assert is_valid_item(item_b)
        assert item_a["canonical_url"] == item_b["canonical_url"]

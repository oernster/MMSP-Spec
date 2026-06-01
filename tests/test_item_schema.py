"""Tests for MMSP item schema validation (Section 6)."""

import pytest
from tests.validators.schema import validate_item, is_valid_item


class TestRequiredFields:
    def test_valid_minimal_item(self, minimal_item):
        assert is_valid_item(minimal_item)

    def test_missing_id(self, minimal_item):
        del minimal_item["id"]
        assert validate_item(minimal_item)

    def test_missing_type(self, minimal_item):
        del minimal_item["type"]
        assert validate_item(minimal_item)

    def test_missing_title(self, minimal_item):
        del minimal_item["title"]
        assert validate_item(minimal_item)

    def test_missing_url(self, minimal_item):
        del minimal_item["url"]
        assert validate_item(minimal_item)

    def test_missing_published(self, minimal_item):
        del minimal_item["published"]
        assert validate_item(minimal_item)

    def test_url_must_be_https(self, minimal_item):
        minimal_item["url"] = "http://example.com/items/1"
        assert validate_item(minimal_item)

    def test_id_must_be_uri(self, minimal_item):
        minimal_item["id"] = "not-a-uri"
        assert validate_item(minimal_item)

    def test_title_must_not_be_empty(self, minimal_item):
        minimal_item["title"] = ""
        assert validate_item(minimal_item)


class TestItemTypes:
    @pytest.mark.parametrize("item_type", [
        "video", "audio", "article", "image", "short",
        "document", "gallery", "event", "release",
        "newsletter", "course", "livestream",
    ])
    def test_valid_item_types(self, minimal_item, item_type):
        minimal_item["type"] = item_type
        assert is_valid_item(minimal_item)

    def test_invalid_type_rejected(self, minimal_item):
        minimal_item["type"] = "webcomic"
        errors = validate_item(minimal_item)
        assert errors


class TestOptionalFields:
    def test_updated_accepted(self, minimal_item):
        minimal_item["updated"] = "2026-06-01T12:00:00Z"
        assert is_valid_item(minimal_item)

    def test_description_accepted(self, minimal_item):
        minimal_item["description"] = "<p>Some content</p>"
        assert is_valid_item(minimal_item)

    def test_tags_accepted(self, minimal_item):
        minimal_item["tags"] = ["tech", "news"]
        assert is_valid_item(minimal_item)

    def test_language_accepted(self, minimal_item):
        minimal_item["language"] = "fr"
        assert is_valid_item(minimal_item)

    def test_duration_accepted(self, minimal_item):
        minimal_item["duration"] = 3600
        assert is_valid_item(minimal_item)

    def test_duration_zero_accepted(self, minimal_item):
        minimal_item["duration"] = 0
        assert is_valid_item(minimal_item)

    def test_duration_negative_rejected(self, minimal_item):
        minimal_item["duration"] = -1
        assert validate_item(minimal_item)

    def test_license_accepted(self, minimal_item):
        minimal_item["license"] = "CC-BY-4.0"
        assert is_valid_item(minimal_item)

    def test_expires_accepted(self, minimal_item):
        minimal_item["expires"] = "2026-12-31T23:59:59Z"
        assert is_valid_item(minimal_item)

    def test_canonical_url_must_be_https(self, minimal_item):
        minimal_item["canonical_url"] = "http://example.com/items/1"
        assert validate_item(minimal_item)

    def test_canonical_url_https_accepted(self, minimal_item):
        minimal_item["canonical_url"] = "https://example.com/items/1"
        assert is_valid_item(minimal_item)

    def test_preview_url_must_be_https(self, minimal_item):
        minimal_item["preview_url"] = "http://cdn.example.com/preview.mp4"
        assert validate_item(minimal_item)

    def test_live_status_values(self, minimal_item):
        for status in ("upcoming", "live", "ended", "archived"):
            minimal_item["type"] = "livestream"
            minimal_item["live_status"] = status
            assert is_valid_item(minimal_item)

    def test_live_status_invalid(self, minimal_item):
        minimal_item["live_status"] = "cancelled"
        assert validate_item(minimal_item)

    def test_scheduled_start_accepted(self, minimal_item):
        minimal_item["type"] = "event"
        minimal_item["scheduled_start"] = "2026-07-01T17:00:00Z"
        assert is_valid_item(minimal_item)

    def test_unknown_fields_permitted(self, minimal_item):
        minimal_item["x-custom-field"] = "value"
        assert is_valid_item(minimal_item)


class TestMediaObject:
    def test_valid_media(self, minimal_item):
        minimal_item["media"] = [{"url": "https://cdn.example.com/v.mp4", "mime_type": "video/mp4"}]
        assert is_valid_item(minimal_item)

    def test_media_url_must_be_https(self, minimal_item):
        minimal_item["media"] = [{"url": "http://cdn.example.com/v.mp4", "mime_type": "video/mp4"}]
        assert validate_item(minimal_item)

    def test_media_missing_url(self, minimal_item):
        minimal_item["media"] = [{"mime_type": "video/mp4"}]
        assert validate_item(minimal_item)

    def test_media_missing_mime_type(self, minimal_item):
        minimal_item["media"] = [{"url": "https://cdn.example.com/v.mp4"}]
        assert validate_item(minimal_item)

    def test_media_role_values(self, minimal_item):
        for role in ("primary", "alternate", "preview"):
            minimal_item["media"] = [{"url": "https://cdn.example.com/v.mp4", "mime_type": "video/mp4", "role": role}]
            assert is_valid_item(minimal_item)

    def test_media_size_bytes_accepted(self, minimal_item):
        minimal_item["media"] = [{"url": "https://cdn.example.com/v.mp4", "mime_type": "video/mp4", "size_bytes": 104857600}]
        assert is_valid_item(minimal_item)

    def test_media_multiple_variants(self, video_item):
        video_item["media"].append({"url": "https://cdn.example.com/v-720p.mp4", "mime_type": "video/mp4", "quality_label": "720p", "role": "alternate"})
        assert is_valid_item(video_item)


class TestThumbnailObject:
    def test_valid_thumbnail(self, minimal_item):
        minimal_item["thumbnail"] = [{"url": "https://cdn.example.com/thumb.jpg"}]
        assert is_valid_item(minimal_item)

    def test_thumbnail_with_dimensions(self, minimal_item):
        minimal_item["thumbnail"] = [{"url": "https://cdn.example.com/thumb.jpg", "width": 1280, "height": 720}]
        assert is_valid_item(minimal_item)

    def test_thumbnail_url_must_be_https(self, minimal_item):
        minimal_item["thumbnail"] = [{"url": "http://cdn.example.com/thumb.jpg"}]
        assert validate_item(minimal_item)

    def test_multiple_thumbnails(self, minimal_item):
        minimal_item["thumbnail"] = [
            {"url": "https://cdn.example.com/thumb-1280.jpg", "width": 1280},
            {"url": "https://cdn.example.com/thumb-640.jpg", "width": 640},
        ]
        assert is_valid_item(minimal_item)


class TestChapterObject:
    def test_valid_chapters(self, minimal_item):
        minimal_item["chapters"] = [
            {"title": "Intro", "start_seconds": 0, "end_seconds": 60},
            {"title": "Main", "start_seconds": 60},
        ]
        assert is_valid_item(minimal_item)

    def test_chapter_missing_title(self, minimal_item):
        minimal_item["chapters"] = [{"start_seconds": 0}]
        assert validate_item(minimal_item)

    def test_chapter_missing_start(self, minimal_item):
        minimal_item["chapters"] = [{"title": "Intro"}]
        assert validate_item(minimal_item)

    def test_chapter_image_url_must_be_https(self, minimal_item):
        minimal_item["chapters"] = [{"title": "Intro", "start_seconds": 0, "image_url": "http://cdn.example.com/ch.jpg"}]
        assert validate_item(minimal_item)


class TestTranscriptObject:
    def test_valid_transcript(self, minimal_item):
        minimal_item["transcript"] = {"url": "https://cdn.example.com/t.txt", "mime_type": "text/plain"}
        assert is_valid_item(minimal_item)

    def test_transcript_with_language(self, minimal_item):
        minimal_item["transcript"] = {"url": "https://cdn.example.com/t.txt", "mime_type": "text/plain", "language": "en"}
        assert is_valid_item(minimal_item)

    def test_transcript_url_must_be_https(self, minimal_item):
        minimal_item["transcript"] = {"url": "http://cdn.example.com/t.txt", "mime_type": "text/plain"}
        assert validate_item(minimal_item)

    def test_transcript_missing_url(self, minimal_item):
        minimal_item["transcript"] = {"mime_type": "text/plain"}
        assert validate_item(minimal_item)


class TestCaptionObject:
    def test_valid_caption(self, minimal_item):
        minimal_item["captions"] = [{"url": "https://cdn.example.com/sub.vtt", "mime_type": "text/vtt", "language": "en"}]
        assert is_valid_item(minimal_item)

    def test_caption_missing_language(self, minimal_item):
        minimal_item["captions"] = [{"url": "https://cdn.example.com/sub.vtt", "mime_type": "text/vtt"}]
        assert validate_item(minimal_item)

    def test_caption_url_must_be_https(self, minimal_item):
        minimal_item["captions"] = [{"url": "http://cdn.example.com/sub.vtt", "mime_type": "text/vtt", "language": "en"}]
        assert validate_item(minimal_item)

    def test_multiple_caption_languages(self, minimal_item):
        minimal_item["captions"] = [
            {"url": "https://cdn.example.com/sub.en.vtt", "mime_type": "text/vtt", "language": "en"},
            {"url": "https://cdn.example.com/sub.fr.vtt", "mime_type": "text/vtt", "language": "fr"},
        ]
        assert is_valid_item(minimal_item)


class TestSeriesObject:
    def test_valid_series(self, minimal_item):
        minimal_item["series"] = {"id": "https://example.com/series/1", "title": "My Series"}
        assert is_valid_item(minimal_item)

    def test_series_with_episode(self, minimal_item):
        minimal_item["series"] = {
            "id": "https://example.com/series/1",
            "title": "My Series",
            "episode_number": 3,
            "season_number": 2,
            "total_episodes": 10,
        }
        assert is_valid_item(minimal_item)

    def test_series_missing_id(self, minimal_item):
        minimal_item["series"] = {"title": "My Series"}
        assert validate_item(minimal_item)

    def test_series_missing_title(self, minimal_item):
        minimal_item["series"] = {"id": "https://example.com/series/1"}
        assert validate_item(minimal_item)


class TestContentRating:
    @pytest.mark.parametrize("rating", ["general", "teen", "mature", "explicit"])
    def test_valid_ratings(self, minimal_item, rating):
        minimal_item["content_rating"] = {"rating": rating}
        assert is_valid_item(minimal_item)

    def test_invalid_rating(self, minimal_item):
        minimal_item["content_rating"] = {"rating": "pg-13"}
        assert validate_item(minimal_item)

    def test_rating_with_descriptors(self, minimal_item):
        minimal_item["content_rating"] = {"rating": "mature", "descriptors": ["violence", "language"]}
        assert is_valid_item(minimal_item)

    def test_spoiler_flag(self, minimal_item):
        minimal_item["content_rating"] = {"rating": "general", "spoiler": True}
        assert is_valid_item(minimal_item)

    def test_content_rating_missing_rating(self, minimal_item):
        minimal_item["content_rating"] = {"descriptors": ["violence"]}
        assert validate_item(minimal_item)


class TestGeoRestriction:
    def test_allowlist(self, minimal_item):
        minimal_item["geo_restriction"] = {"type": "allowlist", "regions": ["GB", "US"]}
        assert is_valid_item(minimal_item)

    def test_blocklist(self, minimal_item):
        minimal_item["geo_restriction"] = {"type": "blocklist", "regions": ["CN"]}
        assert is_valid_item(minimal_item)

    def test_invalid_type(self, minimal_item):
        minimal_item["geo_restriction"] = {"type": "whitelist", "regions": ["GB"]}
        assert validate_item(minimal_item)

    def test_invalid_region_code(self, minimal_item):
        minimal_item["geo_restriction"] = {"type": "allowlist", "regions": ["GBR"]}
        assert validate_item(minimal_item)

    def test_empty_regions_rejected(self, minimal_item):
        minimal_item["geo_restriction"] = {"type": "allowlist", "regions": []}
        assert validate_item(minimal_item)


class TestPaywall:
    def test_paywalled_true(self, minimal_item):
        minimal_item["paywall"] = {"paywalled": True, "preview_available": True}
        assert is_valid_item(minimal_item)

    def test_paywalled_false(self, minimal_item):
        minimal_item["paywall"] = {"paywalled": False}
        assert is_valid_item(minimal_item)

    def test_paywall_missing_paywalled(self, minimal_item):
        minimal_item["paywall"] = {"preview_available": True}
        assert validate_item(minimal_item)


class TestSourceMeta:
    def test_valid_source_meta(self, minimal_item):
        minimal_item["source"] = {"type": "rss", "feed_url": "https://example.com/feed.xml"}
        assert is_valid_item(minimal_item)

    def test_source_meta_with_title(self, minimal_item):
        minimal_item["source"] = {"type": "rss", "feed_url": "https://example.com/feed.xml", "feed_title": "Example Feed"}
        assert is_valid_item(minimal_item)

    def test_source_invalid_type(self, minimal_item):
        minimal_item["source"] = {"type": "scrape", "feed_url": "https://example.com/feed.xml"}
        assert validate_item(minimal_item)

    def test_source_missing_feed_url(self, minimal_item):
        minimal_item["source"] = {"type": "rss"}
        assert validate_item(minimal_item)

    @pytest.mark.parametrize("source_type", ["mfeed", "rss", "atom", "podcast", "platform"])
    def test_all_source_types(self, minimal_item, source_type):
        minimal_item["source"] = {"type": source_type, "feed_url": "https://example.com/feed"}
        assert is_valid_item(minimal_item)

"""Tests for all MMSP item types and multimedia schema (Section 6.3)."""

import pytest
from tests.validators.schema import is_valid_item, validate_item


def make_item(item_type: str, **extra) -> dict:
    item = {
        "id": f"https://example.com/items/{item_type}-1",
        "type": item_type,
        "title": f"Test {item_type.title()} Item",
        "url": f"https://example.com/items/{item_type}-1",
        "published": "2026-06-01T00:00:00Z",
    }
    item.update(extra)
    return item


class TestVideoItem:
    def test_minimal_video_valid(self):
        assert is_valid_item(make_item("video"))

    def test_video_with_duration(self):
        assert is_valid_item(make_item("video", duration=1800))

    def test_video_with_media(self):
        item = make_item("video", media=[
            {"url": "https://cdn.example.com/v.mp4", "mime_type": "video/mp4"}
        ])
        assert is_valid_item(item)

    def test_video_with_quality_variants(self):
        item = make_item("video", media=[
            {"url": "https://cdn.example.com/v-1080p.mp4", "mime_type": "video/mp4", "quality_label": "1080p", "role": "primary"},
            {"url": "https://cdn.example.com/v-720p.mp4", "mime_type": "video/mp4", "quality_label": "720p", "role": "alternate"},
        ])
        assert is_valid_item(item)

    def test_video_with_chapters(self):
        item = make_item("video", chapters=[
            {"title": "Intro", "start_seconds": 0},
            {"title": "Main", "start_seconds": 60},
        ])
        assert is_valid_item(item)

    def test_video_with_captions(self):
        item = make_item("video", captions=[
            {"url": "https://cdn.example.com/sub.vtt", "mime_type": "text/vtt", "language": "en"}
        ])
        assert is_valid_item(item)

    def test_video_with_transcript(self):
        item = make_item("video", transcript={
            "url": "https://cdn.example.com/transcript.txt",
            "mime_type": "text/plain",
        })
        assert is_valid_item(item)


class TestAudioItem:
    def test_minimal_audio_valid(self):
        assert is_valid_item(make_item("audio"))

    def test_audio_with_duration(self):
        assert is_valid_item(make_item("audio", duration=3600))

    def test_audio_with_media(self):
        item = make_item("audio", media=[
            {"url": "https://cdn.example.com/ep.mp3", "mime_type": "audio/mpeg"}
        ])
        assert is_valid_item(item)

    def test_audio_with_transcript(self):
        item = make_item("audio", transcript={
            "url": "https://cdn.example.com/transcript.txt",
            "mime_type": "text/plain",
            "language": "en",
        })
        assert is_valid_item(item)


class TestArticleItem:
    def test_minimal_article_valid(self):
        assert is_valid_item(make_item("article"))

    def test_article_with_description(self):
        assert is_valid_item(make_item("article", description="<p>Content</p>"))

    def test_article_with_tags(self):
        assert is_valid_item(make_item("article", tags=["tech", "news"]))


class TestShortItem:
    def test_minimal_short_valid(self):
        assert is_valid_item(make_item("short"))

    def test_short_with_duration(self):
        assert is_valid_item(make_item("short", duration=45))

    def test_short_with_media(self):
        item = make_item("short", media=[
            {"url": "https://cdn.example.com/short.mp4", "mime_type": "video/mp4"}
        ])
        assert is_valid_item(item)


class TestImageItem:
    def test_minimal_image_valid(self):
        assert is_valid_item(make_item("image"))

    def test_image_with_media(self):
        item = make_item("image", media=[
            {"url": "https://cdn.example.com/photo.jpg", "mime_type": "image/jpeg", "width": 4000, "height": 3000}
        ])
        assert is_valid_item(item)


class TestDocumentItem:
    def test_minimal_document_valid(self):
        assert is_valid_item(make_item("document"))

    def test_document_with_media(self):
        item = make_item("document", media=[
            {"url": "https://cdn.example.com/report.pdf", "mime_type": "application/pdf", "size_bytes": 5242880}
        ])
        assert is_valid_item(item)


class TestGalleryItem:
    def test_minimal_gallery_valid(self):
        assert is_valid_item(make_item("gallery"))

    def test_gallery_with_multiple_images(self):
        item = make_item("gallery", media=[
            {"url": f"https://cdn.example.com/img{i}.jpg", "mime_type": "image/jpeg", "role": "primary"}
            for i in range(5)
        ])
        assert is_valid_item(item)


class TestEventItem:
    def test_minimal_event_valid(self):
        assert is_valid_item(make_item("event"))

    def test_event_with_scheduled_start(self):
        item = make_item("event", scheduled_start="2026-07-01T17:00:00Z")
        assert is_valid_item(item)


class TestReleaseItem:
    def test_minimal_release_valid(self):
        assert is_valid_item(make_item("release"))

    def test_release_with_description(self):
        item = make_item("release", description="<p>Fixed bug #123</p>")
        assert is_valid_item(item)


class TestNewsletterItem:
    def test_minimal_newsletter_valid(self):
        assert is_valid_item(make_item("newsletter"))

    def test_newsletter_with_series(self):
        item = make_item("newsletter", series={
            "id": "https://example.com/newsletters/weekly",
            "title": "Weekly Newsletter",
            "episode_number": 52,
        })
        assert is_valid_item(item)


class TestCourseItem:
    def test_minimal_course_valid(self):
        assert is_valid_item(make_item("course"))

    def test_course_with_series(self):
        item = make_item("course", series={
            "id": "https://example.com/courses/python-101",
            "title": "Python 101",
            "episode_number": 3,
            "season_number": 1,
            "total_episodes": 20,
        })
        assert is_valid_item(item)


class TestLivestreamItem:
    def test_minimal_livestream_valid(self):
        assert is_valid_item(make_item("livestream"))

    def test_livestream_statuses(self):
        for status in ("upcoming", "live", "ended", "archived"):
            item = make_item("livestream", live_status=status)
            assert is_valid_item(item)

    def test_livestream_with_scheduled_start(self):
        item = make_item("livestream", live_status="upcoming", scheduled_start="2026-08-01T20:00:00Z")
        assert is_valid_item(item)

    def test_livestream_with_duration_after_archive(self):
        item = make_item("livestream", live_status="archived", duration=7200)
        assert is_valid_item(item)


class TestUnrecognizedType:
    def test_unrecognized_type_rejected_by_schema(self):
        item = make_item("webcomic")
        errors = validate_item(item)
        assert errors

    def test_all_twelve_types_recognized(self):
        types = [
            "video", "audio", "article", "image", "short",
            "document", "gallery", "event", "release",
            "newsletter", "course", "livestream",
        ]
        assert len(types) == 12
        for t in types:
            assert is_valid_item(make_item(t))


class TestPaywallAndGeoOnAnyType:
    @pytest.mark.parametrize("item_type", ["video", "audio", "article", "document"])
    def test_paywall_on_item_type(self, item_type):
        item = make_item(item_type, paywall={"paywalled": True, "preview_available": True})
        assert is_valid_item(item)

    @pytest.mark.parametrize("item_type", ["video", "audio", "article"])
    def test_geo_restriction_on_item_type(self, item_type):
        item = make_item(item_type, geo_restriction={"type": "allowlist", "regions": ["GB", "IE"]})
        assert is_valid_item(item)


class TestPreviewUrl:
    def test_preview_url_on_video(self):
        item = make_item("video", preview_url="https://cdn.example.com/preview-30s.mp4")
        assert is_valid_item(item)

    def test_preview_url_must_be_https(self):
        item = make_item("video", preview_url="http://cdn.example.com/preview-30s.mp4")
        assert validate_item(item)

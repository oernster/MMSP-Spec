"""Tests for RSS 2.0 normalization to MMSP (Section 10, Appendix B)."""

import pytest
from tests.validators.normalizer import normalize_rss_feed, normalize_rss_item
from tests.validators.schema import is_valid_item
from xml.etree import ElementTree as ET


FEED_URL = "https://example.com/feed.xml"


class TestRssBasicNormalization:
    def test_produces_items(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert len(items) == 2

    def test_item_title_mapped(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert items[0]["title"] == "Article One"

    def test_item_url_mapped(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert items[0]["url"] == "https://example.com/articles/1"

    def test_item_id_from_guid(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert items[0]["id"] == "https://example.com/articles/1"

    def test_item_published_mapped(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert "published" in items[0]
        assert "2026" in items[0]["published"]

    def test_item_description_mapped(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert items[0]["description"] == "First article"

    def test_item_tags_from_categories(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert "tech" in items[0]["tags"]
        assert "news" in items[0]["tags"]

    def test_source_metadata_populated(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert items[0]["source"]["type"] == "rss"
        assert items[0]["source"]["feed_url"] == FEED_URL

    def test_feed_title_in_source(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert items[0]["source"]["feed_title"] == "Test RSS Feed"


class TestRssTypeInference:
    def test_article_inferred_without_enclosure(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert items[0]["type"] == "article"

    def test_video_inferred_from_video_enclosure(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert items[1]["type"] == "video"

    def test_audio_inferred_from_audio_mime(self):
        xml = """<rss version="2.0"><channel><title>T</title>
        <item>
          <guid>https://example.com/ep1</guid>
          <title>Audio Item</title>
          <link>https://example.com/ep1</link>
          <enclosure url="https://cdn.example.com/ep1.mp3" type="audio/mpeg" length="1000"/>
        </item>
        </channel></rss>"""
        items = normalize_rss_feed(xml, FEED_URL)
        assert items[0]["type"] == "audio"

    def test_image_inferred_from_image_mime(self):
        xml = """<rss version="2.0"><channel><title>T</title>
        <item>
          <guid>https://example.com/img1</guid>
          <title>Image Item</title>
          <link>https://example.com/img1</link>
          <enclosure url="https://cdn.example.com/img.jpg" type="image/jpeg" length="500"/>
        </item>
        </channel></rss>"""
        items = normalize_rss_feed(xml, FEED_URL)
        assert items[0]["type"] == "image"


class TestRssEnclosure:
    def test_enclosure_mapped_to_media(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        video_item = items[1]
        assert "media" in video_item
        assert video_item["media"][0]["url"] == "https://cdn.example.com/video.mp4"
        assert video_item["media"][0]["mime_type"] == "video/mp4"
        assert video_item["media"][0]["size_bytes"] == 10485760

    def test_enclosure_role_is_primary(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert items[1]["media"][0]["role"] == "primary"


class TestRssMediaNamespace:
    def test_media_thumbnail_mapped(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        video_item = items[1]
        assert "thumbnail" in video_item
        assert video_item["thumbnail"][0]["url"] == "https://cdn.example.com/thumb.jpg"
        assert video_item["thumbnail"][0]["width"] == 1280
        assert video_item["thumbnail"][0]["height"] == 720


class TestRssAuthor:
    def test_author_extracted_from_email(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        assert "authors" in items[0]
        assert items[0]["authors"][0]["name"] == "Test Author"


class TestRssNormalizationProducesValidItems:
    def test_all_items_valid(self, rss_feed_xml):
        items = normalize_rss_feed(rss_feed_xml, FEED_URL)
        for item in items:
            assert is_valid_item(item), f"Invalid item: {item}"


class TestRssPodcastNormalization:
    def test_podcast_type_is_audio(self, rss_audio_xml):
        from tests.validators.normalizer import normalize_rss_feed
        items = normalize_rss_feed(rss_audio_xml, FEED_URL, source_type="podcast")
        assert items[0]["type"] == "audio"

    def test_itunes_duration_seconds_integer(self, rss_audio_xml):
        items = normalize_rss_feed(rss_audio_xml, FEED_URL, source_type="podcast")
        assert items[0]["duration"] == 3600

    def test_itunes_episode_number(self, rss_audio_xml):
        items = normalize_rss_feed(rss_audio_xml, FEED_URL, source_type="podcast")
        assert items[0]["series"]["episode_number"] == 1

    def test_itunes_season_number(self, rss_audio_xml):
        items = normalize_rss_feed(rss_audio_xml, FEED_URL, source_type="podcast")
        assert items[0]["series"]["season_number"] == 1

    def test_itunes_explicit_no_maps_to_general(self, rss_audio_xml):
        items = normalize_rss_feed(rss_audio_xml, FEED_URL, source_type="podcast")
        assert items[0]["content_rating"]["rating"] == "general"

    def test_itunes_explicit_yes_maps_to_explicit(self):
        xml = """<rss version="2.0"
             xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
          <channel><title>T</title>
          <item>
            <guid>https://example.com/ep2</guid>
            <title>Explicit Ep</title>
            <link>https://example.com/ep2</link>
            <enclosure url="https://cdn.example.com/ep2.mp3" type="audio/mpeg" length="1000"/>
            <itunes:explicit>yes</itunes:explicit>
          </item></channel></rss>"""
        items = normalize_rss_feed(xml, FEED_URL, source_type="podcast")
        assert items[0]["content_rating"]["rating"] == "explicit"

    def test_itunes_image_mapped_to_thumbnail(self, rss_audio_xml):
        items = normalize_rss_feed(rss_audio_xml, FEED_URL, source_type="podcast")
        assert items[0]["thumbnail"][0]["url"] == "https://cdn.example.com/podcast-art.jpg"

    def test_podcast_transcript_mapped(self, rss_audio_xml):
        items = normalize_rss_feed(rss_audio_xml, FEED_URL, source_type="podcast")
        assert items[0]["transcript"]["url"] == "https://cdn.example.com/ep1-transcript.txt"
        assert items[0]["transcript"]["mime_type"] == "text/plain"
        assert items[0]["transcript"]["language"] == "en"

    def test_source_type_is_podcast(self, rss_audio_xml):
        items = normalize_rss_feed(rss_audio_xml, FEED_URL, source_type="podcast")
        assert items[0]["source"]["type"] == "podcast"

    def test_podcast_items_valid(self, rss_audio_xml):
        items = normalize_rss_feed(rss_audio_xml, FEED_URL, source_type="podcast")
        for item in items:
            assert is_valid_item(item)


class TestRssEdgeCases:
    def test_empty_channel_returns_empty(self):
        xml = """<rss version="2.0"><channel><title>Empty</title></channel></rss>"""
        items = normalize_rss_feed(xml, FEED_URL)
        assert items == []

    def test_no_channel_returns_empty(self):
        xml = """<rss version="2.0"></rss>"""
        items = normalize_rss_feed(xml, FEED_URL)
        assert items == []

    def test_guid_without_http_prefixed_with_feed_url(self):
        xml = """<rss version="2.0"><channel><title>T</title>
        <item>
          <guid>local-id-123</guid>
          <title>Local ID Item</title>
          <link>https://example.com/items/local-id-123</link>
        </item>
        </channel></rss>"""
        items = normalize_rss_feed(xml, FEED_URL)
        assert items[0]["id"].startswith(FEED_URL)

    def test_missing_guid_uses_link(self):
        xml = """<rss version="2.0"><channel><title>T</title>
        <item>
          <title>No GUID</title>
          <link>https://example.com/no-guid</link>
        </item>
        </channel></rss>"""
        items = normalize_rss_feed(xml, FEED_URL)
        assert items[0]["id"] == "https://example.com/no-guid"

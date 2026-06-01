"""Shared fixtures for the MMSP conformance test suite."""

import json
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "spec" / "examples"


@pytest.fixture
def minimal_feed() -> dict:
    with (EXAMPLES_DIR / "minimal-feed.json").open() as f:
        return json.load(f)


@pytest.fixture
def full_feed() -> dict:
    with (EXAMPLES_DIR / "full-feed.json").open() as f:
        return json.load(f)


@pytest.fixture
def minimal_item() -> dict:
    return {
        "id": "https://example.com/items/1",
        "type": "article",
        "title": "Test Item",
        "url": "https://example.com/items/1",
        "published": "2026-06-01T00:00:00Z",
    }


@pytest.fixture
def video_item() -> dict:
    return {
        "id": "https://example.com/videos/1",
        "type": "video",
        "title": "Test Video",
        "url": "https://example.com/videos/1",
        "published": "2026-06-01T00:00:00Z",
        "duration": 600,
        "media": [
            {
                "url": "https://cdn.example.com/video.mp4",
                "mime_type": "video/mp4",
                "role": "primary",
            }
        ],
    }


@pytest.fixture
def rss_feed_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>Test RSS Feed</title>
    <link>https://example.com</link>
    <description>Test feed</description>
    <item>
      <guid>https://example.com/articles/1</guid>
      <title>Article One</title>
      <link>https://example.com/articles/1</link>
      <description>First article</description>
      <pubDate>Mon, 01 Jun 2026 10:00:00 +0000</pubDate>
      <author>author@example.com (Test Author)</author>
      <category>tech</category>
      <category>news</category>
    </item>
    <item>
      <guid>https://example.com/videos/1</guid>
      <title>Video One</title>
      <link>https://example.com/videos/1</link>
      <description>First video</description>
      <pubDate>Mon, 01 Jun 2026 09:00:00 +0000</pubDate>
      <enclosure url="https://cdn.example.com/video.mp4"
                 type="video/mp4" length="10485760"/>
      <media:thumbnail url="https://cdn.example.com/thumb.jpg"
                       width="1280" height="720"/>
    </item>
  </channel>
</rss>"""


@pytest.fixture
def rss_audio_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:podcast="https://podcastindex.org/namespace/1.0">
  <channel>
    <title>Test Podcast</title>
    <link>https://podcast.example.com</link>
    <item>
      <guid>https://podcast.example.com/ep1</guid>
      <title>Episode 1</title>
      <link>https://podcast.example.com/ep1</link>
      <description>First episode</description>
      <pubDate>Mon, 01 Jun 2026 08:00:00 +0000</pubDate>
      <enclosure url="https://cdn.example.com/ep1.mp3"
                 type="audio/mpeg" length="52428800"/>
      <itunes:duration>3600</itunes:duration>
      <itunes:episode>1</itunes:episode>
      <itunes:season>1</itunes:season>
      <itunes:explicit>no</itunes:explicit>
      <itunes:image href="https://cdn.example.com/podcast-art.jpg"/>
      <podcast:transcript url="https://cdn.example.com/ep1-transcript.txt"
                          type="text/plain" language="en"/>
    </item>
  </channel>
</rss>"""


@pytest.fixture
def atom_feed_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>https://example.com/atom</id>
  <title>Test Atom Feed</title>
  <link href="https://example.com"/>
  <updated>2026-06-01T10:00:00Z</updated>
  <entry>
    <id>https://example.com/entries/1</id>
    <title>Atom Entry One</title>
    <link rel="alternate" href="https://example.com/entries/1"/>
    <published>2026-06-01T10:00:00Z</published>
    <updated>2026-06-01T11:00:00Z</updated>
    <author>
      <name>Test Author</name>
      <uri>https://example.com/author</uri>
    </author>
    <category term="technology"/>
    <summary>Summary of entry one</summary>
  </entry>
  <entry>
    <id>https://example.com/entries/2</id>
    <title>Atom Entry Two</title>
    <link rel="alternate" href="https://example.com/entries/2"/>
    <link rel="enclosure" href="https://cdn.example.com/audio.mp3"
          type="audio/mpeg" length="5242880"/>
    <published>2026-05-31T10:00:00Z</published>
    <content>Full content of entry two</content>
  </entry>
</feed>"""

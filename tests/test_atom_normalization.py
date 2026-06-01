"""Tests for Atom 1.0 normalization to MMSP (Section 10, Appendix C)."""

import pytest
from tests.validators.normalizer import normalize_atom_feed
from tests.validators.schema import is_valid_item

FEED_URL = "https://example.com/atom.xml"


class TestAtomBasicNormalization:
    def test_produces_items(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert len(items) == 2

    def test_entry_id_mapped(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["id"] == "https://example.com/entries/1"

    def test_entry_title_mapped(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["title"] == "Atom Entry One"

    def test_entry_url_from_alternate_link(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["url"] == "https://example.com/entries/1"

    def test_entry_published_mapped(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["published"] == "2026-06-01T10:00:00Z"

    def test_entry_updated_mapped(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["updated"] == "2026-06-01T11:00:00Z"

    def test_updated_omitted_when_same_as_published(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>https://example.com/atom</id>
  <title>T</title>
  <entry>
    <id>https://example.com/e1</id>
    <title>Entry</title>
    <link rel="alternate" href="https://example.com/e1"/>
    <published>2026-06-01T10:00:00Z</published>
    <updated>2026-06-01T10:00:00Z</updated>
  </entry>
</feed>"""
        items = normalize_atom_feed(xml, FEED_URL)
        assert "updated" not in items[0]

    def test_summary_mapped_to_description(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["description"] == "Summary of entry one"

    def test_content_preferred_over_summary(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[1]["description"] == "Full content of entry two"


class TestAtomAuthor:
    def test_author_name_mapped(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["authors"][0]["name"] == "Test Author"

    def test_author_uri_mapped_to_url(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["authors"][0]["url"] == "https://example.com/author"

    def test_no_author_element_no_authors_field(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert "authors" not in items[1]


class TestAtomCategories:
    def test_category_terms_mapped_to_tags(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert "technology" in items[0]["tags"]


class TestAtomTypeInference:
    def test_article_inferred_without_enclosure(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["type"] == "article"

    def test_audio_inferred_from_enclosure_link(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[1]["type"] == "audio"


class TestAtomEnclosure:
    def test_enclosure_link_mapped_to_media(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[1]["media"][0]["url"] == "https://cdn.example.com/audio.mp3"
        assert items[1]["media"][0]["mime_type"] == "audio/mpeg"
        assert items[1]["media"][0]["size_bytes"] == 5242880

    def test_enclosure_role_is_primary(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[1]["media"][0]["role"] == "primary"


class TestAtomSourceMetadata:
    def test_source_type_is_atom(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["source"]["type"] == "atom"

    def test_source_feed_url_populated(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["source"]["feed_url"] == FEED_URL

    def test_feed_title_in_source(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        assert items[0]["source"]["feed_title"] == "Test Atom Feed"


class TestAtomNormalizationProducesValidItems:
    def test_all_items_valid(self, atom_feed_xml):
        items = normalize_atom_feed(atom_feed_xml, FEED_URL)
        for item in items:
            assert is_valid_item(item), f"Invalid item: {item}"


class TestAtomEdgeCases:
    def test_empty_feed_returns_empty(self):
        xml = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>https://example.com</id>
  <title>Empty</title>
</feed>"""
        items = normalize_atom_feed(xml, FEED_URL)
        assert items == []

    def test_entry_without_published_uses_updated(self):
        xml = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>https://example.com</id>
  <title>T</title>
  <entry>
    <id>https://example.com/e1</id>
    <title>No Published</title>
    <link rel="alternate" href="https://example.com/e1"/>
    <updated>2026-05-01T00:00:00Z</updated>
  </entry>
</feed>"""
        items = normalize_atom_feed(xml, FEED_URL)
        assert "published" in items[0]


class TestAtomLinkEdge:
    def test_link_with_other_rel_ignored(self):
        xml = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>T</title>
  <entry>
    <id>https://example.com/e1</id>
    <title>Entry</title>
    <link rel="alternate" href="https://example.com/e1"/>
    <link rel="self" href="https://example.com/atom/entries/1"/>
    <published>2026-06-01T00:00:00Z</published>
  </entry>
</feed>"""
        items = normalize_atom_feed(xml, FEED_URL)
        assert items[0]["url"] == "https://example.com/e1"

    def test_enclosure_without_length_no_size_bytes(self):
        xml = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>T</title>
  <entry>
    <id>https://example.com/e1</id>
    <title>Audio</title>
    <link rel="alternate" href="https://example.com/e1"/>
    <link rel="enclosure" href="https://cdn.example.com/a.mp3" type="audio/mpeg"/>
    <published>2026-06-01T00:00:00Z</published>
  </entry>
</feed>"""
        items = normalize_atom_feed(xml, FEED_URL)
        assert "size_bytes" not in items[0]["media"][0]

    def test_enclosure_bad_length_no_size_bytes(self):
        xml = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>T</title>
  <entry>
    <id>https://example.com/e1</id>
    <title>Audio</title>
    <link rel="alternate" href="https://example.com/e1"/>
    <link rel="enclosure" href="https://cdn.example.com/a.mp3" type="audio/mpeg" length="notanumber"/>
    <published>2026-06-01T00:00:00Z</published>
  </entry>
</feed>"""
        items = normalize_atom_feed(xml, FEED_URL)
        assert "size_bytes" not in items[0]["media"][0]


class TestAtomAuthorEdge:
    def test_author_without_uri_no_url(self):
        xml = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>T</title>
  <entry>
    <id>https://example.com/e1</id>
    <title>Entry</title>
    <link rel="alternate" href="https://example.com/e1"/>
    <published>2026-06-01T00:00:00Z</published>
    <author><name>Alice</name></author>
  </entry>
</feed>"""
        items = normalize_atom_feed(xml, FEED_URL)
        assert items[0]["authors"][0]["name"] == "Alice"
        assert "url" not in items[0]["authors"][0]


class TestAtomSourceMetadataEdge:
    def test_feed_without_title_no_feed_title_in_source(self):
        xml = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>https://example.com/e1</id>
    <title>Entry</title>
    <link rel="alternate" href="https://example.com/e1"/>
    <published>2026-06-01T00:00:00Z</published>
  </entry>
</feed>"""
        items = normalize_atom_feed(xml, FEED_URL)
        assert "feed_title" not in items[0]["source"]

"""Tests for MMSP feed discovery (Section 9)."""

import pytest
from tests.validators.discovery import (
    ATOM_MIME_TYPE,
    MMSP_MIME_TYPE,
    RSS_MIME_TYPE,
    WELL_KNOWN_PATH,
    discover_from_html,
    validate_feed_url,
    validate_source_url,
    well_known_url,
)


class TestWellKnownUrl:
    def test_basic_well_known(self):
        result = well_known_url("https://example.com")
        assert result == "https://example.com/.well-known/mmsp.json"

    def test_well_known_path_constant(self):
        assert WELL_KNOWN_PATH == "/.well-known/mmsp.json"

    def test_preserves_host(self):
        result = well_known_url("https://media.example.com/some/page")
        assert result == "https://media.example.com/.well-known/mmsp.json"

    def test_http_scheme_preserved(self):
        result = well_known_url("http://example.com")
        assert "http://example.com" in result


class TestDiscoverFromHtml:
    def test_mmsp_link_discovered(self):
        html = '<link rel="alternate" type="application/mmsp+json" href="https://example.com/mmsp.json">'
        links = discover_from_html(html, "https://example.com")
        assert len(links) == 1
        assert links[0]["type"] == MMSP_MIME_TYPE
        assert links[0]["href"] == "https://example.com/mmsp.json"

    def test_rss_link_discovered(self):
        html = '<link rel="alternate" type="application/rss+xml" href="https://example.com/feed.xml">'
        links = discover_from_html(html, "https://example.com")
        assert len(links) == 1
        assert links[0]["type"] == RSS_MIME_TYPE

    def test_atom_link_discovered(self):
        html = '<link rel="alternate" type="application/atom+xml" href="https://example.com/atom.xml">'
        links = discover_from_html(html, "https://example.com")
        assert len(links) == 1
        assert links[0]["type"] == ATOM_MIME_TYPE

    def test_mmsp_before_rss_before_atom(self):
        html = """
        <link rel="alternate" type="application/atom+xml" href="https://example.com/atom.xml">
        <link rel="alternate" type="application/rss+xml" href="https://example.com/rss.xml">
        <link rel="alternate" type="application/mmsp+json" href="https://example.com/mmsp.json">
        """
        links = discover_from_html(html, "https://example.com")
        types = [l["type"] for l in links]
        assert types[0] == MMSP_MIME_TYPE
        assert types[1] == RSS_MIME_TYPE
        assert types[2] == ATOM_MIME_TYPE

    def test_non_alternate_rel_ignored(self):
        html = '<link rel="stylesheet" type="application/mmsp+json" href="https://example.com/mmsp.json">'
        links = discover_from_html(html, "https://example.com")
        assert len(links) == 0

    def test_relative_href_resolved(self):
        html = '<link rel="alternate" type="application/mmsp+json" href="/feeds/main.json">'
        links = discover_from_html(html, "https://example.com")
        assert links[0]["href"] == "https://example.com/feeds/main.json"

    def test_unknown_type_ignored(self):
        html = '<link rel="alternate" type="text/html" href="https://example.com/">'
        links = discover_from_html(html, "https://example.com")
        assert len(links) == 0

    def test_title_attribute_included(self):
        html = '<link rel="alternate" type="application/mmsp+json" href="https://example.com/mmsp.json" title="My Feed">'
        links = discover_from_html(html, "https://example.com")
        assert links[0].get("title") == "My Feed"

    def test_no_href_ignored(self):
        html = '<link rel="alternate" type="application/mmsp+json">'
        links = discover_from_html(html, "https://example.com")
        assert len(links) == 0

    def test_empty_html(self):
        links = discover_from_html("", "https://example.com")
        assert links == []


class TestValidateFeedUrl:
    def test_https_url_valid(self):
        ok, _ = validate_feed_url("https://example.com/.well-known/mmsp.json")
        assert ok

    def test_http_url_invalid(self):
        ok, msg = validate_feed_url("http://example.com/.well-known/mmsp.json")
        assert not ok
        assert "HTTPS" in msg

    def test_empty_url_invalid(self):
        ok, msg = validate_feed_url("")
        assert not ok

    def test_ftp_url_invalid(self):
        ok, msg = validate_feed_url("ftp://example.com/feed")
        assert not ok

    def test_url_without_host_invalid(self):
        ok, msg = validate_feed_url("https:///path")
        assert not ok


class TestValidateSourceUrl:
    @pytest.mark.parametrize("source_type", ["rss", "atom", "podcast", "mfeed"])
    def test_https_required_for_declared_types(self, source_type):
        ok, _ = validate_source_url("https://example.com/feed.xml", source_type)
        assert ok

    @pytest.mark.parametrize("source_type", ["rss", "atom", "podcast", "mfeed"])
    def test_http_rejected_for_declared_types(self, source_type):
        ok, _ = validate_source_url("http://example.com/feed.xml", source_type)
        assert not ok

    def test_platform_source_always_valid(self):
        ok, _ = validate_source_url("custom://platform-internal-id", "platform")
        assert ok

"""MMSP feed discovery utilities."""

from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse


WELL_KNOWN_PATH = "/.well-known/mmsp.json"
MMSP_MIME_TYPE = "application/mmsp+json"
RSS_MIME_TYPE = "application/rss+xml"
ATOM_MIME_TYPE = "application/atom+xml"


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "link":
            return
        attr_dict = {k.lower(): v or "" for k, v in attrs}
        if attr_dict.get("rel") == "alternate":
            self.links.append(attr_dict)


def discover_from_html(html: str, base_url: str) -> list[dict[str, str]]:
    """
    Extract alternate feed links from HTML.

    Returns list of dicts with keys: type, href, title (optional).
    Ordered: MMSP first, then RSS, then Atom.
    """
    parser = _LinkParser()
    parser.feed(html)

    mmsp_links = []
    rss_links = []
    atom_links = []

    for link in parser.links:
        mime = link.get("type", "")
        href = link.get("href", "")
        if not href:
            continue
        if not href.startswith("http"):
            href = urljoin(base_url, href)
        entry = {"type": mime, "href": href}
        if "title" in link:
            entry["title"] = link["title"]
        if mime == MMSP_MIME_TYPE:
            mmsp_links.append(entry)
        elif mime == RSS_MIME_TYPE:
            rss_links.append(entry)
        elif mime == ATOM_MIME_TYPE:
            atom_links.append(entry)

    return mmsp_links + rss_links + atom_links


def well_known_url(base_url: str) -> str:
    """Return the well-known MMSP URL for a given base URL."""
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}{WELL_KNOWN_PATH}"


def validate_feed_url(url: str) -> tuple[bool, str]:
    """
    Validate a feed URL per MMSP spec Section 11.
    Feed URLs MUST use HTTPS.
    """
    if not url:
        return False, "URL is empty"
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False, f"Feed URL must use HTTPS, got scheme: {parsed.scheme!r}"
    if not parsed.netloc:
        return False, "Feed URL has no host"
    return True, "valid"


def validate_source_url(url: str, source_type: str) -> tuple[bool, str]:
    """
    Validate a source URL. RSS/Atom/podcast source URLs MUST use HTTPS.
    """
    if source_type == "platform":
        return True, "platform source URL validation is implementation-specific"
    return validate_feed_url(url)

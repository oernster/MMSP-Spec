"""RSS 2.0, Atom, and Podcast namespace normalization to MMSP item schema."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from xml.etree import ElementTree as ET

RSS_NS = ""
MEDIA_NS = "http://search.yahoo.com/mrss/"
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
PODCAST_NS = "https://podcastindex.org/namespace/1.0"
ATOM_NS = "http://www.w3.org/2005/Atom"

VIDEO_MIME_PREFIXES = ("video/",)
AUDIO_MIME_PREFIXES = ("audio/",)
IMAGE_MIME_PREFIXES = ("image/",)


def _parse_rss_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        return None


def _parse_iso_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    return date_str.strip()


def _infer_type(mime_type: str | None) -> str:
    if not mime_type:
        return "article"
    if any(mime_type.startswith(p) for p in VIDEO_MIME_PREFIXES):
        return "video"
    if any(mime_type.startswith(p) for p in AUDIO_MIME_PREFIXES):
        return "audio"
    if any(mime_type.startswith(p) for p in IMAGE_MIME_PREFIXES):
        return "image"
    return "article"


def _ns(tag: str, namespace: str) -> str:
    if namespace:
        return f"{{{namespace}}}{tag}"
    return tag


def _parse_itunes_duration(duration_str: str | None) -> int | None:
    if not duration_str:
        return None
    parts = duration_str.strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return int(parts[0])
    except (ValueError, IndexError):
        return None


def normalize_rss_item(
    item_el: ET.Element,
    feed_url: str,
    feed_title: str | None,
    source_type: str = "rss",
) -> dict[str, Any]:
    """Normalize a single RSS <item> element to MMSP item schema."""

    def text(tag: str, ns: str = "") -> str | None:
        el = item_el.find(_ns(tag, ns))
        return el.text.strip() if el is not None and el.text else None

    def attr(tag: str, attribute: str, ns: str = "") -> str | None:
        el = item_el.find(_ns(tag, ns))
        return el.get(attribute) if el is not None else None

    guid = text("guid") or ""
    title = text("title") or ""
    link = text("link") or ""
    description = text("description")
    pub_date = _parse_rss_date(text("pubDate"))
    author_email = text("author")

    enclosure_url = attr("enclosure", "url")
    enclosure_type = attr("enclosure", "type")
    enclosure_length = attr("enclosure", "length")

    media_content_el = item_el.find(_ns("content", MEDIA_NS))
    media_thumbnail_el = item_el.find(_ns("thumbnail", MEDIA_NS))

    itunes_duration = _parse_itunes_duration(text("duration", ITUNES_NS))
    itunes_episode = text("episode", ITUNES_NS)
    itunes_season = text("season", ITUNES_NS)
    itunes_title = text("title", ITUNES_NS)
    itunes_image = item_el.find(_ns("image", ITUNES_NS))
    itunes_explicit = text("explicit", ITUNES_NS)

    podcast_transcript_el = item_el.find(_ns("transcript", PODCAST_NS))

    categories = [
        el.text.strip()
        for el in item_el.findall("category")
        if el.text
    ]

    mime_type = None
    media: list[dict] = []

    if enclosure_url:
        mime_type = enclosure_type
        entry: dict[str, Any] = {"url": enclosure_url, "mime_type": enclosure_type or "application/octet-stream", "role": "primary"}
        if enclosure_length:
            try:
                entry["size_bytes"] = int(enclosure_length)
            except ValueError:
                pass
        media.append(entry)

    if media_content_el is not None:
        mc_url = media_content_el.get("url")
        mc_type = media_content_el.get("type")
        if mc_url:
            if not mime_type:
                mime_type = mc_type
            mc_entry: dict[str, Any] = {"url": mc_url, "mime_type": mc_type or "application/octet-stream", "role": "primary"}
            mc_duration = media_content_el.get("duration")
            if mc_duration:
                try:
                    mc_entry["duration"] = int(mc_duration)
                except ValueError:
                    pass
            if not media:
                media.append(mc_entry)

    thumbnails: list[dict] = []
    if media_thumbnail_el is not None:
        th_url = media_thumbnail_el.get("url")
        if th_url:
            th_entry: dict[str, Any] = {"url": th_url}
            th_w = media_thumbnail_el.get("width")
            th_h = media_thumbnail_el.get("height")
            if th_w:
                try:
                    th_entry["width"] = int(th_w)
                except ValueError:
                    pass
            if th_h:
                try:
                    th_entry["height"] = int(th_h)
                except ValueError:
                    pass
            thumbnails.append(th_entry)

    if itunes_image is not None:
        itunes_img_href = itunes_image.get("href")
        if itunes_img_href and not thumbnails:
            thumbnails.append({"url": itunes_img_href})

    item_type = _infer_type(mime_type)
    if source_type == "podcast":
        item_type = "audio"

    item_id = guid if guid.startswith("http") else f"{feed_url}#{guid}" if guid else link

    result: dict[str, Any] = {
        "id": item_id,
        "type": item_type,
        "title": itunes_title or title,
        "url": link,
        "published": pub_date or datetime.now(timezone.utc).isoformat(),
    }

    if description:
        result["description"] = description
    if categories:
        result["tags"] = categories
    if author_email:
        name = re.sub(r".*\((.*)\).*", r"\1", author_email).strip()
        result["authors"] = [{"name": name or author_email}]
    if media:
        result["media"] = media
    if thumbnails:
        result["thumbnail"] = thumbnails
    if itunes_duration:
        result["duration"] = itunes_duration

    if itunes_episode or itunes_season:
        series: dict[str, Any] = {
            "id": f"{feed_url}#series",
            "title": feed_title or "Podcast",
        }
        if itunes_episode:
            try:
                series["episode_number"] = int(itunes_episode)
            except ValueError:
                pass
        if itunes_season:
            try:
                series["season_number"] = int(itunes_season)
            except ValueError:
                pass
        result["series"] = series

    if itunes_explicit:
        rating = "explicit" if itunes_explicit.lower() == "yes" else "general"
        result["content_rating"] = {"rating": rating}

    if podcast_transcript_el is not None:
        tr_url = podcast_transcript_el.get("url")
        tr_type = podcast_transcript_el.get("type")
        tr_lang = podcast_transcript_el.get("language")
        if tr_url and tr_type:
            transcript: dict[str, Any] = {"url": tr_url, "mime_type": tr_type}
            if tr_lang:
                transcript["language"] = tr_lang
            result["transcript"] = transcript

    result["source"] = {
        "type": source_type,
        "feed_url": feed_url,
    }
    if feed_title:
        result["source"]["feed_title"] = feed_title

    return result


def normalize_rss_feed(xml_text: str, feed_url: str, source_type: str = "rss") -> list[dict[str, Any]]:
    """Parse RSS XML and normalize all items. Returns list of MMSP items."""
    parser = ET.XMLParser()
    root = ET.fromstring(xml_text.encode(), parser=parser)
    channel = root.find("channel")
    if channel is None:
        return []
    feed_title_el = channel.find("title")
    feed_title = feed_title_el.text.strip() if feed_title_el is not None and feed_title_el.text else None
    items = channel.findall("item")
    return [normalize_rss_item(item, feed_url, feed_title, source_type) for item in items]


def normalize_atom_entry(
    entry_el: ET.Element,
    feed_url: str,
    feed_title: str | None,
    ns: str = ATOM_NS,
) -> dict[str, Any]:
    """Normalize a single Atom <entry> element to MMSP item schema."""

    def text(tag: str) -> str | None:
        el = entry_el.find(f"{{{ns}}}{tag}")
        return el.text.strip() if el is not None and el.text else None

    entry_id = text("id") or ""
    title = text("title") or ""
    summary = text("summary")
    content_el = entry_el.find(f"{{{ns}}}content")
    content = content_el.text.strip() if content_el is not None and content_el.text else None
    description = content or summary

    published = _parse_iso_date(text("published"))
    updated = _parse_iso_date(text("updated"))

    author_el = entry_el.find(f"{{{ns}}}author")
    author_name = None
    author_url = None
    if author_el is not None:
        name_el = author_el.find(f"{{{ns}}}name")
        uri_el = author_el.find(f"{{{ns}}}uri")
        author_name = name_el.text.strip() if name_el is not None and name_el.text else None
        author_url = uri_el.text.strip() if uri_el is not None and uri_el.text else None

    link_url = None
    enclosure_url = None
    enclosure_type = None
    enclosure_length = None

    for link_el in entry_el.findall(f"{{{ns}}}link"):
        rel = link_el.get("rel", "alternate")
        href = link_el.get("href", "")
        if rel == "alternate" and not link_url:
            link_url = href
        elif rel == "enclosure" and not enclosure_url:
            enclosure_url = href
            enclosure_type = link_el.get("type")
            length_str = link_el.get("length")
            if length_str:
                try:
                    enclosure_length = int(length_str)
                except ValueError:
                    pass

    categories = [
        el.get("term", "")
        for el in entry_el.findall(f"{{{ns}}}category")
        if el.get("term")
    ]

    media: list[dict] = []
    mime_type = None
    if enclosure_url:
        mime_type = enclosure_type
        enc_entry: dict[str, Any] = {
            "url": enclosure_url,
            "mime_type": enclosure_type or "application/octet-stream",
            "role": "primary",
        }
        if enclosure_length:
            enc_entry["size_bytes"] = enclosure_length
        media.append(enc_entry)

    item_type = _infer_type(mime_type)

    result: dict[str, Any] = {
        "id": entry_id or link_url or f"{feed_url}#unknown",
        "type": item_type,
        "title": title,
        "url": link_url or entry_id,
        "published": published or updated or datetime.now(timezone.utc).isoformat(),
    }

    if updated and updated != published:
        result["updated"] = updated
    if description:
        result["description"] = description
    if author_name:
        author: dict[str, Any] = {"name": author_name}
        if author_url:
            author["url"] = author_url
        result["authors"] = [author]
    if categories:
        result["tags"] = categories
    if media:
        result["media"] = media

    result["source"] = {
        "type": "atom",
        "feed_url": feed_url,
    }
    if feed_title:
        result["source"]["feed_title"] = feed_title

    return result


def normalize_atom_feed(xml_text: str, feed_url: str) -> list[dict[str, Any]]:
    """Parse Atom XML and normalize all entries. Returns list of MMSP items."""
    root = ET.fromstring(xml_text.encode())
    ns = ATOM_NS
    feed_title_el = root.find(f"{{{ns}}}title")
    feed_title = feed_title_el.text.strip() if feed_title_el is not None and feed_title_el.text else None
    entries = root.findall(f"{{{ns}}}entry")
    return [normalize_atom_entry(entry, feed_url, feed_title, ns) for entry in entries]

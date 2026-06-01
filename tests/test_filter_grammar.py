"""Tests for MMSP filter grammar (Appendix A)."""

import pytest
from tests.validators.filter import (
    FilterError,
    apply_filter,
    compile_filter,
    filter_items,
)


VIDEO_ITEM = {
    "id": "https://example.com/v1",
    "type": "video",
    "title": "Climate Documentary",
    "url": "https://example.com/v1",
    "published": "2026-06-01T10:00:00Z",
    "duration": 3600,
    "tags": ["climate", "documentary"],
    "language": "en",
    "authors": [{"name": "Alice"}],
    "content_rating": {"rating": "general"},
    "description": "A film about climate change",
}

AUDIO_ITEM = {
    "id": "https://example.com/a1",
    "type": "audio",
    "title": "Tech Podcast Episode 5",
    "url": "https://example.com/a1",
    "published": "2026-05-15T08:00:00Z",
    "duration": 1800,
    "tags": ["tech", "podcast"],
    "language": "en",
    "authors": [{"name": "Bob"}],
    "content_rating": {"rating": "general"},
    "description": "Discussion on software trends",
}

EXPLICIT_ITEM = {
    "id": "https://example.com/e1",
    "type": "audio",
    "title": "Explicit Show",
    "url": "https://example.com/e1",
    "published": "2026-04-01T00:00:00Z",
    "duration": 900,
    "tags": ["comedy"],
    "language": "fr",
    "authors": [{"name": "Charlie"}],
    "content_rating": {"rating": "explicit"},
    "description": "Comedy with adult content",
}

ALL_ITEMS = [VIDEO_ITEM, AUDIO_ITEM, EXPLICIT_ITEM]


class TestTypeFilter:
    def test_type_video_matches_video(self):
        assert apply_filter("type:video", VIDEO_ITEM)

    def test_type_video_no_match_audio(self):
        assert not apply_filter("type:video", AUDIO_ITEM)

    def test_type_audio_matches_audio(self):
        assert apply_filter("type:audio", AUDIO_ITEM)

    def test_type_article_no_match_video(self):
        assert not apply_filter("type:article", VIDEO_ITEM)

    @pytest.mark.parametrize("item_type", [
        "video", "audio", "article", "image", "short",
        "document", "gallery", "event", "release",
        "newsletter", "course", "livestream",
    ])
    def test_all_type_values_parseable(self, item_type):
        node = compile_filter(f"type:{item_type}")
        assert node is not None


class TestTagFilter:
    def test_tag_match(self):
        assert apply_filter('tag:"climate"', VIDEO_ITEM)

    def test_tag_no_match(self):
        assert not apply_filter('tag:"climate"', AUDIO_ITEM)

    def test_tag_unquoted(self):
        assert apply_filter("tag:tech", AUDIO_ITEM)

    def test_tag_absent_field(self):
        item = {**VIDEO_ITEM}
        del item["tags"]
        assert not apply_filter('tag:"climate"', item)


class TestAuthorFilter:
    def test_author_match_case_insensitive(self):
        assert apply_filter('author:"Alice"', VIDEO_ITEM)
        assert apply_filter('author:"alice"', VIDEO_ITEM)

    def test_author_no_match(self):
        assert not apply_filter('author:"Bob"', VIDEO_ITEM)

    def test_author_absent_field(self):
        item = {**VIDEO_ITEM}
        del item["authors"]
        assert not apply_filter('author:"Alice"', item)


class TestLangFilter:
    def test_lang_match(self):
        assert apply_filter("lang:en", VIDEO_ITEM)

    def test_lang_no_match(self):
        assert not apply_filter("lang:fr", VIDEO_ITEM)

    def test_lang_case_insensitive(self):
        assert apply_filter("lang:EN", VIDEO_ITEM)

    def test_lang_fr_match(self):
        assert apply_filter("lang:fr", EXPLICIT_ITEM)


class TestDurationFilter:
    def test_duration_gte_match(self):
        assert apply_filter("duration:>=3600", VIDEO_ITEM)

    def test_duration_gte_no_match(self):
        assert not apply_filter("duration:>=7200", VIDEO_ITEM)

    def test_duration_lte_match(self):
        assert apply_filter("duration:<=1800", AUDIO_ITEM)

    def test_duration_lte_no_match(self):
        assert not apply_filter("duration:<=900", AUDIO_ITEM)

    def test_duration_range_match(self):
        assert apply_filter("duration:[1000,5000]", VIDEO_ITEM)

    def test_duration_range_no_match(self):
        assert not apply_filter("duration:[5000,10000]", VIDEO_ITEM)

    def test_duration_absent_no_match(self):
        item = {**VIDEO_ITEM}
        del item["duration"]
        assert not apply_filter("duration:>=100", item)

    def test_duration_gte_non_numeric_returns_false(self):
        assert not apply_filter("duration:>=abc", VIDEO_ITEM)

    def test_duration_range_null_duration_returns_false(self):
        item = {**VIDEO_ITEM}
        del item["duration"]
        assert not apply_filter("duration:[0,7200]", item)

    def test_duration_range_bad_bounds_returns_false(self):
        assert not apply_filter("duration:[1T,2Z]", VIDEO_ITEM)


class TestPublishedFilter:
    def test_published_gte_match(self):
        assert apply_filter("published:>=2026-01-01T00:00:00Z", VIDEO_ITEM)

    def test_published_gte_no_match(self):
        assert not apply_filter("published:>=2027-01-01T00:00:00Z", VIDEO_ITEM)

    def test_published_lte_match(self):
        assert apply_filter("published:<=2026-12-31T23:59:59Z", VIDEO_ITEM)

    def test_published_range_match(self):
        assert apply_filter("published:[2026-01-01T00:00:00Z,2026-12-31T23:59:59Z]", VIDEO_ITEM)

    def test_published_range_no_match(self):
        assert not apply_filter("published:[2025-01-01T00:00:00Z,2025-12-31T23:59:59Z]", VIDEO_ITEM)

    def test_published_absent_no_match(self):
        item = {**VIDEO_ITEM}
        del item["published"]
        assert not apply_filter("published:>=2026-01-01T00:00:00Z", item)

    def test_published_gte_non_date_returns_false(self):
        assert not apply_filter("published:>=notadate", VIDEO_ITEM)

    def test_published_range_null_published_returns_false(self):
        item = {**VIDEO_ITEM}
        del item["published"]
        assert not apply_filter("published:[2026-01-01T00:00:00Z,2026-12-31T23:59:59Z]", item)

    def test_published_range_bad_bounds_returns_false(self):
        assert not apply_filter("published:[2026-13-01T00:00:00Z,2027-01-01T00:00:00Z]", VIDEO_ITEM)


class TestKeywordFilter:
    def test_keyword_in_title(self):
        assert apply_filter('keyword:"Climate"', VIDEO_ITEM)

    def test_keyword_in_description(self):
        assert apply_filter('keyword:"climate change"', VIDEO_ITEM)

    def test_keyword_case_insensitive(self):
        assert apply_filter('keyword:"CLIMATE"', VIDEO_ITEM)

    def test_keyword_no_match(self):
        assert not apply_filter('keyword:"blockchain"', VIDEO_ITEM)


class TestRatingFilter:
    def test_rating_general_match(self):
        assert apply_filter("rating:general", VIDEO_ITEM)

    def test_rating_explicit_match(self):
        assert apply_filter("rating:explicit", EXPLICIT_ITEM)

    def test_rating_no_match(self):
        assert not apply_filter("rating:explicit", VIDEO_ITEM)

    def test_rating_absent_no_match(self):
        item = {**VIDEO_ITEM}
        del item["content_rating"]
        assert not apply_filter("rating:general", item)


class TestBooleanOperators:
    def test_and_both_true(self):
        assert apply_filter("type:video AND lang:en", VIDEO_ITEM)

    def test_and_one_false(self):
        assert not apply_filter("type:video AND lang:fr", VIDEO_ITEM)

    def test_or_first_true(self):
        assert apply_filter("type:video OR type:audio", VIDEO_ITEM)

    def test_or_second_true(self):
        assert apply_filter("type:video OR type:audio", AUDIO_ITEM)

    def test_or_both_false(self):
        assert not apply_filter("type:image OR type:document", VIDEO_ITEM)

    def test_not_true_becomes_false(self):
        assert not apply_filter("NOT type:video", VIDEO_ITEM)

    def test_not_false_becomes_true(self):
        assert apply_filter("NOT type:video", AUDIO_ITEM)

    def test_complex_expression(self):
        expr = 'type:video AND duration:>=300 AND NOT tag:"sponsored"'
        assert apply_filter(expr, VIDEO_ITEM)

    def test_parentheses_grouping(self):
        expr = "(type:article OR type:newsletter) AND lang:en"
        article = {**VIDEO_ITEM, "type": "article"}
        assert apply_filter(expr, article)
        assert not apply_filter(expr, VIDEO_ITEM)

    def test_not_with_parentheses(self):
        expr = 'NOT (type:audio AND lang:fr)'
        assert apply_filter(expr, VIDEO_ITEM)
        assert not apply_filter(expr, EXPLICIT_ITEM)


class TestFilterItems:
    def test_filter_returns_matching_items(self):
        result = filter_items("type:video", ALL_ITEMS)
        assert len(result) == 1
        assert result[0]["type"] == "video"

    def test_filter_returns_multiple_matches(self):
        result = filter_items("type:audio", ALL_ITEMS)
        assert len(result) == 2

    def test_filter_returns_empty_on_no_match(self):
        result = filter_items("type:image", ALL_ITEMS)
        assert result == []

    def test_filter_returns_all_on_broad_match(self):
        result = filter_items("lang:en OR lang:fr", ALL_ITEMS)
        assert len(result) == 3


class TestFilterErrors:
    def test_missing_field_value_raises(self):
        with pytest.raises(FilterError):
            compile_filter("type:")

    def test_unknown_operator_raises(self):
        with pytest.raises(FilterError):
            compile_filter("type:video XOR type:audio")

    def test_unclosed_paren_raises(self):
        with pytest.raises(FilterError):
            compile_filter("(type:video AND lang:en")

    def test_empty_expression_raises(self):
        with pytest.raises(FilterError):
            compile_filter("")

    def test_value_starts_with_paren_raises(self):
        with pytest.raises(FilterError):
            compile_filter("type:(video)")

    def test_duration_missing_value_raises(self):
        with pytest.raises(FilterError):
            compile_filter("duration:")

    def test_duration_bad_token_raises(self):
        with pytest.raises(FilterError):
            compile_filter("duration:hello")

    def test_non_field_token_at_atom_position_raises(self):
        with pytest.raises(FilterError):
            compile_filter(")")

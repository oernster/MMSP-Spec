"""Feed manifest and item schema validation against MMSP JSON Schema."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Union

import jsonschema
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

# Known item types per Section 6.3; unknown types degrade to this value.
_FALLBACK_ITEM_TYPE = "article"

SCHEMA_DIR = Path(__file__).parent.parent.parent / "spec" / "schema"
FEED_SCHEMA_PATH = SCHEMA_DIR / "mmsp-feed.schema.json"
ITEM_SCHEMA_PATH = SCHEMA_DIR / "mmsp-item.schema.json"


def _load_schemas() -> tuple[dict, dict]:
    with FEED_SCHEMA_PATH.open() as f:
        feed_schema = json.load(f)
    with ITEM_SCHEMA_PATH.open() as f:
        item_schema = json.load(f)
    return feed_schema, item_schema


def _build_registry() -> Registry:
    feed_schema, item_schema = _load_schemas()
    registry = Registry().with_resources([
        (
            "https://mmsp.dev/schema/1.0/feed",
            Resource.from_contents(feed_schema),
        ),
        (
            "https://mmsp.dev/schema/1.0/item",
            Resource.from_contents(item_schema),
        ),
        (
            "mmsp-item.schema.json",
            Resource.from_contents(item_schema),
        ),
    ])
    return registry


def validate_feed(feed: dict) -> list[str]:
    """Validate a feed manifest. Returns list of error messages (empty = valid)."""
    feed_schema, _ = _load_schemas()
    registry = _build_registry()
    validator = Draft202012Validator(feed_schema, registry=registry)
    errors = sorted(validator.iter_errors(feed), key=lambda e: list(e.path))
    return [e.message for e in errors]


def validate_item(item: dict) -> list[str]:
    """Validate a single item object. Returns list of error messages (empty = valid)."""
    _, item_schema = _load_schemas()
    validator = Draft202012Validator(item_schema)
    errors = sorted(validator.iter_errors(item), key=lambda e: list(e.path))
    return [e.message for e in errors]


def is_valid_feed(feed: dict) -> bool:
    return len(validate_feed(feed)) == 0


def is_valid_item(item: dict) -> bool:
    return len(validate_item(item)) == 0


def validate_pagination_consistency(feed: dict) -> list[str]:
    """Check that has_more=True implies next_url is present (Section 5.5.1).

    Returns a list of error strings; empty means the feed is consistent.
    Operates on the co-constraint that is not expressible in JSON Schema alone.
    """
    pagination = feed.get("pagination")
    if pagination is None:
        return []
    if not pagination.get("has_more", False):
        return []
    if "next_url" not in feed:
        return [
            "pagination.has_more is true but next_url is absent"
            " (Section 5.5.1: when has_more is true the manifest MUST include next_url)"
        ]
    return []


def validate_item_tolerant(
    item: dict,
) -> tuple[Union[dict, None], list[str]]:
    """Apply Section 6.15 client tolerance rules to a single item.

    Returns (normalised_item_or_None, warnings):
    - None when a REQUIRED field is missing or has the wrong JSON type
      (the item must be skipped).
    - A (possibly mutated copy of the) item when it is processable, with any
      unknown type degraded to ``_FALLBACK_ITEM_TYPE`` and any malformed
      optional fields stripped.
    - warnings: a list of human-readable strings describing degradations
      applied; empty when the item was valid as-is.
    """
    _, item_schema = _load_schemas()
    required_fields: list[str] = item_schema.get("required", [])
    known_types: list[str] = (
        item_schema.get("properties", {})
        .get("type", {})
        .get("enum", [])
    )
    warnings: list[str] = []

    # Check required fields first; if any are missing, skip the item.
    for field in required_fields:
        if field not in item:
            return None, [f"item skipped: required field '{field}' is missing"]

    # Work on a shallow copy so we do not mutate the caller's dict.
    normalised = copy.copy(item)

    # Unknown type degrades to article (Section 6.15 / Section 6.3).
    if normalised.get("type") not in known_types:
        warnings.append(
            f"unknown type '{normalised['type']}' degraded to '{_FALLBACK_ITEM_TYPE}'"
            " (Section 6.15)"
        )
        normalised["type"] = _FALLBACK_ITEM_TYPE

    # Malformed optional fields: strip any optional field that fails schema
    # validation, rather than skipping the whole item.
    properties = item_schema.get("properties", {})
    defs = item_schema.get("$defs", {})
    for field, value in list(normalised.items()):
        if field in required_fields:
            continue
        if field not in properties:
            # Unknown member: forward-compat, keep it (Section 6.15).
            continue
        field_schema = properties[field]
        try:
            _validate_field(field_schema, value, defs)
        except jsonschema.ValidationError:
            warnings.append(
                f"optional field '{field}' is malformed and was stripped"
                " (Section 6.15)"
            )
            del normalised[field]

    return normalised, warnings


def _validate_field(field_schema: dict, value: object, defs: dict) -> None:
    """Validate a single value against a field sub-schema.

    Raises jsonschema.ValidationError when the value does not conform.
    Uses a minimal registry built from the item schema's own $defs so that
    $ref resolution works for nested objects (e.g. author, media).
    """
    # Build a temporary document embedding the defs so $ref works.
    wrapper_schema: dict = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": defs,
        **field_schema,
    }
    validator = Draft202012Validator(wrapper_schema)
    validator.validate(value)

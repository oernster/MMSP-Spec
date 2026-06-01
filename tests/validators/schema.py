"""Feed manifest and item schema validation against MMSP JSON Schema."""

import json
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

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

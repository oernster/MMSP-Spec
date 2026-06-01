"""MMSP filter grammar evaluator (Appendix A of the spec)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

ITEM_TYPES = {
    "video", "audio", "article", "image", "short",
    "document", "gallery", "event", "release",
    "newsletter", "course", "livestream",
}
RATING_VALUES = {"general", "teen", "mature", "explicit"}


class FilterError(ValueError):
    pass


class _Tokenizer:
    TOKEN_RE = re.compile(
        r'(?P<LPAREN>\()'
        r'|(?P<RPAREN>\))'
        r'|(?P<AND>\bAND\b)'
        r'|(?P<OR>\bOR\b)'
        r'|(?P<NOT>\bNOT\b)'
        r'|(?P<FIELD>type|tag|author|lang|duration|published|keyword|rating)'
        r'|(?P<COLON>:)'
        r'|(?P<QUOTED>"[^"]*")'
        r'|(?P<RANGE>\[[\d\-T:Z.+]+,[\d\-T:Z.+]+\])'
        r'|(?P<GTE>>=)'
        r'|(?P<LTE><=)'
        r'|(?P<TOKEN>[^\s\(\)"]+)'
        r'|(?P<WS>\s+)',
    )

    def __init__(self, text: str) -> None:
        self.tokens: list[tuple[str, str]] = []
        for m in self.TOKEN_RE.finditer(text):
            kind = m.lastgroup
            value = m.group()
            if kind == "WS":
                continue
            if kind is None:  # pragma: no cover
                raise FilterError(f"Unexpected character: {value!r}")
            self.tokens.append((kind, value))
        self.pos = 0

    def peek(self) -> tuple[str, str] | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self) -> tuple[str, str]:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, kind: str) -> str:
        tok = self.peek()
        if tok is None or tok[0] != kind:
            raise FilterError(f"Expected {kind}, got {tok!r}")
        return self.consume()[1]


class _Parser:
    def __init__(self, tokenizer: _Tokenizer) -> None:
        self.t = tokenizer

    def parse(self) -> dict:
        node = self._expr()
        if self.t.peek() is not None:
            raise FilterError(f"Unexpected token: {self.t.peek()!r}")
        return node

    def _expr(self) -> dict:
        left = self._term()
        while self.t.peek() and self.t.peek()[0] in ("AND", "OR"):
            op = self.t.consume()[0]
            right = self._term()
            left = {"op": op, "left": left, "right": right}
        return left

    def _term(self) -> dict:
        tok = self.t.peek()
        if tok and tok[0] == "NOT":
            self.t.consume()
            child = self._term()
            return {"op": "NOT", "child": child}
        if tok and tok[0] == "LPAREN":
            self.t.consume()
            node = self._expr()
            self.t.expect("RPAREN")
            return node
        return self._atom()

    def _atom(self) -> dict:
        tok = self.t.peek()
        if tok is None:
            raise FilterError("Unexpected end of filter expression")
        if tok[0] != "FIELD":
            raise FilterError(f"Expected field name, got {tok!r}")
        field = self.t.consume()[1]
        self.t.expect("COLON")
        value = self._value(field)
        return {"op": "FILTER", "field": field, "value": value}

    def _value(self, field: str) -> Any:
        tok = self.t.peek()
        if tok is None:
            raise FilterError(f"Missing value for field {field!r}")

        if field in ("duration",):
            return self._range_or_compare(numeric=True)
        if field == "published":
            return self._range_or_compare(numeric=False)

        if tok[0] == "QUOTED":
            return self.t.consume()[1][1:-1]
        if tok[0] == "TOKEN":
            return self.t.consume()[1]
        raise FilterError(f"Cannot parse value for field {field!r}: {tok!r}")

    def _range_or_compare(self, numeric: bool) -> dict:
        tok = self.t.peek()
        if tok is None:  # pragma: no cover
            raise FilterError("Missing range/compare value")
        if tok[0] == "RANGE":
            raw = self.t.consume()[1][1:-1]
            parts = raw.split(",", 1)
            return {"op": "range", "min": parts[0], "max": parts[1], "numeric": numeric}
        if tok[0] == "GTE":
            self.t.consume()
            val = self.t.consume()[1]
            return {"op": "gte", "value": val, "numeric": numeric}
        if tok[0] == "LTE":
            self.t.consume()
            val = self.t.consume()[1]
            return {"op": "lte", "value": val, "numeric": numeric}
        raise FilterError(f"Expected range or compare operator, got {tok!r}")


def _compare_numeric(item_val: int | None, op: str, cmp_val: str) -> bool:
    if item_val is None:
        return False
    try:
        n = int(cmp_val)
    except ValueError:
        return False
    if op == "gte":
        return item_val >= n
    return item_val <= n


def _compare_date(item_val: str | None, op: str, cmp_val: str) -> bool:
    if not item_val:
        return False
    try:
        item_dt = datetime.fromisoformat(item_val.replace("Z", "+00:00"))
        cmp_dt = datetime.fromisoformat(cmp_val.replace("Z", "+00:00"))
    except ValueError:
        return False
    if op == "gte":
        return item_dt >= cmp_dt
    return item_dt <= cmp_dt


def _evaluate_node(node: dict, item: dict[str, Any]) -> bool:
    op = node["op"]

    if op == "AND":
        return _evaluate_node(node["left"], item) and _evaluate_node(node["right"], item)
    if op == "OR":
        return _evaluate_node(node["left"], item) or _evaluate_node(node["right"], item)
    if op == "NOT":
        return not _evaluate_node(node["child"], item)

    field = node["field"]
    value = node["value"]

    if field == "type":
        return item.get("type") == value

    if field == "tag":
        return value in item.get("tags", [])

    if field == "author":
        return any(
            a.get("name", "").lower() == value.lower()
            for a in item.get("authors", [])
        )

    if field == "lang":
        return item.get("language", "").lower() == value.lower()

    if field == "rating":
        cr = item.get("content_rating", {})
        return cr.get("rating") == value

    if field == "keyword":
        needle = value.lower()
        return (
            needle in item.get("title", "").lower()
            or needle in item.get("description", "").lower()
        )

    if field == "duration":
        item_dur = item.get("duration")
        cmp_op = value["op"]
        if cmp_op == "range":
            if item_dur is None:
                return False
            try:
                return int(value["min"]) <= item_dur <= int(value["max"])
            except ValueError:
                return False
        return _compare_numeric(item_dur, cmp_op, value["value"])

    if field == "published":
        item_pub = item.get("published")
        cmp_op = value["op"]
        if cmp_op == "range":
            if not item_pub:
                return False
            try:
                item_dt = datetime.fromisoformat(item_pub.replace("Z", "+00:00"))
                min_dt = datetime.fromisoformat(value["min"].replace("Z", "+00:00"))
                max_dt = datetime.fromisoformat(value["max"].replace("Z", "+00:00"))
                return min_dt <= item_dt <= max_dt
            except ValueError:
                return False
        return _compare_date(item_pub, cmp_op, value["value"])

    return False  # pragma: no cover


def compile_filter(expression: str) -> dict:
    """Parse a filter expression string into an AST node."""
    tokenizer = _Tokenizer(expression)
    parser = _Parser(tokenizer)
    return parser.parse()


def apply_filter(expression: str, item: dict[str, Any]) -> bool:
    """Evaluate a filter expression against a single MMSP item. Returns True if item matches."""
    ast = compile_filter(expression)
    return _evaluate_node(ast, item)


def filter_items(expression: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter a list of MMSP items by a filter expression."""
    ast = compile_filter(expression)
    return [item for item in items if _evaluate_node(ast, item)]

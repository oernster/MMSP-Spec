#!/usr/bin/env python3
"""Propagate the draft identifier into the published site.

This specification has one identity: the draft identifier. It lives in exactly
one place, the name of the draft file under ``spec/``. Advancing to the next
draft is therefore a rename; everything else derives from it.

Two consumers cannot derive it for themselves. The Pages workflow derives the
injected page title at build time, so that one is handled. The static site
pages cannot compute anything at render time, so they carry delimited tokens
that this script refreshes. The draft file's own header block is normative
editorial text and is never rewritten here; it is checked instead, so a
mismatch fails loudly rather than shipping a page and a document that disagree.

Run it after renaming the draft file. It is idempotent: a second run against
an already-current tree reports that nothing changed and touches no file.

Exit codes: 0 when the tree is consistent, 1 when it is not.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SPEC_DIR = REPO_ROOT / "spec"
SITE_DIR = REPO_ROOT / "docs"

DRAFT_GLOB = "draft-mmsp-*.md"
SITE_SUFFIXES = (".md", ".html")

OPEN_TOKEN = "<!--DRAFT-->"
CLOSE_TOKEN = "<!--/DRAFT-->"
TOKEN_PATTERN = re.compile(
    re.escape(OPEN_TOKEN) + ".*?" + re.escape(CLOSE_TOKEN), re.DOTALL
)

SPEC_HEADER_PREFIX = "Internet-Draft:"


class DraftError(Exception):
    """The repository is not in a state this script can safely act on."""


def draft_identifier() -> tuple[str, Path]:
    """Return the draft identifier and the file it was derived from."""
    candidates = sorted(SPEC_DIR.glob(DRAFT_GLOB))
    if len(candidates) != 1:
        found = ", ".join(p.name for p in candidates) or "nothing"
        raise DraftError(
            f"Expected exactly one {SPEC_DIR.name}/{DRAFT_GLOB}, found {found}. "
            "The draft identifier is derived from that filename, so it cannot "
            "be resolved while more than one draft is present."
        )
    spec_path = candidates[0]
    return spec_path.stem, spec_path


def check_spec_header(draft: str, spec_path: Path) -> None:
    """Verify the draft file's own header agrees with its filename."""
    header_lines = [
        line.strip()
        for line in spec_path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith(SPEC_HEADER_PREFIX)
    ]
    if not header_lines:
        raise DraftError(
            f"{spec_path.name} has no '{SPEC_HEADER_PREFIX}' line, so its "
            "stated identity cannot be checked against its filename."
        )
    declared = header_lines[0][len(SPEC_HEADER_PREFIX) :].strip()
    if declared != draft:
        raise DraftError(
            f"{spec_path.name} declares '{SPEC_HEADER_PREFIX} {declared}' but "
            f"is named '{draft}'. Correct the header in the draft text; this "
            "script does not edit the specification."
        )


def stamp_site(draft: str) -> tuple[list[Path], int]:
    """Refresh every delimited token under the site directory.

    Returns the files changed and the total number of tokens seen.
    """
    replacement = f"{OPEN_TOKEN}{draft}{CLOSE_TOKEN}"
    changed: list[Path] = []
    tokens_seen = 0

    for path in sorted(SITE_DIR.rglob("*")):
        if not path.is_file() or path.suffix not in SITE_SUFFIXES:
            continue
        # newline="" on both sides: the file's own line endings survive a
        # stamp, so running this never shows up as a whole-file diff.
        with open(path, encoding="utf-8", newline="") as handle:
            original = handle.read()
        stamped, count = TOKEN_PATTERN.subn(replacement, original)
        if count == 0:
            continue
        tokens_seen += count
        if stamped != original:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(stamped)
            changed.append(path)

    return changed, tokens_seen


def main() -> int:
    try:
        draft, spec_path = draft_identifier()
        check_spec_header(draft, spec_path)
        changed, tokens_seen = stamp_site(draft)
        if tokens_seen == 0:
            raise DraftError(
                f"No {OPEN_TOKEN}...{CLOSE_TOKEN} tokens found under "
                f"{SITE_DIR.name}/. The site would silently keep whatever "
                "draft identifier is written into it, which is the failure "
                "this script exists to prevent."
            )
    except DraftError as exc:
        print(f"stamp_draft: {exc}", file=sys.stderr)
        return 1

    print(f"stamp_draft: identifier '{draft}' from {spec_path.name}")
    print(f"stamp_draft: {tokens_seen} token(s) checked under {SITE_DIR.name}/")
    if not changed:
        print("stamp_draft: nothing to change, the site is already current")
        return 0
    for path in changed:
        print(f"stamp_draft: updated {path.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

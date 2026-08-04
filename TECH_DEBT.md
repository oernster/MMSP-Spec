# MMSP: Technical Debt

A standing reference to the project's outstanding technical debt. It records what is still open, weighs whether each item is worth doing and gives the rationale. Scope is the whole repository: the specification text in `spec/`, the JSON Schemas, the conformance suite in `tests/`, the packaging metadata and the GitHub Pages site under `docs/`.

The framing here is different from an application's. MMSP is a specification offered to other implementers, so debt is weighed by what it costs *someone else* to adopt the protocol, not by what it costs to maintain the repository. An item that only inconveniences the author ranks below an item that blocks a third party.

---

**Read this repository together with Meridian.** Meridian is publicly billed as the reference implementation of MMSP, which changes how several items below should be weighed: the specification is not a document in isolation, it is a document with a working implementation beside it. Where the two repositories should be closing a loop and are not, that is recorded as debt here rather than there, because the specification owns the normative rules.

---

## 1. `pyproject.toml` names a build backend that does not exist

```toml
[build-system]
build-backend = "setuptools.backends.legacy:build"
```

There is no `setuptools.backends` module. Verified: importing it raises `ModuleNotFoundError`. Any `pip install .`, `pip install -e .` or `python -m build` in this repository fails at backend resolution before it reads a single line of the project. The valid values are `setuptools.build_meta` or `setuptools.build_meta:__legacy__`.

This is first because it is the one item that stops an implementer cold. Someone who reads the specification, decides to check their feed against the conformance suite and follows the obvious install path gets an error with no relationship to MMSP. One-word fix, highest value in the file.

## 2. The conformance suite is not consumable by anyone but this repository

`pyproject.toml` declares a distributable package called `mmsp-conformance`. The code it would distribute is `tests/validators/` (schema, normalizer, discovery, filter, poll), which is inside the test tree, and there is no `[tool.setuptools.packages.find]` block, so nothing is actually packaged.

The specification's strongest claim is that it is checkable: `README.md` and the site both lead with the conformance suite mirroring the normative sections. That claim only pays off if a publisher building an MMSP feed can run the validators against their own output. Today they would have to clone the repo and import out of `tests/`.

The fix is a genuine package split: move the five validator modules to `mmsp_conformance/` at root, leave `tests/` importing them exactly as it does now, add the `packages.find` block and let the coverage gate keep pointing at the validators under their new path. The suite is small enough that this is an afternoon and it converts the repository's central claim from true-for-the-author into true-for-everyone.

**The reference implementation is the first customer.** Meridian implements MMSP independently in `meridian/infrastructure/fetching/parser/mfeed_parser.py`, depends on nothing from this repository and shares no test with it. So the normative rules exist twice, in two languages of expression, and nothing checks that the two agree. Meridian could drift from the specification it is the reference for and both repositories would stay green.

That is the real prize behind this item, and it is bigger than distribution convenience. Once the validators are an importable package, Meridian's own suite can assert its parser output against them, and the claim "Meridian proves the rules against real feeds" becomes mechanically true rather than a statement about intent. Meridian also hardcodes `_USER_AGENT = "MMSP/1.0"`, a third copy of the protocol version that item 4 should absorb.

## 3. The conformance suite never runs in CI

The only workflow is `.github/workflows/pages.yml`, which injects the spec into the site and deploys Pages. Nothing runs `pytest`.

So the suite that proves the specification is internally consistent is verified only when the author remembers to run it locally, while the site that publishes the specification is rebuilt automatically on every push to `main`. The publishing path is automated and the correctness path is not, which is exactly the wrong way round for a standards document.

Adding a second workflow that runs `pytest` on push and on pull request is small and turns the 100% validator gate into something a contributor's PR is held to rather than something the author holds themselves to.

## 4. The draft number is encoded in a filename and repeated in four places

The spec lives at `spec/draft-mmsp-00.md`, names itself `draft-mmsp-00` in its own header, and the Pages workflow hardcodes `"MMSP Specification: draft-mmsp-00"` in a `printf` inside the YAML. Separately, the protocol version (`MUST be "1.0"`) is asserted in the spec text, encoded in both JSON Schemas and checked by `test_versioning.py`, and the package version in `pyproject.toml` reads `0.1.0` and relates to none of them.

Three independent version identities (draft number, protocol version, package version) with no single source and no stamping step. Advancing to `draft-mmsp-01` means a file rename, an edit inside the file, an edit to the workflow YAML and a check of every cross-reference, done by hand, with the site silently continuing to publish the old title if the YAML is missed.

The proportionate fix is the pattern the rest of the portfolio uses: a `VERSION` file holding the protocol version, the draft number derived from the filename by the workflow rather than typed into it, and `pyproject.toml` made dynamic. This is worth doing before `draft-01`, not after.

## 5. `tests/test_rss_normalization.py` is 512 lines

Over the 400-line cap, and the largest file in the repository by a wide margin. Nothing in the suite measures module size, so it is not reported anywhere.

RSS normalisation is genuinely the most rule-dense part of the spec, so the length reflects real content rather than sprawl. It still wants splitting along the seams the spec itself provides (element mapping, date handling, enclosure and media translation, tolerance rules), because a 512-line test file is where a missing normative case hides.

## 6. One unexplained broad exception in the normalizer

`tests/validators/normalizer.py:28` catches bare `except Exception` with no comment and no `# noqa`. In a validator, swallowing an exception means a malformed input is reported as something other than the failure it is, and a conformance validator that silently degrades is worse than one that crashes. Give it the specific exception type and a comment naming what it tolerates and why the spec permits that tolerance.

## 7. IANA considerations are drafted but nothing is registered

The spec reserves a media type and defines optional parameters (Section 11 area, the `version` parameter). Nothing has been submitted. `IETF-PLAN.md` records the intent.

This is not a code defect and it is not urgent. It is recorded because it is the single largest open item in the project's own stated direction, and because the media type is referenced normatively by the schemas and by Meridian, the reference implementation. Until registration happens, every implementer is using a provisional identifier.

---

## Looks like debt, not worth touching

- The validators living under `tests/` *as a directory choice* is addressed by item 2, but the fact that they are imported by the tests they serve is correct and should survive the move.
- `tests/validators/normalizer.py` at 361 lines is under the cap and clear of the danger band. It needs nothing.
- The Jekyll site under `docs/`. Jekyll is the right tool for a static spec site on GitHub Pages and is the one place in the portfolio where a site generator is the correct answer.
- The two example feeds (`minimal-feed.json`, `full-feed.json`) duplicating structure that the schemas already describe. Examples are for humans and are worth the duplication.
- The workflow's `printf` heredoc that prepends Jekyll front matter to the raw spec markdown. It is a shell incantation inside YAML and it is ugly, but keeping `spec/draft-mmsp-00.md` free of site-specific front matter is worth it: the spec file stays a clean Internet-Draft.

## Not debt (do not "fix" these)

These look like candidates but are correct as they stand; changing them would regress or add cost for nothing.

- **The coverage gate scoped to `tests/validators` rather than the whole repository.** The validators are the product; the tests are the specification restated. Gating the validators at 100% is the right scope and matches how the rest of the portfolio scopes partial gates.
- **`additionalProperties: true` in the JSON Schemas.** It looks permissive. It is the deliberate forward-compatibility rule the spec's versioning section depends on, and tightening it would break the extension model.
- **One test module per normative section** (`test_pagination`, `test_poll_semantics`, `test_discovery`, `test_filter_grammar`, `test_series_episodes`, `test_authenticity`, `test_media_types`, `test_item_tolerance`, `test_versioning`). The one-to-one mapping between spec sections and test modules is the whole point; consolidating them would destroy the traceability.
- **The 300-second poll floor and the absence of push.** These are the specification's central trade-off, argued for in the spec text and on the site. They are design, not debt.
- **Apache-2.0 rather than the portfolio's usual GPL-3.0.** Correct for a specification intended for third-party implementation.

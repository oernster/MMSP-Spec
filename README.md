# <img width="128" height="128" alt="MMSP logo" src="https://github.com/user-attachments/assets/e8116858-fa7e-43c9-9600-3ce5264757e0" /> MMSP - MultiMedia Subscription Protocol

[Read the specification](https://ernster.dev/MMSP-Spec/)

MMSP is a community specification for multimedia feed subscription: a
JSON-based, pull-only protocol defined as a semantic superset of RSS 2.0 and
Atom, with calm consumption as a first-class design constraint.

This repository is the specification itself. It holds the draft text, the
normative JSON Schemas, worked example feeds and a conformance suite that
mirrors the draft section by section. There is no application here.

## Who this is for

- Publishers who want their video, audio, articles, images, releases and
  events carried by one feed format rather than several namespace overlays.
- Client authors building a reader, plus anyone who needs to know precisely
  what a conformant client must do when a feed is slow, paginated, relocated,
  rate-limited or partially malformed.
- Implementers of RSS or Atom tooling who want a defined normalization path
  into a single item schema.

## Who this is not for

- Anyone looking for an installable library or a feed reader. Nothing here is
  packaged, published or importable; see [Meridian](https://ernster.dev/meridian/)
  for the reference client.
- Anyone who needs server push. MMSP has no push mechanism and will not gain
  one; that is the point of the design, not an omission.
- Anyone expecting an IETF work product. The `draft-NN` naming borrows IETF
  convention as a familiar label only. MMSP has not been submitted to the
  IETF and is not affiliated with or endorsed by it.

## Key properties

- JSON format, media type `application/mmsp+json`
- 12 first-class item types: video, audio, article, image, short, document,
  gallery, event, release, newsletter, course, livestream
- Semantic superset of RSS 2.0 and Atom, with normalization defined in the
  draft rather than left to each client
- Pull-only: no push, no notifications, 300 second minimum poll interval
- Conditional GET, 429 back-off, cursor pagination and partial-feed tolerance
  are normative, so behaviour under load and failure is predictable
- ABNF filter grammar so subscribers can narrow a feed at the protocol level
- Discovery via `/.well-known/mmsp.json` or an HTML `<link rel="alternate">`
- User-Agent `MMSP/<version>`, optionally followed by a single client product
  token; never anything that identifies the subscriber or the installation
- All URLs MUST use HTTPS

## What is in the repository

| Path | Contents |
|---|---|
| `spec/draft-mmsp-00.md` | The specification text. This is the product. |
| `spec/schema/mmsp-feed.schema.json` | Normative JSON Schema for a feed manifest |
| `spec/schema/mmsp-item.schema.json` | Normative JSON Schema for a single item |
| `spec/examples/` | Minimal and full worked feeds |
| `tests/` | Conformance suite, one module per area of the draft |
| `tests/validators/` | The validators the suite exercises, kept deliberately small |
| `docs/` | Source of the published site |
| `IETF-PLAN.md` | The route from community draft to submission |

## Source types

| Type | Acquires from |
|---|---|
| `mfeed` | Native MMSP manifest |
| `rss` | Any RSS 2.0 feed |
| `atom` | Any Atom 1.0 feed |
| `podcast` | RSS plus podcast namespace extensions |
| `platform` | Platform-specific adapter |

## Stack

| Concern | Choice |
|---|---|
| Specification text | Markdown, RFC 2119 normative language |
| Schemas | JSON Schema draft 2020-12 |
| Conformance suite | Python 3.13, pytest |
| Schema validation | `jsonschema` with `referencing` |
| RSS and Atom parsing | `feedparser` and `lxml` |
| HTTP behaviour under test | `responses` and `pytest-httpserver` |
| Coverage gate | `pytest-cov`, 100% of `tests/validators` |
| Site | Jekyll on GitHub Pages, minima theme |
| CI | GitHub Actions |

## Running the conformance suite

```bash
pip install -r requirements.txt
pytest
```

`pyproject.toml` configures the run and nothing else: there is no
`[build-system]` and no `[project]` table, because a specification is not a
distributable. Dependencies live in `requirements.txt` and are installed
directly.

The default options in `pyproject.toml` fail the run below 100% branch
coverage of `tests/validators`, so `pytest` on its own is the whole gate.
Coverage target is 100% of normative statements in the draft.

## Build

There is nothing to build. The one generated artefact is the site: the
`Deploy GitHub Pages` workflow prepends Jekyll front matter to
`spec/draft-mmsp-00.md`, writes the result to `docs/spec.md` and publishes
`docs/`. That deploy is gated on the conformance suite, so the specification
is never published while the suite proving it internally consistent is
failing. The `Conformance` workflow runs the same suite on every pull
request, because a community specification takes changes by pull request and
a proposed change to the draft text must be checked before it reaches `main`.

Run `python stamp_draft.py` after renaming the draft file: it propagates the
draft identifier into the site and reports any place that has drifted. See
`IETF-PLAN.md` for the full procedure.

## Project documentation

- [IETF-PLAN.md](IETF-PLAN.md): the route from community draft to submission;
  also the procedure for advancing the draft number.

## Author

Oliver Ernster

## Licence

Apache License 2.0. See [LICENSE](LICENSE).

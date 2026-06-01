# MMSP — MultiMedia Subscription Protocol

A community specification for multimedia feed subscription, designed as a
semantic superset of RSS 2.0 and Atom. MMSP is a pull-only, JSON-based
protocol with calm consumption as a first-class design constraint.

## Specification

- **Spec:** `spec/draft-ernster-mmsp-00.md`
- **JSON Schema (feed):** `spec/schema/mmsp-feed.schema.json`
- **JSON Schema (item):** `spec/schema/mmsp-item.schema.json`
- **Examples:** `spec/examples/`
- **IETF plan:** `IETF-PLAN.md`

## Key Properties

- JSON format, MIME type `application/mmsp+json`
- 12 first-class item types: video, audio, article, image, short, document, gallery, event, release, newsletter, course, livestream
- Semantic superset of RSS 2.0 and Atom (normalization defined in spec)
- Pull-only: no push, no notifications, 300s minimum poll interval
- User-Agent: `MMSP/1.0` only
- All URLs MUST use HTTPS
- Discovery via `/.well-known/mmsp.json` or HTML `<link rel="alternate">`

## Conformance Test Suite

```bash
pip install -r requirements.txt
pytest
```

Coverage target: 100% of normative spec statements.

## Source Types

| Type | Acquires from |
|---|---|
| `mfeed` | Native MMSP manifest |
| `rss` | Any RSS 2.0 feed |
| `atom` | Any Atom 1.0 feed |
| `podcast` | RSS + iTunes/Podcast Index namespace |
| `platform` | Platform-specific adapter |

## Author

Oliver Ernster

## License

Spec text: CC BY 4.0. Code: MIT.

---
layout: home
title: MMSP
---

# MMSP — MultiMedia Subscription Protocol

A JSON-based protocol for subscribing to and consuming multimedia content feeds.
MMSP is a pull-only semantic superset of RSS 2.0 and Atom, built around calm consumption as a first-class design constraint.

**Status:** Community Specification (Pre-IETF) — `draft-mmsp-00`

---

## Key Properties

- **Format:** JSON, MIME type `application/mmsp+json`
- **Transport:** HTTPS only, pull-only, no server push
- **Poll floor:** 300 seconds minimum
- **12 item types:** video, audio, article, image, short, document, gallery, event, release, newsletter, course, livestream
- **Backwards compatible:** any RSS 2.0 or Atom feed normalizes to MMSP item schema
- **Discovery:** `/.well-known/mmsp.json` or HTML `<link rel="alternate">`
- **User-Agent:** `MMSP/1.0`

---

## Resources

- [Full Specification](/MMSP-Spec/spec/)
- [JSON Schema (feed)](https://github.com/oernster/MMSP-Spec/blob/main/spec/schema/mmsp-feed.schema.json)
- [JSON Schema (item)](https://github.com/oernster/MMSP-Spec/blob/main/spec/schema/mmsp-item.schema.json)
- [Example feeds](https://github.com/oernster/MMSP-Spec/tree/main/spec/examples)
- [Conformance test suite](https://github.com/oernster/MMSP-Spec/tree/main/tests)
- [GitHub repository](https://github.com/oernster/MMSP-Spec)

---

## License

[Apache License 2.0](https://github.com/oernster/MMSP-Spec/blob/main/LICENSE)

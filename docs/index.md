---
layout: default
title: MMSP: MultiMedia Subscription Protocol
description: Open community specification for multimedia feed subscription. JSON-based, pull-only, calm consumption. Semantic superset of RSS 2.0 and Atom.
keywords: MMSP, multimedia subscription protocol, RSS, Atom, JSON feed, podcast feed, open standard, IETF, feed reader, calm consumption, multimedia syndication
---

# MMSP: MultiMedia Subscription Protocol

A JSON-based protocol for subscribing to and consuming multimedia content feeds.
MMSP is a pull-only semantic superset of RSS 2.0 and Atom, built around calm consumption as a first-class design constraint.

**Status:** Community Specification, `draft-mmsp-00`

MMSP is an independent, open community specification. The `draft-NN` versioning
borrows IETF Internet-Draft naming as a familiar convention only: **MMSP has not
been submitted to the IETF, is not an IETF work product and is not affiliated
with or endorsed by the IETF, the IESG or ISOC.** "Pre-IETF" describes an
intention to potentially pursue that track in future, not current standing.

---

## Why this exists

RSS answered the early web's question: how do I follow a site's articles without visiting it?
The current web poses a broader one. A publisher's output now spans video, audio, articles,
images, releases and events across disconnected platforms and every push-based alternative
monetises attention. RSS 2.0 and Atom model one content form well; everything else arrives
through namespace extensions, platform APIs or not at all.

MMSP is the answer as a protocol rather than a platform: JSON-based, pull-only and defined as a
semantic superset of RSS 2.0 and Atom. Twelve first-class item types carry the multimedia model,
formal JSON Schemas make a publisher's output mechanically verifiable, discovery works from a
bare domain via `/.well-known/mmsp.json` and calm consumption is enforced at the wire level (no
push, a 300 second poll floor) instead of being left as a cultural norm.

The project is run like a standards effort: a versioned specification with RFC-style normative
language, worked examples, a conformance suite targeting every normative statement and a working
reference client, [Meridian](https://ernster.dev/meridian/), that proves the normalization rules
against real feeds. The spec keeps the client honest; the client keeps the spec real.

Full reasoning at [crankthecode.com](https://www.crankthecode.com/posts/mmsp).

---

## Why MMSP and not RSS, Atom or JSON Feed?

JSON Feed already proved the appetite for JSON-native syndication but stops
at the document: it is a *file format*. MMSP specifies the *protocol* around the
format and is built on four commitments those formats do not make:

- **Calm consumption as a design constraint.** At the wire level MMSP is
  pull-only with no server-push mechanism and mandates a 300-second minimum poll
  interval; both are normative, not advisory. How a client surfaces new items,
  including whether it notifies, is a presentation concern addressed by the
  optional Calm Consumption Profile (Section 4.1).
- **Polling discipline.** Conditional GET (ETag / Last-Modified), 429 back-off,
  cursor pagination and partial-feed tolerance are part of the spec, so every
  conformant client behaves predictably under load and failure.
- **Filter expressions.** A defined ABNF filter grammar (Appendix A) lets
  subscribers narrow a feed at the protocol level, not as a client-specific
  feature bolted on top.
- **A real item taxonomy.** 12 first-class item types instead of one generic
  "entry", with unknown types degrading gracefully rather than breaking clients.

Any RSS 2.0 or Atom feed normalizes cleanly into the MMSP item schema, so
adoption costs nothing on the consumption side.

---

## Key Properties

- **Format:** JSON, MIME type `application/mmsp+json`
- **Transport:** HTTPS only, pull-only, no server push
- **Poll floor:** 300 seconds minimum
- **12 item types:** video, audio, article, image, short, document, gallery, event, release, newsletter, course, livestream
- **Backwards compatible:** any RSS 2.0 or Atom feed normalizes to MMSP item schema
- **Forward compatible:** versioned `MAJOR.MINOR`; unknown item types and fields degrade gracefully instead of breaking clients
- **Robust polling:** conditional GET (ETag / Last-Modified), 429 back-off, cursor pagination and partial-feed tolerance for malformed items
- **Discovery:** `/.well-known/mmsp.json` or HTML `<link rel="alternate">`
- **User-Agent:** `MMSP/<version>`, optionally a client token (e.g. `MMSP/1.0 Meridian/2.3`); never subscriber- or install-identifying

---

## Resources

- [Full Specification]({{ "/spec/" | relative_url }})
- [JSON Schema (feed)](https://github.com/oernster/MMSP-Spec/blob/main/spec/schema/mmsp-feed.schema.json)
- [JSON Schema (item)](https://github.com/oernster/MMSP-Spec/blob/main/spec/schema/mmsp-item.schema.json)
- [Example feeds](https://github.com/oernster/MMSP-Spec/tree/main/spec/examples)
- [Conformance test suite](https://github.com/oernster/MMSP-Spec/tree/main/tests)
- [GitHub repository](https://github.com/oernster/MMSP-Spec)

---

## License

[Apache License 2.0](https://github.com/oernster/MMSP-Spec/blob/main/LICENSE)

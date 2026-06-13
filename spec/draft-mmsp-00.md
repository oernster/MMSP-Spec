# The MultiMedia Subscription Protocol (MMSP)

```
Internet-Draft: draft-mmsp-00
Date:           June 2026
Author:         MMSP Community
Status:         Community Specification
License:        Apache-2.0
```

> **Status note.** MMSP is an independent, open community specification. The
> `draft-NN` versioning borrows IETF Internet-Draft naming as a familiar
> convention only: MMSP has not been submitted to the IETF, is not an IETF work
> product and is not affiliated with or endorsed by the IETF, the IESG or
> ISOC. "Pre-IETF" describes an intention to potentially pursue that track in
> future, not current standing.

---

## Abstract

This document specifies the MultiMedia Subscription Protocol (MMSP), a
JSON-based protocol for subscribing to and consuming multimedia content
feeds. MMSP is a semantic superset of RSS 2.0 and Atom, extending feed
syndication to cover rich multimedia content including video, audio,
articles, images, short-form content, documents, galleries, events,
software releases, newsletters, courses, and livestreams.

MMSP is designed around a "calm consumption" model. At the wire level it
guarantees this through two enforceable properties: it is pull-only, with
no server-push mechanism, and it mandates a minimum poll interval.
Presentation behaviour, such as whether a client raises notifications, is
out of scope for the base protocol; clients that wish to commit to calm
behaviour MAY conform to the optional Calm Consumption Profile (Section
4.1). Subscribers consume feeds when they choose to, not when publishers
demand attention.

---

## 1. Introduction

RSS and Atom have served as the foundation of web content syndication
since the early 2000s. However, both protocols were designed primarily
for text-based content and have accumulated multimedia support only
through informal extensions and namespace overlays.

MMSP addresses three gaps:

1. **Multimedia-first schema**: item types, media attachments, chapters,
   transcripts, captions, and quality variants are first-class fields,
   not extension namespaces.

2. **Cross-platform normalization**: content from any declared source
   type (RSS, Atom, podcast feeds) normalizes into a single item schema,
   allowing unified consumption regardless of origin format.

3. **Calm consumption**: at the wire level the protocol guarantees
   pull-only behaviour and a minimum poll interval, and defines no
   server-push mechanism. How a client surfaces new items to a subscriber,
   including whether it notifies, is a client-presentation concern outside
   the base protocol; clients MAY additionally conform to the optional
   Calm Consumption Profile (Section 4.1).

### 1.1 Motivation

The proliferation of multimedia content platforms, combined with the
notification fatigue caused by push-heavy consumption models, creates
a need for a protocol that:

- Treats video, audio, and other media as first-class content types
- Enables subscription to content from any source with a declared feed
- Returns control of consumption timing to the subscriber

### 1.2 Design Principles

- **Pull-only**: MMSP servers MUST NOT push content to clients. Clients
  poll at their discretion, subject to poll interval constraints.
- **Declared sources only**: MMSP supports only sources that explicitly
  declare themselves consumable via a supported source type.
- **Credential-free spec**: authentication and platform API credentials
  are implementation concerns, not protocol concerns.
- **Privacy by default**: the protocol minimises information disclosed
  to publishers during polling.
- **Backwards compatible**: any RSS 2.0 or Atom feed is consumable as
  an MMSP source via normalization.

---

## 2. Conventions and Definitions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all
capitals, as shown here.

---

## 3. Terminology

**Feed**: A machine-readable document conforming to this specification
that describes a collection of items published by a source.

**Feed Manifest**: The top-level MMSP document served at a feed URL,
containing feed metadata and an array of items.

**Item**: A single piece of content within a feed, with a defined type
and associated metadata.

**Source**: A content origin from which an MMSP client derives a feed,
declared via a source type and configuration.

**Client**: A conforming implementation that polls feeds, normalizes
source types, and presents content to a subscriber.

**Publisher**: An entity that serves a feed manifest at a stable URL.

**Subscriber**: A human or system that consumes content via an MMSP
client.

**Poll**: An HTTP GET request issued by a client to retrieve the current
state of a feed.

**Normalization**: The process of converting a non-native source type
(RSS, Atom) into an MMSP item representation.

**Calm consumption**: The pattern of consuming feed content at
subscriber-chosen times, with no server-push or notification mechanism.

---

## 4. Protocol Overview

MMSP is a stateless HTTP-based protocol. A publisher serves a feed
manifest as a JSON document. A client polls the manifest URL periodically,
respecting the declared poll interval, and presents new items to the
subscriber when the subscriber chooses to view them.

```
Publisher                         Client                    Subscriber
    |                               |                            |
    |  GET /.well-known/mmsp.json   |                            |
    |  or feed URL                  |                            |
    |<------------------------------|                            |
    |  200 OK + Feed Manifest JSON  |                            |
    |------------------------------>|                            |
    |                               |  (stores new items)        |
    |                               |                            |
    |                               |  subscriber opens reader   |
    |                               |<---------------------------|
    |                               |  presents new items        |
    |                               |--------------------------->|
```

The base protocol defines no notification mechanism and places no
normative requirement on how a client surfaces newly polled items to a
subscriber; this is a client-presentation concern. Clients that wish to
make an explicit commitment to calm behaviour MAY conform to the optional
Calm Consumption Profile defined below.

### 4.1 Calm Consumption Profile (Optional)

The Calm Consumption Profile is an optional conformance profile that a
client MAY claim. It exists so that "calm consumption" can be a concrete,
self-certified commitment without placing unobservable requirements on the
wire protocol.

A client claiming conformance to the Calm Consumption Profile:

- MUST NOT raise interruptive notifications (system push notifications,
  sounds, vibration, or badge counts) as a result of polling a feed.
- MUST surface newly polled items only in response to an explicit
  subscriber action, such as opening or refreshing the reader interface.
- MAY display a passive, non-interruptive unread indicator within its own
  interface.

Because notification behaviour is not observable on the wire, conformance
to this profile cannot be verified by a publisher or by an on-the-wire
conformance test; it is a commitment a client makes to its subscribers,
not a property a publisher can test. This separation is deliberate: the
base protocol carries only requirements that are observable and
enforceable on the wire, and the calm-presentation contract lives here, as
a profile, rather than as an untestable MUST in the core.

---

## 5. Feed Manifest

A feed manifest is a JSON object served over HTTPS. The media type is
`application/mmsp+json`.

### 5.1 Required Fields

| Field | Type | Description |
|---|---|---|
| `mmsp` | string | Protocol version, of the form `MAJOR.MINOR`. MUST be `"1.0"` for this revision. Version semantics are defined in Section 5.7. |
| `id` | string (URI) | Globally unique, permanent identifier for the feed. MUST be a URI. MUST NOT change after publication. |
| `title` | string | Human-readable feed title. |
| `feed_url` | string (HTTPS URL) | Canonical URL of this feed manifest. MUST use HTTPS. |
| `items` | array | Array of item objects. MAY be empty. |

### 5.2 Optional Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | Human-readable description of the feed. |
| `icon` | string (HTTPS URL) | Feed icon image. MUST use HTTPS if present. |
| `language` | string | Primary language of feed content. BCP 47 language tag. |
| `authors` | array of Author | Feed-level authors. |
| `tags` | array of string | Feed-level tags. |
| `contact` | string (email) | Publisher contact address. |
| `poll` | Poll object | Poll semantics declaration. See Section 8. |
| `capabilities` | array of string | Declared capabilities. See Section 5.4. |
| `moved_to` | string (HTTPS URL) | Permanent relocation URL. See Section 8.4. |
| `deprecated` | Deprecation object | Feed deprecation notice. See Section 8.5. |
| `bundle_id` | string (URI) | Groups related feeds from the same publisher. |
| `pagination` | Pagination object | Cursor-based pagination. See Section 5.5. |
| `next_url` | string (HTTPS URL) | URL of next page of items (older). |

### 5.3 Author Object

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | REQUIRED | Display name. |
| `url` | string (HTTPS URL) | OPTIONAL | Author profile URL. |
| `avatar` | string (HTTPS URL) | OPTIONAL | Author avatar image URL. |

### 5.4 Capabilities

The `capabilities` field declares optional protocol features supported
by this feed. Defined capability strings:

| Capability | Meaning |
|---|---|
| `"conditional-get"` | Feed supports ETag and Last-Modified headers. |
| `"pagination"` | Feed supports cursor-based pagination via `next_url`. |
| `"filter-metadata"` | Items contain machine-readable filter metadata. |

### 5.5 Pagination Object

A feed manifest returns the newest items inline. Older items are retrieved
by walking pages backwards in time. A publisher that offers historical
items beyond the first page SHOULD include a `pagination` object and a
`next_url`.

| Field | Type | Required | Description |
|---|---|---|---|
| `cursor` | string | REQUIRED | Opaque, server-generated cursor identifying this page boundary. Clients MUST treat it as opaque and MUST NOT parse or construct it. |
| `has_more` | boolean | REQUIRED | Whether older items exist beyond this page. |

#### 5.5.1 Walking Pages

- When `has_more` is `true`, the manifest MUST include `next_url`. The
  client retrieves the next (older) page by issuing a poll to `next_url`.
- When `has_more` is `false`, the client has reached the end of the
  available history and MUST NOT request further pages.
- A client performing a backfill walk MUST follow `next_url` values only;
  it MUST NOT synthesise page URLs or numeric offsets of its own.

#### 5.5.2 Consistency Under Mutation

Feeds change between page fetches as new items are published. To prevent
items being skipped or duplicated during a backfill walk, the `cursor`
MUST anchor a page to a stable ordering position, defined as descending
`published` with item `id` as a tie-breaker, rather than to a numeric
offset. Items published at the head of the feed after a walk begins MUST
NOT alter the set of items reachable from an already-issued `cursor`. A
publisher MUST keep a cursor resolvable for at least the feed's
`ttl_seconds` (Section 8.1) and SHOULD keep it resolvable for
substantially longer. A client that receives an error or an unresolvable
cursor MUST restart the walk from the feed manifest rather than guessing a
position.

#### 5.5.3 Termination and Loop Safety

A client MUST bound a backfill walk. It MUST stop when `has_more` is
`false`, when `next_url` is absent, or when it observes a `cursor` value it
has already seen during the current walk. A client SHOULD additionally
impose an implementation-defined maximum page count per walk so that a
misbehaving or hostile publisher cannot drive an unbounded fetch loop.

### 5.6 Feed Validation and Error Handling

A client MUST validate a feed manifest before use and MUST fail safely when
validation does not pass. A failed poll MUST NOT discard previously stored,
valid items for that feed.

- **Malformed JSON.** If the response body does not parse as JSON, the
  client MUST treat the poll as failed, MUST retain the last known-good
  state of the feed, and SHOULD surface a fetch error for that feed to the
  subscriber. The client MUST apply back-off (Section 8.3) rather than
  immediately re-polling.
- **Wrong media type.** If the response is not `application/mmsp+json`,
  and is not a recognised RSS/Atom/podcast source being normalized, the
  client SHOULD treat the poll as failed.
- **Missing or mistyped required fields.** If any field REQUIRED by
  Section 5.1 is absent, or is present with the wrong JSON type, the
  manifest is invalid; the client MUST reject the manifest as a whole and
  retain the last known-good state.
- **Unknown manifest members.** A client MUST ignore any feed-level member
  it does not recognise, rather than rejecting the manifest. This is the
  manifest-level counterpart of the item rule in Section 6.15, and is what
  lets a later minor version (Section 5.7) add feed-level fields safely.
- **Unsupported version.** Version handling is defined in Section 5.7.
- **Invalid individual items.** A client MUST NOT discard an entire,
  otherwise-valid feed solely because individual items are invalid.
  Item-level handling is defined in Section 6.15.

### 5.7 Protocol Versioning

The `mmsp` field carries a `MAJOR.MINOR` version string.

- **Minor versions are additive and backward-compatible.** A new MINOR
  version within the same MAJOR version MUST only add optional fields,
  item types, or capabilities. It MUST NOT remove a field, change the type
  or meaning of an existing field, or make an existing optional field
  required.
- **Clients accept any minor version of a major version they implement.**
  A client that implements major version N MUST accept any feed whose
  version is `N.x`, regardless of the value of `x`, and MUST ignore
  members it does not recognise (Sections 5.6 and 6.15). This is what makes
  adding fields in a later minor version safe.
- **Major versions may break compatibility.** A change to MAJOR signals a
  break. A client that does not implement a feed's MAJOR version MUST NOT
  process the manifest as if it understood it; it MUST reject the feed and
  SHOULD inform the subscriber that the feed requires a newer client.
- **Publishers MUST NOT introduce breaking changes within a major
  version.** Any change that would break a conforming `N.x` client
  requires incrementing MAJOR.

---

## 6. Item Schema

Each entry in the `items` array is an item object.

### 6.1 Required Fields

| Field | Type | Description |
|---|---|---|
| `id` | string (URI) | Globally unique, permanent item identifier. MUST be a URI. |
| `type` | string | Item type. See Section 6.3. |
| `title` | string | Human-readable item title. |
| `url` | string (HTTPS URL) | Canonical URL of the content. MUST use HTTPS. |
| `published` | string (ISO 8601) | Publication datetime in ISO 8601 format with timezone. |

### 6.2 Optional Fields

| Field | Type | Description |
|---|---|---|
| `updated` | string (ISO 8601) | Last modification datetime. |
| `description` | string | Item description or summary. HTML is permitted; clients MUST sanitize before rendering. |
| `authors` | array of Author | Item-level authors. Overrides feed-level authors. |
| `tags` | array of string | Item tags. |
| `language` | string | BCP 47 language tag for this item. Overrides feed-level language. |
| `duration` | integer | Duration in seconds. Applies to `video`, `audio`, `short`, `livestream` types. |
| `media` | array of Media | Media attachments. See Section 6.4. |
| `thumbnail` | array of Thumbnail | Thumbnail images at multiple resolutions. |
| `chapters` | array of Chapter | Timestamp markers. See Section 6.5. |
| `transcript` | Transcript object | Text transcript. See Section 6.6. |
| `captions` | array of Caption | Subtitle/caption files. See Section 6.7. |
| `series` | Series object | Series membership. See Section 6.8. |
| `content_rating` | ContentRating object | Content classification. See Section 6.9. |
| `license` | string (SPDX or URI) | Content license. SPDX identifier or URI. |
| `geo_restriction` | GeoRestriction object | Regional availability. See Section 6.10. |
| `paywall` | Paywall object | Paywall declaration. See Section 6.11. |
| `live_status` | string | One of: `upcoming`, `live`, `ended`, `archived`. Only valid for `livestream` type. |
| `scheduled_start` | string (ISO 8601) | Scheduled start time. Only valid for `event` and `livestream` types. |
| `expires` | string (ISO 8601) | Datetime after which content may be unavailable. |
| `canonical_url` | string (HTTPS URL) | Canonical URL for deduplication across sources. See Section 6.12. |
| `source` | Source object | Origin feed metadata (populated during normalization). |
| `original` | object | Preserved source fields (populated during normalization). |
| `preview_url` | string (HTTPS URL) | Short teaser/preview media URL. |

### 6.3 Item Types

The `type` field MUST contain one of the following values:

| Type | Description |
|---|---|
| `video` | Long-form video content. |
| `audio` | Audio content (non-podcast episodes handled by podcast source type). |
| `article` | Text article or blog post. |
| `image` | Single image. |
| `short` | Short-form video (typically under 60 seconds). |
| `document` | PDF, ebook, whitepaper, or other document. |
| `gallery` | Collection of images as a single item. |
| `event` | Scheduled future occurrence. |
| `release` | Software release, package version, or changelog entry. |
| `newsletter` | Newsletter edition published as a feed item. |
| `course` | Structured educational content, optionally with ordered episodes. |
| `livestream` | Live or previously-live video/audio stream. |

Clients MUST treat unrecognized type values as `"article"` for
display purposes and MUST NOT reject items with unrecognized types.

### 6.4 Media Object

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string (HTTPS URL) | REQUIRED | Media file URL. MUST use HTTPS. |
| `mime_type` | string | REQUIRED | MIME type of the media file. |
| `size_bytes` | integer | OPTIONAL | File size in bytes. |
| `duration` | integer | OPTIONAL | Duration in seconds. |
| `width` | integer | OPTIONAL | Width in pixels (video/image). |
| `height` | integer | OPTIONAL | Height in pixels (video/image). |
| `bitrate_kbps` | integer | OPTIONAL | Bitrate in kilobits per second. |
| `role` | string | OPTIONAL | One of: `primary`, `alternate`, `preview`. Default: `primary`. |
| `quality_label` | string | OPTIONAL | Human-readable quality descriptor (e.g., `"1080p"`, `"320kbps"`). |

Multiple media entries with different `mime_type` or `quality_label`
values represent quality variants of the same content.

### 6.5 Thumbnail Object

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string (HTTPS URL) | REQUIRED | Thumbnail image URL. MUST use HTTPS. |
| `width` | integer | OPTIONAL | Width in pixels. |
| `height` | integer | OPTIONAL | Height in pixels. |

### 6.6 Chapter Object

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | REQUIRED | Chapter title. |
| `start_seconds` | integer | REQUIRED | Chapter start time in seconds from item start. |
| `end_seconds` | integer | OPTIONAL | Chapter end time in seconds. |
| `image_url` | string (HTTPS URL) | OPTIONAL | Chapter thumbnail. |

### 6.7 Transcript Object

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string (HTTPS URL) | REQUIRED | Transcript document URL. MUST use HTTPS. |
| `mime_type` | string | REQUIRED | MIME type. Typically `text/plain` or `text/html`. |
| `language` | string | OPTIONAL | BCP 47 language tag. |

### 6.8 Caption Object

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string (HTTPS URL) | REQUIRED | Caption file URL. MUST use HTTPS. |
| `mime_type` | string | REQUIRED | MIME type. Typically `text/vtt` or `application/ttml+xml`. |
| `language` | string | REQUIRED | BCP 47 language tag. |
| `label` | string | OPTIONAL | Human-readable label. |

### 6.9 Series Object

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string (URI) | REQUIRED | Globally unique series identifier. |
| `title` | string | REQUIRED | Series title. |
| `episode_number` | integer | OPTIONAL | Episode number within the series. |
| `season_number` | integer | OPTIONAL | Season number. |
| `total_episodes` | integer | OPTIONAL | Total episodes in the season, if known. |

### 6.10 ContentRating Object

| Field | Type | Required | Description |
|---|---|---|---|
| `rating` | string | REQUIRED | Rating value. Defined values: `general`, `teen`, `mature`, `explicit`. |
| `system` | string | OPTIONAL | Rating system identifier (e.g., `mpaa`, `bbfc`). |
| `descriptors` | array of string | OPTIONAL | Content descriptors (e.g., `"violence"`, `"language"`). |
| `spoiler` | boolean | OPTIONAL | Whether this item contains spoilers. Default: `false`. |

### 6.11 GeoRestriction Object

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | REQUIRED | One of: `allowlist`, `blocklist`. |
| `regions` | array of string | REQUIRED | ISO 3166-1 alpha-2 country codes. |

### 6.12 Paywall Object

| Field | Type | Required | Description |
|---|---|---|---|
| `paywalled` | boolean | REQUIRED | Whether full content requires payment. |
| `preview_available` | boolean | OPTIONAL | Whether a free preview is available. |

### 6.13 Source Object (Normalization Metadata)

Populated by clients during normalization of non-native source types.

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | REQUIRED | Source type that produced this item. |
| `feed_url` | string | REQUIRED | URL of the source feed. |
| `feed_title` | string | OPTIONAL | Title of the source feed. |

### 6.14 Canonical URL and Deduplication

When the same content appears in multiple sources (e.g., a video
available on both a primary platform and a mirror), `canonical_url`
SHOULD be set to the authoritative URL for the content.

Clients that aggregate multiple sources SHOULD use `canonical_url` to
deduplicate items. Two items with identical `canonical_url` values
SHOULD be treated as the same piece of content.

### 6.15 Item Validation and Partial-Feed Tolerance

Real feeds contain occasional malformed items. A client MUST be tolerant
of bad items without discarding the whole feed.

- **Skip, do not reject.** If an item is missing a field REQUIRED by
  Section 6.1, or carries a REQUIRED field of the wrong JSON type, the
  client MUST skip that single item and MUST continue processing the
  remaining items in the feed.
- **Unknown members MUST be ignored.** A client MUST ignore any object
  member it does not recognise, at every level of the item schema, rather
  than rejecting the item. This is the forward-compatibility rule that
  lets later minor versions (Section 5.7) and future extensions add fields
  without breaking existing clients.
- **Unknown item types degrade.** As defined in Section 6.3, an
  unrecognised `type` value MUST be treated as `article` for display and
  MUST NOT cause the item to be rejected.
- **Invalid optional fields degrade.** If an OPTIONAL field is present but
  malformed, the client SHOULD ignore that field and render the item
  without it, rather than skipping the item.
- **Observability.** A client SHOULD record how many items it skipped in a
  given poll so the condition is diagnosable, and SHOULD NOT silently hide
  a feed that yielded zero valid items from an otherwise successful fetch.

---

## 7. Source Types

MMSP defines five source types. A source type determines how a client
acquires and normalizes a feed.

### 7.1 mfeed (Native MMSP)

A native MMSP feed manifest. No normalization required.

```json
{
  "source": {
    "type": "mfeed",
    "url": "https://example.com/.well-known/mmsp.json"
  }
}
```

### 7.2 rss (RSS 2.0)

An RSS 2.0 feed. Clients MUST normalize RSS items to MMSP item schema
per Appendix B.

```json
{
  "source": {
    "type": "rss",
    "url": "https://example.com/feed.xml"
  }
}
```

### 7.3 atom (Atom 1.0)

An Atom 1.0 feed. Clients MUST normalize Atom entries to MMSP item
schema per Appendix C.

```json
{
  "source": {
    "type": "atom",
    "url": "https://example.com/atom.xml"
  }
}
```

### 7.4 podcast (RSS + Podcast Namespace)

An RSS feed using the iTunes or Podcast Index namespace for podcast
metadata. Clients MUST normalize per Appendix B and SHOULD additionally
map podcast-specific fields per Appendix D.

```json
{
  "source": {
    "type": "podcast",
    "url": "https://example.com/podcast.xml"
  }
}
```

### 7.5 platform (Platform Adapter)

A platform-specific feed source. The `platform_id` identifies the
platform adapter. Platform adapters are defined outside this
specification. Clients that do not support a given `platform_id` SHOULD
fall back to `rss` if an `rss_fallback_url` is provided.

```json
{
  "source": {
    "type": "platform",
    "platform_id": "example-platform",
    "config": {},
    "rss_fallback_url": "https://example.com/feed.xml"
  }
}
```

---

## 8. Poll Semantics

### 8.1 Minimum Poll Interval

MMSP enforces a calm consumption model through mandatory poll interval
constraints.

The `poll` object within a feed manifest declares polling parameters:

| Field | Type | Required | Description |
|---|---|---|---|
| `min_interval_seconds` | integer | OPTIONAL | Minimum seconds between polls. Default: 300. |
| `recommended_interval_seconds` | integer | OPTIONAL | Recommended polling interval. |
| `ttl_seconds` | integer | OPTIONAL | Time-to-live for cached items in seconds. |

Normative constraints:

- Clients MUST NOT poll a feed more frequently than the declared
  `min_interval_seconds`. If not declared, the default minimum is
  **300 seconds (5 minutes)**.
- The `min_interval_seconds` value MUST NOT be set below 300 by
  publishers. Clients MUST enforce a floor of 300 seconds regardless
  of the declared value.
- Notification and presentation behaviour is not governed by this section.
  Clients that commit to suppressing interruptive notifications do so under
  the optional Calm Consumption Profile (Section 4.1).

### 8.2 Conditional GET

Clients SHOULD use HTTP conditional GET to avoid unnecessary data
transfer:

- Clients SHOULD store the `ETag` response header value from each
  successful poll and send it as `If-None-Match` on subsequent polls.
- Clients SHOULD store the `Last-Modified` response header value and
  send it as `If-Modified-Since` on subsequent polls.
- When a server responds with `304 Not Modified`, clients MUST treat
  this as a successful poll with no new items and MUST update their
  last-poll timestamp.

### 8.3 Rate Limiting

- When a server responds with `429 Too Many Requests`, clients MUST
  cease polling for at least the duration specified in the `Retry-After`
  response header.
- If no `Retry-After` header is present, clients MUST apply an
  exponential back-off starting from the current `min_interval_seconds`.
- Clients MUST NOT retry a `429`-responding feed more frequently than
  the calculated back-off interval.

### 8.4 Feed Relocation

When a feed permanently moves to a new URL, the publisher SHOULD serve
the old URL with a `301 Moved Permanently` HTTP response pointing to
the new URL. Additionally, the publisher MAY set `moved_to` in the
feed manifest:

```json
{
  "moved_to": "https://new-location.example.com/.well-known/mmsp.json"
}
```

Clients that encounter `moved_to` MUST update stored subscription URLs
to the new location and MUST NOT continue polling the old URL.

### 8.5 Feed Deprecation

A publisher announcing feed shutdown SHOULD set the `deprecated` field:

```json
{
  "deprecated": {
    "reason": "This feed is shutting down.",
    "sunset_date": "2027-01-01T00:00:00Z"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | string | OPTIONAL | Human-readable deprecation reason. |
| `sunset_date` | string (ISO 8601) | OPTIONAL | Date after which the feed will cease to be available. |

Clients SHOULD surface deprecation notices to subscribers.

---

## 9. Discovery

### 9.1 Well-Known URI

Publishers SHOULD serve the MMSP feed manifest at:

```
https://{host}/.well-known/mmsp.json
```

This path is registered per [RFC8615].

### 9.2 HTML Link Discovery

Publishers SHOULD include a link element in the HTML `<head>` of their
website:

```html
<link rel="alternate"
      type="application/mmsp+json"
      title="Feed Title"
      href="https://example.com/.well-known/mmsp.json">
```

### 9.3 Discovery Priority

Clients performing autodiscovery for a given URL SHOULD attempt
discovery in the following order:

1. `/.well-known/mmsp.json` on the same host
2. HTML `<link rel="alternate" type="application/mmsp+json">` element
3. HTML `<link rel="alternate" type="application/rss+xml">` element (RSS fallback)
4. HTML `<link rel="alternate" type="application/atom+xml">` element (Atom fallback)

---

## 10. RSS and Atom Normalization

When consuming `rss`, `atom`, or `podcast` source types, clients MUST
normalize source items into MMSP item objects.

### 10.1 General Normalization Rules

- Fields present in the source MUST be mapped per Appendix B or C.
- Fields absent in the source MUST be omitted from the normalized item
  (not set to null).
- The normalized item's `source` field MUST be populated with the
  source feed's type and URL.
- The original source fields SHOULD be preserved in the `original` field.

### 10.2 Type Inference

When normalizing from RSS or Atom (which have no item type field),
clients SHOULD infer `type` as follows:

1. If an enclosure or media attachment has a video MIME type: `video`
2. If an enclosure or media attachment has an audio MIME type: `audio`
3. If an enclosure or media attachment has an image MIME type: `image`
4. Otherwise: `article`

For `podcast` source type, all items SHOULD be inferred as `audio`
unless overridden by media metadata.

---

## 11. HTTP Requirements

- All MMSP feed URLs MUST use HTTPS (TLS 1.2 or later). Clients MUST
  reject non-HTTPS feed URLs.
- Source URLs of type `rss`, `atom`, and `podcast` MUST use HTTPS.
  Clients SHOULD warn and MAY reject non-HTTPS source URLs.
- Clients MUST send a User-Agent header on all polls whose first token
  identifies the protocol and version: `MMSP/<version>` (for this
  revision, `MMSP/1.0`).
- Clients SHOULD append a single product token identifying the client
  software and its version, separated by a space, for example:
  `User-Agent: MMSP/1.0 Meridian/2.3`. This lets a publisher's operator
  distinguish, rate-limit, and contact the author of a specific
  implementation that is behaving badly, which a uniform User-Agent makes
  impossible.
- To preserve subscriber privacy, the User-Agent MUST NOT carry any
  information that identifies the subscriber or the individual
  installation: no operating-system build string, no device identifier,
  no per-install or per-user token, and nothing derived from subscriber
  data. Permitted identification is limited to the coarse
  {software name, software version} pair, which is shared by every user of
  that client and therefore adds negligible per-subscriber entropy.
- Clients MUST NOT vary the User-Agent per feed, per poll, or per
  subscriber.

---

## 12. Security Considerations

### 12.1 HTTPS Enforcement

All feed URLs and media URLs in a conforming MMSP implementation MUST
use HTTPS. This prevents content injection via man-in-the-middle attacks
on unencrypted channels.

### 12.2 Content Sanitization

Item `description` fields may contain HTML. Clients MUST sanitize
HTML content before rendering to prevent cross-site scripting (XSS)
attacks. Clients MUST NOT execute JavaScript from feed content.

### 12.3 URL Validation

Clients MUST validate all URLs received in feed manifests before
fetching. Clients MUST reject URLs with non-HTTPS schemes. Clients
implementing server-side feed fetching MUST apply SSRF (Server-Side
Request Forgery) mitigations including blocking private IP ranges and
loopback addresses.

### 12.4 XML Parsing (RSS/Atom Normalization)

When parsing RSS or Atom XML for normalization, clients MUST disable
external entity expansion to prevent XML External Entity (XXE) attacks.
Clients MUST enforce a maximum document size limit to prevent
denial-of-service via large XML documents (billion laughs attack).

### 12.5 Feed Authenticity (Known Limitation)

This revision of MMSP defines no mechanism for verifying that a feed served
at a given URL is authoritative. This is a known limitation, to be
addressed in a future revision, rather than a settled position.

HTTPS authenticates the transport to a host; it does not establish that the
host is the legitimate publisher of a feed. An attacker who takes over a
domain, a hosting account, or a network path (for example via DNS or BGP
hijacking, or a lapsed and re-registered domain) can serve a feed under a
previously trusted URL with a fully valid certificate. Well-known URI
registration and certificate validation raise the bar but do not close this
gap: a subscriber cannot today distinguish a genuine publisher from an
attacker who has acquired control of the publisher's URL.

Clients and subscribers MUST NOT treat the mere presence of a feed at an
HTTPS URL as proof of publisher authenticity.

A future revision is expected to define an OPTIONAL content-authenticity
mechanism: a detached `signature` over a canonical serialisation of the
feed or item, verified against a publisher key, most likely building on
HTTP Message Signatures [RFC9421]. To keep that path open without a
breaking change, the member name `signature` is reserved at both feed and
item level by this document; clients MUST ignore it where present (Section
6.15) until a future revision assigns it meaning, and publishers MUST NOT
use `signature` for any other purpose.

---

## 13. Privacy Considerations

### 13.1 Information Disclosed During Polling

When a client polls a feed, the publisher observes:

- The client's IP address
- The poll timestamp and frequency
- The User-Agent string (`MMSP/1.0`)
- Conditional GET headers (ETag, If-Modified-Since)

This information may allow publishers to infer subscription patterns.
Clients SHOULD document this behaviour to subscribers.

### 13.2 IP Address Correlation

A subscriber who polls multiple feeds from the same IP address may be
identified across unrelated publishers through IP correlation. Clients
SHOULD support operation through a proxy or VPN for subscribers who
require stronger privacy guarantees. This is an implementation
concern, not a protocol requirement.

### 13.3 Subscription List Privacy

A subscriber's subscription list constitutes a record of their
interests. Clients SHOULD store subscription lists locally and MUST NOT
transmit subscription lists to remote services without explicit
subscriber consent.

---

## 14. IANA Considerations

### 14.1 Media Type Registration

This document registers the following media type:

- Type name: application
- Subtype name: mmsp+json
- Required parameters: none
- Optional parameters: version (version string, e.g., "1.0")
- Encoding considerations: UTF-8
- Security considerations: See Section 12
- Published specification: This document
- Author: MMSP Community

### 14.2 Well-Known URI Registration

This document registers the following Well-Known URI per [RFC8615]:

- URI suffix: mmsp.json
- Change controller: IETF
- Specification document: This document

---

## References

### Normative References

- [RFC2119] Bradner, S., "Key words for use in RFCs to Indicate
  Requirement Levels", BCP 14, RFC 2119, March 1997.
- [RFC8174] Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC
  2119 Key Words", BCP 14, RFC 8174, May 2017.
- [RFC8615] Nottingham, M., "Well-Known Uniform Resource Identifiers
  (URIs)", RFC 8615, May 2019.
- [RFC9110] Fielding, R. et al., "HTTP Semantics", RFC 9110, June 2022.

### Informative References

- RSS 2.0 Specification, Harvard Berkman Center, 2003.
- Atom Syndication Format, RFC 4287, December 2005.
- JSON Feed Version 1.1, Brent Simmons and Manton Reece, 2020.
- [RFC9421] Backman, A., Richer, J., Sporny, M., "HTTP Message
  Signatures", RFC 9421, February 2024.

---

## Appendix A: Filter Grammar

Clients supporting subscription-level filtering SHOULD implement
the following filter grammar. Filters are evaluated client-side against
normalized item objects.

### A.1 Grammar (ABNF)

```
filter       = expr
expr         = term *(SP bool-op SP term)
bool-op      = "AND" / "OR"
term         = ["NOT" SP] atom / "(" expr ")"
atom         = type-filter / tag-filter / author-filter /
               lang-filter / duration-filter / date-filter /
               keyword-filter / rating-filter
type-filter  = "type:" item-type
tag-filter   = "tag:" string-val
author-filter = "author:" string-val
lang-filter  = "lang:" language-code
duration-filter = "duration:" range-expr
date-filter  = "published:" date-range-expr
keyword-filter = "keyword:" string-val
rating-filter = "rating:" rating-val
range-expr   = ">=" number / "<=" number /
               "[" number "," number "]"
date-range-expr = ">=" iso8601 / "<=" iso8601 /
                  "[" iso8601 "," iso8601 "]"
string-val   = DQUOTE *(%x20-21 / %x23-7E) DQUOTE
item-type    = "video" / "audio" / "article" / "image" /
               "short" / "document" / "gallery" / "event" /
               "release" / "newsletter" / "course" / "livestream"
rating-val   = "general" / "teen" / "mature" / "explicit"
language-code = 2*8ALPHA *("-" 2*8(ALPHA / DIGIT))
```

### A.2 Examples

```
type:video AND duration:>=300
```
Match video items 5 minutes or longer.

```
NOT tag:"sponsored" AND (type:article OR type:newsletter)
```
Match articles and newsletters without the "sponsored" tag.

```
keyword:"climate" AND lang:en AND published:>=2026-01-01T00:00:00Z
```
Match English items containing "climate" published in 2026 or later.

---

## Appendix B: RSS 2.0 Field Mapping

| RSS 2.0 Field | MMSP Item Field | Notes |
|---|---|---|
| `guid` | `id` | Use as-is if URI; otherwise prepend feed URL as namespace |
| `title` | `title` | Direct mapping |
| `link` | `url` | Direct mapping |
| `description` | `description` | May contain HTML |
| `pubDate` | `published` | Convert to ISO 8601 |
| `author` | `authors[0].name` | RSS author is email; extract name if present |
| `category` | `tags[]` | Multiple category elements map to array |
| `enclosure[@url]` | `media[0].url` | |
| `enclosure[@type]` | `media[0].mime_type` | |
| `enclosure[@length]` | `media[0].size_bytes` | |
| `media:content[@url]` | `media[].url` | |
| `media:content[@type]` | `media[].mime_type` | |
| `media:content[@duration]` | `media[].duration` | |
| `media:thumbnail[@url]` | `thumbnail[0].url` | |
| `media:thumbnail[@width]` | `thumbnail[0].width` | |
| `media:thumbnail[@height]` | `thumbnail[0].height` | |
| `channel/title` | `source.feed_title` | |
| `channel/link` | `source.feed_url` | |

---

## Appendix C: Atom Field Mapping

| Atom Field | MMSP Item Field | Notes |
|---|---|---|
| `id` | `id` | Direct mapping |
| `title` | `title` | Extract text content |
| `link[@rel="alternate"]` | `url` | |
| `summary` or `content` | `description` | Prefer `content` if both present |
| `published` | `published` | Direct ISO 8601 mapping |
| `updated` | `updated` | Direct ISO 8601 mapping |
| `author/name` | `authors[0].name` | |
| `author/uri` | `authors[0].url` | |
| `category[@term]` | `tags[]` | Multiple entries map to array |
| `link[@rel="enclosure"]` | `media[0].url` | |
| `link[@rel="enclosure"][@type]` | `media[0].mime_type` | |
| `link[@rel="enclosure"][@length]` | `media[0].size_bytes` | |
| `feed/title` | `source.feed_title` | |
| `feed/id` | `source.feed_url` | |

---

## Appendix D: Podcast Namespace Mapping

| Podcast Namespace Field | MMSP Field | Notes |
|---|---|---|
| `itunes:duration` | `duration` | Convert HH:MM:SS to seconds |
| `itunes:episode` | `series.episode_number` | |
| `itunes:season` | `series.season_number` | |
| `itunes:title` | `title` | Override RSS title if present |
| `itunes:image[@href]` | `thumbnail[0].url` | |
| `itunes:explicit` | `content_rating.rating` | `"yes"` -> `"explicit"`, `"no"` -> `"general"` |
| `podcast:transcript[@url]` | `transcript.url` | |
| `podcast:transcript[@type]` | `transcript.mime_type` | |
| `podcast:transcript[@language]` | `transcript.language` | |
| `podcast:chapters[@url]` | Fetch and map to `chapters[]` | |
| `podcast:person[@role="host"]` | `authors[0].name` | |

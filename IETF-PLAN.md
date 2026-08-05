# MMSP IETF Submission Plan

## Overview

MMSP (MultiMedia Subscription Protocol) follows a two-phase publication strategy:
Phase 1 is community specification for adoption; Phase 2 is IETF standardisation.
This document tracks the milestones and process requirements for each phase.

---

## Phase 1: Community Specification (Current)

**Goal:** Establish the specification, achieve two or more independent
implementations and build an implementer community before IETF submission.

### Milestones

| # | Milestone | Status |
|---|---|---|
| 1.1 | Publish the draft text to GitHub | Done |
| 1.2 | Publish JSON Schema for feed manifest and item | Done |
| 1.3 | Publish Python conformance test suite | Done |
| 1.4 | Publish reference validator implementation | In progress |
| 1.5 | Publish public website | Done |
| 1.6 | Announce on relevant mailing lists (rss-public, atom-syntax, ietf-announce) | Pending |
| 1.7 | Achieve two independent client implementations | Pending |
| 1.8 | Achieve one independent server/publisher implementation | Pending |
| 1.9 | Conduct interoperability testing between implementations | Pending |
| 1.10 | Publish a revised draft incorporating implementation feedback | Pending |

Notes on the milestones above:

- 1.3 is done in a stronger sense than "the files exist". The suite runs on
  every pull request and it gates deployment of the site, so the published
  draft text cannot get ahead of the tests that check it.
- 1.4 is partial. The validators the suite exercises live in
  `tests/validators/` and are deliberately small; they exist to prove the
  normative statements, not to be depended on. A validator published as a
  usable artefact in its own right is still outstanding. Meridian is the
  reference client and covers the consumption side.
- 1.5 is done via GitHub Pages rather than the standalone domain originally
  sketched here. The `mmsp.dev` URLs that remain in the JSON Schemas are
  schema `$id` identifiers, not addresses anyone is expected to fetch; they
  stay put: changing a published schema identifier is a breaking change.

### Deliverables

- The draft file under `spec/`: full specification text
- `spec/schema/`: JSON Schema files for validation
- `tests/`: Python conformance test suite
- `spec/examples/`: Annotated feed examples
- `.github/workflows/`: conformance on every pull request; a Pages deploy
  gated on that same suite

---

## Advancing the Draft Number

The draft identifier is the closest thing this repository has to a version;
advancing it is an editorial act, not a mechanical bump. It is deliberately
not automated end to end. What is automated is everything downstream of the
decision, so that the decision is the only manual step.

The single source of truth is the **name of the draft file** under `spec/`.

To advance the draft:

1. Rename `spec/draft-mmsp-NN.md` to the next number.
2. Edit the `Internet-Draft:` line in that file's header block to match.
   This is normative editorial text inside the specification and no script
   rewrites it.
3. Run `python stamp_draft.py` from the repository root. It derives the
   identifier from the filename, refuses to continue if the header from step 2
   disagrees with it and refreshes the delimited tokens in the site source
   under `docs/`. It is idempotent and prints every file it touched.
4. Update any prose in `README.md` or this file that names the draft by number
   rather than describing it.

The Pages workflow needs no change. It derives the injected page title from
the same filename at build time, so the published specification page always
carries the draft number of the file it was built from.

The protocol version is a separate thing and is **not** advanced by this
procedure. `mmsp` is normatively `"1.0"` for this revision, asserted in the
draft text and enforced by both JSON Schemas and the versioning tests.
Changing it changes the protocol; Section 5.7 governs when that is
permitted.

---

## Phase 2: IETF Internet-Draft Submission

**Goal:** Submit MMSP as an IETF Individual Submission Internet-Draft, seek
Working Group adoption and progress to RFC.

### Prerequisites (must complete before submission)

- [ ] Two or more independent interoperable implementations
- [ ] Documented interoperability test results
- [ ] Spec text converted to xml2rfc XML format (I-D toolchain)
- [ ] IANA considerations section reviewed by IANA
- [ ] Security review by at least one external reviewer
- [ ] Privacy review completed

### IETF Process Steps

#### Step 1: Individual Internet-Draft Submission

1. Convert spec from Markdown to xml2rfc format using `kramdown-rfc` or `mmark`
2. Validate with `idnits` tool (checks formatting, boilerplate, references)
3. Submit to IETF Datatracker as Individual Submission:
   `https://datatracker.ietf.org/submit/`
4. Draft name: whatever the file under `spec/` is called at the time. See
   Advancing the Draft Number above.
5. Expiry: Internet-Drafts expire after 6 months. Refresh or progress.

#### Step 2: Identify Relevant Working Group

MMSP most likely fits one of:

| Working Group | Area | Why |
|---|---|---|
| **DISPATCH** | ART | First stop for new ART proposals; recommends WG home |
| **HTTPAPI** | ART | HTTP-based API conventions |
| **MEDIAMAN** | ART | Media types, MIME registration |

Recommended path: present to DISPATCH first. They will recommend the appropriate WG
or form a new one if adoption is sufficient.

#### Step 3: IETF Meeting Presentation

- Request agenda time at DISPATCH WG session (IETF meeting or interim)
- Prepare 10-15 minute presentation covering: motivation, design decisions,
  existing implementations, open issues
- Post slides to IETF Datatracker before the meeting

#### Step 4: Working Group Adoption

- WG chairs call for adoption of the draft as a WG document
- Requires WG consensus (not unanimous but rough consensus)
- Draft renamed: `draft-ietf-<wgname>-mmsp-00`

#### Step 5: WG Development

- Address WG review comments
- Iterate through numbered drafts (01, 02, ...)
- Resolve all open issues in GitHub/tracker
- WGLC (Working Group Last Call) when WG judges the draft ready

#### Step 6: IETF Last Call

- IESG issues IETF-wide Last Call (typically 2 weeks)
- Community-wide review and comment period
- Address all DISCUSS and COMMENT positions from ADs

#### Step 7: IESG Review and Publication

- IESG reviews; ADs may raise DISCUSS ballots
- Author resolves each DISCUSS
- RFC Editor queue: copy editing, final AUTH48 review
- RFC published

### Estimated Timeline

| Phase | Duration |
|---|---|
| Community spec + implementations | 6-12 months |
| Individual I-D submission to WG adoption | 3-6 months |
| WG development to WGLC | 6-12 months |
| IETF Last Call to RFC | 3-6 months |
| **Total** | **18-36 months** |

---

## IANA Considerations Summary

The following registrations are required before RFC publication:

### Media Type Registration

- Type: `application/mmsp+json`
- Subtype: `mmsp+json`
- Required parameters: none
- Optional parameters: `version`
- Encoding: UTF-8
- Security considerations: See Section 11 of the spec
- Fragment identifiers: N/A
- Restrictions on usage: none
- Author: MMSP Community

### Well-Known URI Registration

- URI suffix: `mmsp.json`
- Change controller: IETF
- Specification document: This RFC
- Related information: MMSP Feed Manifest endpoint

---

## xml2rfc Conversion

When ready for IETF submission, convert using:

```bash
pip install kramdown-rfc
kdrfc spec/draft-mmsp-*.md
# Produces a .xml and a .txt named after the draft
```

Validate with:
```bash
pip install idnits
idnits draft-mmsp-*.txt
```

---

## References

- IETF Datatracker: https://datatracker.ietf.org
- Internet-Draft submission: https://authors.ietf.org
- xml2rfc documentation: https://xml2rfc.tools.ietf.org
- RFC 2119 (Key Words): https://www.rfc-editor.org/rfc/rfc2119
- RFC 8174 (Ambiguity of RFC 2119): https://www.rfc-editor.org/rfc/rfc8174
- IETF DISPATCH WG: https://datatracker.ietf.org/wg/dispatch/about/

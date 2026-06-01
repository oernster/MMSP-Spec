# MMSP IETF Submission Plan

## Overview

MMSP (MultiMedia Subscription Protocol) follows a two-phase publication strategy:
Phase 1 is community specification for adoption; Phase 2 is IETF standardisation.
This document tracks the milestones and process requirements for each phase.

---

## Phase 1: Community Specification (Current)

**Goal:** Establish the specification, achieve two or more independent implementations,
and build an implementer community before IETF submission.

### Milestones

| # | Milestone | Status |
|---|---|---|
| 1.1 | Publish draft-mmsp-00.md to GitHub | In progress |
| 1.2 | Publish JSON Schema for feed manifest and item | In progress |
| 1.3 | Publish Python conformance test suite | In progress |
| 1.4 | Publish reference validator implementation | Pending |
| 1.5 | Publish public website at mmsp.dev (or equivalent) | Pending |
| 1.6 | Announce on relevant mailing lists (rss-public, atom-syntax, ietf-announce) | Pending |
| 1.7 | Achieve two independent client implementations | Pending |
| 1.8 | Achieve one independent server/publisher implementation | Pending |
| 1.9 | Conduct interoperability testing between implementations | Pending |
| 1.10 | Publish MMSP v0.2 incorporating implementation feedback | Pending |

### Deliverables

- `spec/draft-mmsp-00.md`: Full specification text
- `spec/schema/`: JSON Schema files for validation
- `tests/`: Python conformance test suite
- `spec/examples/`: Annotated feed examples

---

## Phase 2: IETF Internet-Draft Submission

**Goal:** Submit MMSP as an IETF Individual Submission Internet-Draft, seek
Working Group adoption, and progress to RFC.

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
4. Draft name: `draft-mmsp-00`
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
- Requires WG consensus (not unanimous, but rough consensus)
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
kdrfc spec/draft-mmsp-00.md
# Produces: draft-mmsp-00.xml and draft-mmsp-00.txt
```

Validate with:
```bash
pip install idnits
idnits draft-mmsp-00.txt
```

---

## References

- IETF Datatracker: https://datatracker.ietf.org
- Internet-Draft submission: https://authors.ietf.org
- xml2rfc documentation: https://xml2rfc.tools.ietf.org
- RFC 2119 (Key Words): https://www.rfc-editor.org/rfc/rfc2119
- RFC 8174 (Ambiguity of RFC 2119): https://www.rfc-editor.org/rfc/rfc8174
- IETF DISPATCH WG: https://datatracker.ietf.org/wg/dispatch/about/

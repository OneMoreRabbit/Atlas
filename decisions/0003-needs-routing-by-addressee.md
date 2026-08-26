---
title: ADR-0003 (Atlas) — Needs routing must honour the addressee, not the graph edge
interface: atlas-adr-0003
version: 1.0
status: accepted
date: 2026-08-26
origin: Atlas-AgentEco architecture/proposals/0008 (raised by the rbac-compile seat from
  first- and third-session field evidence; flagged for extraction by the arch seat)
affects: [atlas_validate, aac-method, templates/component-repo]
implemented: method 1.13 (2026-08-26)
---

# ADR-0003 — Needs routing must honour the addressee, not the graph edge

## Status

**Accepted** — 2026-08-26, all four decisions, unamended. Verified against the reporting
estate before and after.

## Context (as reported, verified here)

`--emit-context` built its *needs addressed to me* section by walking the `docs/needs/`
folder of every component holding an io-graph edge to the reader, then filtering on the
frontmatter key `to`. Two defects followed, pointing in opposite directions:

1. **The addressee field has two spellings; the tool read one.** Documents spelling it
   `addressed-to:` fell through `to is None → True` — the *fail-open* branch — and were
   broadcast to every component whose edge caused that folder to be scanned. Re-audited
   on 2026-08-26: **6 of 23** needs documents use `addressed-to`, up from the 4 of 21
   reported the day before. The ignored spelling is the one in current use.
2. **Edge-scoped selection hid needs that did name the reader.**
   `agent-compile/docs/needs/agent-compile-registry-management-response-v0_1.md` carries
   a correctly spelled `to:` naming `rbac-compile`, and had never appeared in that
   seat's briefing: `agent-compile` holds no edge to `rbac-compile`, so its folder was
   never walked. Confirmed: rbac-compile's edge-scoped folders are
   `[ansible-platform, ingstr, sync-compile]`.

The report's framing is exact and worth preserving as method vocabulary: the routing was
**fail-open where it should be precise, and fail-closed where it should be permissive** —
seats read documents written for someone else, and missed documents written for them.
It is not fixable by fixing the graph: the edge list correctly describes who consumes
what. It does not, and should not, describe who may write to whom.

## Decision

1. **Accept both spellings.** `to`, `addressed-to`, `addressed_to` are aliases.
2. **Route by addressee, not by edge.** A needs document naming an addressee is
   delivered to that slug wherever it lives — all `components/*/docs/needs/` are
   scanned. Documents naming nobody keep the historic edge-scoped, fail-open behaviour,
   where that is the intent.
3. **Canonicalise `to:`** in the method docs and templates; the aliases mean vaults
   normalise at leisure, not as a migration.
4. **Warn on an unroutable addressee.** Routing by addressee turns a typo into silent
   non-delivery, so the validator reports any needs document whose addressee matches no
   component (warn-only). `nav` — the human, via the bridge (AAC-method §9) — is a
   valid addressee.

Alternatives rejected at origin and confirmed here: fixing the four documents and
changing no code (leaves unrecognised-key-means-broadcast in place, so the next document
re-breaks it); making the no-addressee default fail closed (four documents legitimately
name nobody and would vanish silently — under-delivery is worse than visible noise).

## Verification

The reporter's own acceptance list, run against Atlas-AgentEco at 1.12 vs 1.13:

| Case | 1.12 | 1.13 |
|---|---|---|
| `ansible-needs-codex-image-provisions` in rbac-compile's briefing | present ×3 | **absent** |
| `ingstr-needs-qdrant-stack` in it | present | **absent** |
| `ansible-needs-plan-contracts` in it | present | **present** (now because it names the slug) |
| `agent-compile-registry-management-response` in it | absent | **present** |
| `dprox-qdrant-client-bug` (`to: dprox workstream`) | absent | absent |
| unroutable addressee warned | no | **yes** |

Briefing size 27,672 → 21,741 bytes (−21.4%).

## Consequences

- Briefings carry what was addressed to the reader; the retrieval invariant becomes
  true rather than aspirational.
- A need reaches its addressee with no edge between the two components — which is
  exactly when a component most needs to hear from a stranger.
- **Behaviour change, not silent:** seats stop seeing documents they currently see.
- **Found on first run, in the reporting estate:** ten needs documents address
  `image-compile workstream`, `agent-deployment workstream`, `architect` or
  `architecture (route to the Atlas method seat)` — none of which are component slugs,
  so they reach nobody. They already reached nobody under the old selector; the
  difference is that this is now *reported* instead of silent. Fixing them is the
  owning components' work, not the method's — the method deliberately does not map repo
  names or role names onto slugs.
- Scanning all needs folders is a broader read than scanning consumers'. Trivial at nine
  components; worth revisiting at a different scale.

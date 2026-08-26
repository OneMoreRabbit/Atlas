---
title: ADR-0005 (Atlas) — A briefing must show what the component still owes
interface: atlas-adr-0005
version: 1.0
status: accepted
date: 2026-08-26
origin: Atlas-AgentEco PR #30, components/agent-skeleton/docs/needs/agent-skeleton-unanswered-needs-finding-v0_1.md
affects: [atlas_validate, aac-method, templates/component-repo]
implemented: method 1.14 (2026-08-26)
---

# ADR-0005 — A briefing must show what the component still owes

## Status

**Accepted** — 2026-08-26. Decisions 1 and 3 implemented; decision 2 was already
delivered by [[0003-needs-routing-by-addressee]] in method 1.13, after the report was
written.

## Context

The *Consumer feedback* section listed the needs raised against a component but not
which of them it had already answered — so a settled item and an outstanding one
rendered identically. On the reporting seat, three needs displayed the same way: two
answered, one (`ansible-needs-seat-python-docs`) raised on 2026-08-25 and unnoticed
until the seat listed the consumer's folder **by hand**, which is precisely the browsing
§6 forbids.

The existing filter drops needs whose `status:` is resolved — but `status:` is
maintained by the **raiser**, so it reflects "has the consumer noticed and closed this",
not "has the provider answered". Those diverge immediately, and asking consumers to
close promptly does not fix it: the raiser has no event to react to, and would have to
poll the provider's outbox — the same problem pointed the other way.

## Decision

1. **Compute the join.** The provider already writes the link (`responds_to:` in its
   `provides/` documents); make it load-bearing. The emitter indexes the component's own
   `provides/` (including `archive/` — an answer later superseded was still given) and
   marks each need **`answered by <doc>`** or **`UNANSWERED`**, with a count at the head
   of the section. No cross-component writes, no consumer cooperation: the provider owns
   its responses and the join is computed — the same shape as pinned-vs-latest drift.
2. **Separate what is addressed to me.** Already delivered by decisions/0003 (1.13):
   needs are routed by addressee, so a need naming another component no longer appears.
3. **Render the fields the document carries** (`need:`, `status:`) instead of a
   `version:` that needs documents never have — the `(version ?)` every entry showed.
4. **Warn on a `responds_to:` naming no document in the vault.** Existence, not
   category: a response may legitimately answer a need, a proposal, or a living
   document, and anything narrower cries wolf on correct links. Values are parsed in all
   the shapes the field is written in — vault-relative path, `[[wikilink]]`, or prose
   naming a file — so no vault needs a migration.

## Verification

On the reporting estate: `_1 unanswered._`, with `codex-image-provisions` and
`seat-python-docs` shown as answered by the documents that answered them, and
`seat-contract-v0_3` — whose response carries no `responds_to:` — correctly outstanding.
No entry renders `(version ?)`. All four of the estate's existing `responds_to:` values,
in three different shapes, resolve.

## Consequences

- What a component owes is on the page, not in its memory — the method's instinct
  elsewhere (branch policy, `--verify`, drift rows) applied to the one list that states
  obligations.
- **`responds_to:` becomes load-bearing.** A response published without it reads as
  UNANSWERED. That is the correct default — silence about an obligation should look like
  an obligation — but it is a real convention change for component seats.
- The reporter's scope note is worth keeping: "read it more carefully" is not a
  system-level answer, particularly for a fresh seat with no memory of what it has
  already dealt with.

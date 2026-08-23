---
title: ADR-0001 (Atlas) — Component repo wiring is a declared, checkable fact
interface: atlas-adr-0001
version: 1.0
status: accepted
date: 2026-08-23
origin: Atlas-AgentEco architecture/proposals/0005 (raised 2026-08-21 by the
  agent-skeleton component session; classified ATLAS-METHOD by AgentEco arch
  review 2026-08-23 and extracted here — one home per document)
affects: [aac-method, atlas_validate, component-init, templates/component-repo]
implemented: method 1.6 (2026-08-23)
---

# ADR-0001 — Component repo wiring is a declared, checkable fact

First ADR of the method repo's own decision log. The method is governed by its
own rules (AAC-method preamble): decisions about the method's shared
architecture follow the same proposal → review → decision flow it prescribes,
recorded here. Project-level residue from the originating proposal stays with
the originating vault (noted in §Review).

## Status

**Accepted** — 2026-08-23, Atlas method review. Implementation scheduled for
method 1.6, with the amendments recorded in §Review.

## Context (as raised, AgentEco 2026-08-21)

Method 1.1 gave every component code repo a committed "Atlas half"
(`AGENTS.md`, `.atlas.conf`, `scripts/atlas-*.sh`, `.claude/`), installed by
`atlas_init.py`. It is what makes a session mechanical rather than
trust-based: `ATLAS-CONTEXT.md` at SessionStart, the golden-rule-2 write
guard at the tool boundary, `/atlas-publish` at the end.

Three facts about the originating estate (AgentEco, 2026-08-21):

1. **Seven of eight components were unwired.** Only agent-skeleton had the
   code-repo half installed.
2. **Nothing reports it.** A component sat unwired from repo creation until
   someone happened to read `component-init.md` §4. There is no signal
   anywhere — not in the vault, not on the dashboard, not in CI. An unwired
   component looks exactly like a wired one from above.
3. **The vault could not even locate the repos.** `registry/io-graph.yml`
   carried `source: G:\VSProjects\<Name>` for seven of eight components — a
   machine path on one person's desk, which method 1.1 outlawed. Fact 3 turns
   fact 2 from a gap into a dead end: you cannot write a check for a thing
   you have no address for.

A seat-local mitigation (a warning when a cloned repo lacks `.atlas.conf`)
catches the next occurrence but cannot see an estate: it sees only what a
given seat happens to clone, and reports to a terminal nobody may be watching.

## Decision (as raised; amendments in §Review)

Make wiring a declared fact in the graph and a checked one in CI.

1. **`source:` is the component's clone URL, for every component.** It is
   already the graph's field for "where the code lives"; this fixes its type.
   Machine paths become drift, reported like any other. One-line edit per
   component, owned by that component (it names its own slug, so the write
   guard already permits it).

2. **"Wired" gets a definition.** A component repo is wired iff its default
   branch root contains `.atlas.conf` whose `SLUG` equals the component's
   slug, and a committed `AGENTS.md`. Both are cheap to fetch and neither can
   be faked by a local checkout — the point is what a *fresh clone anywhere*
   gets.

3. **The validator gains an opt-in `--check-wiring` mode.** For each
   component with a URL `source:`, fetch those two paths and report wired /
   unwired / unaddressable. CI runs it with the flag; a local run without it
   behaves as today.

4. **Unwired components surface where drift does** — on the dashboard and in
   the drift report. **Warn, never block:** a component is free to be unwired
   while it is being brought up; what it may not be is unwired *invisibly*.

5. **Wiring stays the owning component's own act, in its own repo.** Golden
   rule 2 is about ownership, not only vault paths. An arch seat wiring code
   repos on components' behalf is the same category of mistake as authoring
   in someone else's outbox. New repos wire at creation; existing ones wire
   from their own seat, at that seat's next session.

## Consequences (as raised)

- The estate becomes legible: "which components are actually in the protocol"
  is a number on the dashboard rather than folklore.
- The last machine paths leave the graph, closing a method-1.1 debt.
- The check is the same shape as drift — declared vs actual — so it needs no
  new concepts, no new ceremony, and no new place to look.
- Cost: an optional network dependency and a credential requirement for
  private repos in CI. Contained by opt-in + warn-only.
- A component could pass the check and still have drifted scripts;
  `atlas-sync.sh` already checksums those against the pinned method — this
  decision deliberately does not duplicate that.

Alternatives considered and rejected at origin: wiring repos centrally at
seat provisioning (wiring is a commit to a repo, not seat state); leaving it
to the seat-local warning (right check, wrong place — kept as the fast local
signal); blocking on unwired (bring-up would deadlock; method precedent is
that naming and drift warn, not block).

## Review (Atlas method review, 2026-08-23 — acceptance notes)

Accepted. The decision is method-shaped end to end: declared in the graph,
checked mechanically, warn-never-block, ownership preserved. Four amendments
for the 1.6 implementation:

1. **The "validator is pure and offline" premise is stale.** The proposal was
   written against method 1.4; method 1.5's branch-status table already
   performs always-on `ls-remote` per repo with graceful offline degrade.
   Restated boundary: *ref-level* lookups (branches, tags) are cheap and
   always-on; *content* fetches (`--check-wiring`) are opt-in for CI, exactly
   as proposed. The opt-in conclusion survives; the rationale is updated.
2. **No new panel: a `Wired` column joins the 1.5 branch-status table.** The
   proposal predates that table; wiring, default-branch, divergence, and tag
   are the same per-repo estate row. One table, one place to look.
3. **`source:` typing is elevated to the spec (§5).** Method 1.5 already
   reports "no source URL" per repo; 1.6 defines `source:` as the clone URL
   in the io-graph schema, making machine paths reportable drift by
   definition rather than by side effect.
4. **Fetch mechanism:** a blobless shallow clone (`--depth 1
   --filter=blob:none --no-checkout`) with on-demand `git show` of the two
   files — refs plus two blobs per repo, vendor-neutral, honours the same
   credentials as every other vault fetch.

Project residue staying with Atlas-AgentEco (its arch seat holds them): the
seven `source:` URL corrections, and adoption of the flag in its vault CI
once 1.6 ships.

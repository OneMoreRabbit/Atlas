---
title: ADR-0004 (Atlas) — The briefing is compiled from the work branch, not the checkout
interface: atlas-adr-0004
version: 1.0
status: accepted
date: 2026-08-26
origin: Atlas-AgentEco PR #28, components/agent-skeleton/docs/needs/agent-skeleton-stale-briefing-finding-v0_1.md
affects: [atlas-context, atlas-sync, atlas-common]
implemented: method 1.14 (2026-08-26)
---

# ADR-0004 — The briefing is compiled from the work branch

## Status

**Accepted** — 2026-08-26, the reporter's *preferred* fix, superseding the warning-only
mitigation I shipped in 1.12.

## Context

`atlas-context.sh` compiled `ATLAS-CONTEXT` from whatever branch the vault clone had
checked out. After any publishing session that is an `atlas/<slug>/<topic>` branch — the
**normal end state of publishing** — so the next session was briefed from a snapshot of
the vault as it was when that branch was cut. Observed on the reporting seat at both of
its last two orientations: an ADR accepted the previous day still rendered
`status: proposed`, and `atlas-sync` reported method drift and script self-drift against
the *parked branch's* pin (1.7, then 1.11) rather than the work branch's.

Two properties make this worse than an ordinary bug, and the report states them better
than I would:

- **It breaks the retrieval invariant.** §6 says a session reads the briefing and never
  browses, and that a session which has started has already done the reads. If the
  artefact can be silently historical, that guarantee is gone — and the session has been
  told not to go and check.
- **It presents as authority, not as an error.** Nothing is missing or malformed; the
  false drift warnings cite specific version numbers, which reads as precision. Both
  occurrences invited a *wrong corrective action* — re-pin to close drift that does not
  exist, or re-copy scripts that are already correct.

Method 1.12 added a `STALE SOURCE` header, on my judgement that the warning was
sufficient and work-branch compilation could wait. It was not sufficient: the finding
recurred at 1.12, and the warning never addressed the false drift signals at all, which
are produced by `atlas-sync` reading the pin from the checkout.

## Decision

1. **Compile the briefing from `origin/<work>`.** `atlas-context.sh` adds a throwaway
   detached worktree of the work branch and runs the emitter against it, then removes it.
   The publish branch is left exactly where it was (1.11's correct behaviour stands).
2. **Read the io-graph from the work branch too** — pin, and the branch policy itself.
   A parked branch's pin can only manufacture false drift, and false drift invites the
   wrong action. Shared as `atlas_graph_text` / `atlas_work_branch` in `atlas-common.sh`,
   so sync and context cannot disagree (a child process cannot export to its parent).
3. **Every briefing states its provenance** — `Compiled from vault <branch> @ <sha>` — so
   a stale one can never look like a fresh one. If the worktree cannot be created, the
   1.12 `STALE SOURCE` banner remains as the fallback.

## Verification

Against a fixture where the work branch has moved on (pin 1.11 → 1.14, a proposal
accepted and moved to `decisions/`) while the clone is parked on a publish branch:

| Criterion (the reporter's) | Result |
|---|---|
| briefing emits work-branch content | ✅ `origin/dev` content, provenance line names it |
| no drift warning cites a version differing from the work branch pin | ✅ cites v1.14, not v1.11 |
| an ADR accepted on the work branch is not shown as `proposed` | ✅ absent |
| the publish branch is left alone | ✅ still checked out |
| no worktree left behind | ✅ |

## Consequences

- The retrieval invariant holds again for the case that broke it most often.
- A parked publish branch is now free of consequences, which is what made 1.11's
  leave-it-alone decision safe in the first place.
- Cost: one extra worktree add/remove per session start when the clone is off-branch.
- Lesson recorded: when a report offers "fix it properly, or make it visible", visibility
  is not a substitute if the invisible failure also drives *other* signals wrong.

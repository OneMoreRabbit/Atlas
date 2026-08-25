---
title: Arch Seat Protocol — the architecture session's own duties
interface: arch-seat
version: 1.1
status: active
maturity: 0.1        # first written form of a previously trust-based role
updated: 2026-08-25
supersedes: 1.0
# 1.1: the escalation rule — which proposals the arch seat decides, and which go to @nav.
---

# Arch Seat Protocol

The counterpart to [[component-init]]: what the **architecture session** of a project
does, every session and at review. Components had a mechanical protocol from method
1.1; the arch seat was held in memory until now.

## Scope

| | |
|---|---|
| **Owns (writes directly)** | `architecture/**` (constitution, system-context, proposals, decisions), `registry/io-graph.yml`, vault `_triage/` and `meta/` |
| **Writes in the Nav vault** | `_bridge/` only |
| **Reviews, never authors** | `components/<slug>/**` — component outboxes are theirs |
| **Never commits** | generated views (`registry/graph.md`, `dashboard.md`, `component.md` edge blocks, `registry/.compiled/**`) — CI regenerates them on the work branch |

Works against the vault's work branch directly (it is the reviewer, not a PR author).

## Every session

1. **Sync.** Pull the vault (work branch) and the Nav vault.
2. **Sweep component asks.** `ls components/*/docs/needs/nav-*.md` — for each not already
   linked from `_bridge/tasks.md`, add a bridge line:
   `- [ ] @nav — <ask> (from <slug>, <date>) — components/<slug>/docs/needs/<file>`
   Do **not** edit the component's file to mark it mirrored — it is their outbox;
   dedupe by what the bridge already links.
3. **Answer the bridge.** Every `@atlas` task and thread turn gets a reply or a tick
   before the session ends.
4. **Read the dashboard.** Act on red: method pin drift, branch policy, wiring,
   breaking contract drift.
5. **Clear the review queue.** Merge outbox-only PRs that CI passed; review PRs
   touching `architecture/proposals/**` or `registry/io-graph.yml`.

## Periodic review

Pull-driven — run it when the dashboard shows it is due (open threads, unreleased
`dev → main` delta, red rows), not on a fixed calendar.

1. Walk open `_bridge/threads/`; resolve or reply, then move resolved ones to
   `_bridge/archive/`.
2. Accept or reject `architecture/proposals/**`. Accepted → `architecture/decisions/`,
   update constitution / system-context / io-graph. Rejected → keep, `status: rejected`.
   **Escalation rule:** decide purely structural or mechanical proposals yourself.
   Anything that changes **direction, cost, or scope** goes to the bridge for `@nav` —
   stated in plain words, not as a diff — and waits. Escalating a naming or
   folder-placement question is a defect; so is deciding a scope question alone.
3. Re-pin deliberately: method version, contract versions flagged as drift.
4. Archive: answered proposals to `architecture/archive/proposals/` with a
   `resolution:` frontmatter line pointing at the answer. Empty `_triage/`.
5. Clear the validator's naming and doc-plane warnings.
6. Merge `dev → main` across the project's repos — the release/deploy signal.

## Answering a component's ask

Answers land in the vault the normal way — an ADR, an updated contract, a constitution
change — never by editing the asking component's outbox. The component picks the
outcome up in its next `ATLAS-CONTEXT.md`; the asking component archives its own
`needs/` doc at its next publish.

## Never

- Author under `components/<slug>/docs/**` (curation moves and archiving of
  *vault-level* material are in scope; a component's documents are not).
- Wire component code repos on their behalf (decisions/0001) — wiring is a commit to
  their repo, by them.
- Write anywhere in a Nav vault except `_bridge/`.

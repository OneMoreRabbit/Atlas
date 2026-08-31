---
title: Arch Seat Protocol — the architecture session's own duties
interface: arch-seat
version: 1.3
status: active
maturity: 0.1        # first written form of a previously trust-based role
updated: 2026-08-25
supersedes: 1.0
# 1.1: the escalation rule — which proposals the arch seat decides, and which go to @nav.
# 1.2: platform asks route to the orchestrator; seats run AI, not products. Cross-vault
#   providers sweep consuming vaults and deliver answers into them. Doctrine v0.2: no
#   container runtime in a seat, estate-built images, reshape asks before forwarding;
#   the development ladder decides which asks need the estate at all.
# 1.3: a structural change is a design act — re-read decisions/ before extending a
#   mechanism; summarised context is never the design record.
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

## Before you extend a mechanism, read the decision

> **A structural change is a design act.** Before you add a directory, a file kind, or
> a schema key — anywhere — re-read `architecture/decisions/` for the governing ADR.
> Extending the mechanism already in front of you is not neutral: it is a design
> decision taken without consultation, and it will look like momentum rather than a
> choice. **Summarised context is never the design record** — not session memory, not
> what survived compaction, not the briefing's prose. The vault is.

Two failures of this class in three days on the reporting estate, both caught by the
operator rather than by the protocol: a mechanism trusted over recorded intent
(external pins), and a product bundle extended in place instead of re-reading the
repo-shape ADR that already answered it. The design was never missing in either case;
the consultation was.

The ownership question the second one turned on is worth carrying as a general test:
**a thing belongs to what it serves today, not to whoever created it first.** A
component's platform never lives inside another product's bundle; a document owned by
one component never lives in another's folder (§3). When those disagree, the ADR wins
and you re-home the thing.

## Cross-vault providers — sweep and deliver

If this vault's component provides to consumers in **other** vaults, two duties are
yours, because only you have the estate access:

- **Sweep.** Each session, read the consuming vaults for open `needs/` addressed to your
  slug. They cannot reach you any other way, and they have no access to this vault.
- **Deliver.** Answer in your own `provides/` (the authored home), then push a
  banner-marked copy to `components/<your-slug>/docs/provides/` in the consumer's vault,
  on branch `atlas/<your-slug>/<topic>`. The CI guard already fences this to exactly
  that folder — it is the one sanctioned write into another project's vault. Never write
  anything else there, and never paste the content into a bridge: bridges carry
  coordination, documents have homes.

A consumer needs no `external:` pin to read what you delivered; the pin is optional
bookkeeping that gives them a drift row. **Deliver on every version bump** — a stale
delivered copy is silent, since an unpinned consumer has no drift signal.

## Platform asks are not yours to answer

A component asking for a database, broker or product runtime is asking for a **platform
container**, which is estate work: it runs beside the seat on the project network, and
the orchestrator declares, provisions and owns its lifecycle. Route the ask there —
do not answer it in-vault, and never by suggesting the seat install the thing. A seat
runs AI and the component's own build and test runs; nothing else, and never a container
runtime (Orchestrator `decisions/0004-seats-and-platforms`).

**Know which rung the ask belongs on** (Orchestrator `decisions/0005-dev-loop-ladder`).
A component owns its seat and iterates freely in its dev container against a shared
checkout; the orchestrator is involved when the **environment** changes — new
requirements, a rebuild, a promotion — not when the component's code does. An ask that
is really "my code changed" needs no estate round trip at all; say so and close it.

**Reshape the ask before you forward it.** Components ask for the tool they imagine
using, not the outcome they need, and forwarding that verbatim spends an estate round
trip on the wrong question. The pattern, from the field: *"give my seat a container
runtime so I can build my image"* is really *"build this Dockerfile on an estate host
and return the image id, run output and readiness result."* Rewrite it that way — the
component authors the image, the estate builds it. Transient runs of a component's own
code in its seat need no ask at all; anything that must stay up is a platform container.

The same test settles the borderline cases: **anything needing superuser or a different
image is an ask**; using a platform that already exists is not.

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

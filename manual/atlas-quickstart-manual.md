---
title: Atlas Quickstart — the operator's view
interface: atlas-quickstart-manual
version: 1.0
status: active
updated: 2026-08-24
---

# Atlas Quickstart

The human operator's view of an Atlas-run project: what the repos are, where you act,
and where everything else happens without you. Setup detail lives in the referenced
docs — this page points, it doesn't duplicate.

## The fleet — four repo classes per project

| Repo | What it is | Who edits | Branch you're on |
|---|---|---|---|
| `Atlas` (this repo) | the method: spec, tools, templates, manuals | the method seat | n/a — vaults pin a release tag |
| `Atlas-<Project>` | the project vault: constitution, ADRs, io-graph, contracts, dashboard | AI seats (write model); **you review, never edit** | `dev` (work) |
| `Nav-<Project>` | your idea space: sketches, canvases, half-ideas — messy by right | **you; AI writes only `_bridge/`** | `main` (trunk-only) |
| one code repo per component | the code + its committed Atlas half | its component seat | `dev` (work) |

## Your day

- **The bridge** — `Nav-<Project>/_bridge/` (sorts first in Obsidian). `tasks.md`: tick
  and add `@nav` items, drop `@atlas` asks. `threads/`: durable conversations — ideas,
  decisions, disagreements go here, not into chat history. Rules: [[bridge-init]].
- **The dashboard** — `Atlas-<Project>/dashboard.md`: method pin, per-repo estate
  (branch policy, unreleased work, wiring), contract drift. Red means "look", not
  necessarily "act".
- **Vault PRs** — outbox-only PRs auto-merge; PRs touching `architecture/proposals/`
  or `registry/io-graph.yml` wait for **you** (or your arch seat) — that's proposing,
  the one ceremony the method keeps.
- **Periodic review** — one sitting: walk the bridge threads, accept/reject ADRs,
  merge `dev → main` across the project repos (the release/deploy signal).

## Where things go

Idea → Nav vault, anywhere. Direction, decision, or ask → `_bridge/`. Architecture →
never written by you: it arrives in the Atlas vault via the seats, traceable to what
was agreed on the bridge.

## Setup pointers

- New project: `README.md` → "Starting a new project" (vault seed, CI, branches, pin).
- New component: [[component-init]] (registration + the code-repo half).
- Upgrading a vault to a new method release: `README.md` → "Upgrading an existing vault".
- Obsidian on desktop and phone: [[obsidian-manual]].

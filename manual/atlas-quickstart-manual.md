---
title: Atlas Quickstart — the operator's reference
interface: atlas-quickstart-manual
version: 1.1
status: active
updated: 2026-08-24
supersedes: 1.0
# 1.1: cut narrative; lookup tables + step pointers only.
---

# Atlas Quickstart

## The repos

| Repo | Contents | Who edits | Your branch |
|---|---|---|---|
| `Atlas` | the method: spec, tools, templates, manuals | method seat | n/a (vaults pin a tag) |
| `Atlas-<Project>` | vault: constitution, ADRs, io-graph, contracts, dashboard | AI seats — you review PRs, never edit | `dev` |
| `Nav-<Project>` | your ideas; AI writes `_bridge/` only | you | `main` |
| code repos (per component) | code + committed Atlas half | component seats | `dev` |

## Daily

1. `Nav-<Project>/_bridge/tasks.md` — tick/add `@nav` items; add `@atlas` asks.
2. `_bridge/threads/` — durable conversations; decisions go here, not chat.
3. `Atlas-<Project>/dashboard.md` — method pin, estate (branches, wiring), drift.
4. Vault PRs: outbox-only auto-merge; review only `architecture/proposals/**` and `registry/io-graph.yml` PRs.

## Periodic review (one sitting)

1. Walk open `_bridge/threads/`; resolve or reply.
2. Accept/reject ADR proposals.
3. Merge `dev → main` across project repos (the release/deploy signal).

## Task → doc

| Task | Doc |
|---|---|
| New project | `README.md` → "Starting a new project" |
| New component | [[component-init]] |
| Upgrade a vault to a new method release | `README.md` → "Upgrading an existing vault" |
| Bridge setup / rules | [[bridge-init]] |
| Obsidian on desktop/Android | [[obsidian-manual]] |

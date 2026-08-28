---
title: Operating Atlas — the human's manual
interface: atlas-operating-manual
version: 1.0
status: active
updated: 2026-08-25
supersedes: atlas-quickstart-manual 1.1
---

# Operating Atlas

What you do, and what is done for you.

## Your three surfaces

| Surface | Where | You |
|---|---|---|
| **The bridge** | `Nav-<Project>/_bridge/` | work here daily |
| **The dashboard** | `Atlas-<Project>/dashboard.md` | read it; never edit it |
| **PRs** | GitHub | see §4 — most are not yours |

Everything else — the Atlas vault, contracts, ADRs, drift — is maintained for you.

## 1. Daily (~10 minutes)

1. Open `Nav-<Project>/_bridge/tasks.md`. Tick what you have done; answer or action
   `@nav` items; add anything you want done as an `@atlas` item.
2. Skim `_bridge/threads/` for turns addressed to you; reply in the thread.

If both are empty, you are done. Most days they will be.

## 2. Periodic (~30–60 minutes, roughly weekly)

Run it when the dashboard shows it is due — open threads, unreleased `dev → main`
changes, or red rows. Not on a calendar.

1. Open `Atlas-<Project>/dashboard.md`. Read **red rows only**: method pin, branch
   policy, wiring, breaking contract drift. Anything red that is not obvious, ask the
   arch seat on the bridge.
2. Walk open `_bridge/threads/`: resolve or decide each one.
3. Decide the proposals the arch seat escalated to you (§3). Say yes or no on the
   bridge; the arch seat writes it up as an ADR.
4. Merge `dev → main` across the project's repos. **This is the release/deploy
   signal** — `main` is what is live.

## 3. What you discuss with the arch seat

Direction and judgment — what it cannot decide for you:

- What to build next, and what to drop.
- Trade-offs with a taste, cost, or risk dimension.
- Whether a proposal is worth accepting at all.
- Anything where being wrong costs money, time, or a rewrite.

**Not** yours: contract versions, drift, folder placement, naming, branches, ADR
wording. Those are the arch seat's job. If it brings you one, push it back.

| | Example |
|---|---|
| Good ask from arch | "dprox wants to change the endpoint contract; it breaks agent-compile. Two options, one costs a week. Which?" |
| Bad ask from arch | "Should this document go in `provides/` or `needs/`?" |

**The escalation rule.** The arch seat accepts proposals that are purely structural or
mechanical, on its own authority. Anything that changes direction, cost, or scope comes
to the bridge for you — in plain words, not as a diff.

## 4. PRs — the two kinds

| Kind | Contains | Who handles it |
|---|---|---|
| **Vault PR**, touching only `components/<slug>/**` | documentation only — a component publishing a contract, an ask, its own io-graph line | **auto-merges.** You never see it |
| **Vault PR**, touching `architecture/proposals/**` or `registry/io-graph.yml` | a proposal, or a change to the topology | arch seat reviews; escalates to you per §3 |
| **Code PR** in a component repo | actual code | ordinary dev practice — skim the diff, merge |

Vault PRs never contain code. Code PRs are not governed by the method.

You do not sit in a PR queue.

## 5. What you never do

- Edit the Atlas vault (that includes `dashboard.md`, contracts and ADRs).
- Write architecture documents.
- Fix drift, rename files, or tidy folders.
- Chase components for updates.

If you find yourself doing any of these, something upstream is broken — say so on the
bridge.

## 6. Where to look something up

| Task | Doc |
|---|---|
| Start a new project | `README.md` → "Starting a new project" |
| Add a component | [[component-init]] |
| Upgrade a vault to a new method release | `README.md` → "Upgrading an existing vault" |
| How the bridge works | [[bridge-init]] |
| What the arch seat is supposed to do | [[arch-seat]] |
| Obsidian on desktop and Android | `Atlas-Orchestrator` → `components/ansible-platform/docs/manual/new-seat-4-obsidian-sync.md` |
| Tokens and repo access | `Atlas-Orchestrator` → `components/ansible-platform/docs/manual/new-seat-3-github-tokens.md` |

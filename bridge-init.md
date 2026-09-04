---
title: Bridge Init — the human/AI interface of a project
interface: bridge-init
version: 1.3
status: active
maturity: 0.1        # deliberately simple; iterate from practice, not design
updated: 2026-08-24
supersedes: 1.0
# 1.1: component asks route via their own needs/ outbox (nav- prefix), mirrored to the
#   bridge by the arch seat — no component seat needs Nav-vault credentials.
# 1.2: tasks.md write-loss under syncing clients acknowledged and deferred; threads are
#   the record, tasks.md an index.
---

# Bridge Init

Every project has two poles: **Nav** (the human — direction: ideas, priorities,
decisions, judgment) and **Atlas** (the AI side — implementation: analysis, structure,
execution, memory). Ideation and design are **mutual discussion**. The **bridge** is
where that discussion lives, durably — sessions evaporate; files persist.

- The human never edits the Atlas vault. The AI never edits the Nav vault — **except
  `_bridge/`**, the one declared exception, granted by the project owner.
- The bridge is where direction is *agreed*, never the system of record for
  architecture: the arch seat carries accepted direction into the Atlas vault
  (proposals, contracts, ADRs) on its side.

## Where

`_bridge/` at the root of the project's Nav vault — `Nav-<Project>` (formerly
`Dev-<Project>`). The underscore sorts it first in Obsidian. Nav vaults are trunk-only
on `main`, and messy by right: no naming canon, no branch policy, no ceremony —
hygiene `.gitignore` (`.trash/`, workspace cruft) only.

```
Nav-<Project>/_bridge/
  tasks.md        # ONE list, two owners — every item tagged @nav or @atlas
  threads/        # one file per conversation topic, append-only turns
  archive/        # resolved threads move here
```

## The three rules

1. **Tasks carry owners.** Either side may *add* an item for either owner; only the
   **owner** edits or ticks it. One line per item:
   ```markdown
   - [ ] @nav — decide X (from @atlas, 2026-08-24)
   - [ ] @atlas — implement Y (from @nav, 2026-08-24)
   ```
2. **Threads are append-only, one topic per file.** Turns are headed `## @nav — <date>`
   / `## @atlas — <date>`. Frontmatter: `topic`, `status: open | resolved`, `opened`.
   When resolved, move the file to `archive/`.
3. **The arch seat reads `_bridge/` every session and answers before it ends** —
   anything addressed `@atlas` gets a turn or a tick. It reads the wider Nav vault only
   where a task or thread points it (the human's idea space stays private by default).

## Component asks — routed, not direct

Component seats never write to a Nav vault. A component asking the human files it in
**its own outbox**, where the CI guard already permits it and the PR auto-merges:

```
components/<slug>/docs/needs/nav-<slug>-<topic>-vX_Y.md
```
```yaml
---
to: nav          # required and explicit — a needs doc with no `to:` goes to everyone
version: 0.1
status: open
---
```

The `nav-` prefix makes the arch seat's sweep one glob and clusters the asks in a
folder listing. The arch seat mirrors each new one onto `tasks.md` as an `@nav` line
linking the source file ([[arch-seat]] §Every session); you tick it on the bridge,
which you own. Answers come back through the vault (ADR, contract, constitution) —
never by editing the asking component's outbox.

**The bridge is human↔AI only — never a seat-to-seat channel.** `nav` addresses the
human; `to: nav` is for a decision or direction only the human can give. A seat that
needs something from *another component* addresses **that component's slug**, and the
ask is delivered straight into its briefing — no bridge, no human relay. If the arch
seat sweeps a `to: nav` ask that is really for another component, it **redirects it to
that component rather than mirroring it to the bridge** (the same reshape it does for
platform asks). Two seats conversing through `@nav` is the failure this prevents: the
human is not their transport. (Direct seat messaging, when it exists, is the
`agent-comms` component's job, not the vault's.)

## Setup (arch seat, one time — as part of the 1.7 upgrade)

1. *(Owner)* Rename `Dev-<Project>` → `Nav-<Project>` — GitHub redirects old URLs, so
   clones and GitSync keep working.
2. Add the Nav vault to the arch seat's repo list: **read `_bridge/` (and pointed-to
   docs); write `_bridge/` only.**
3. Create `_bridge/tasks.md` (header + the two-owner rule in a comment), `threads/`,
   `archive/`. Open a first thread announcing the bridge and inviting the owner's
   first items.
4. Thread template:
   ```markdown
   ---
   topic: <short-topic>
   status: open
   opened: 2026-08-24
   ---

   ## @atlas — 2026-08-24
   <turn>
   ```

## Deliberately deferred

**Known: `tasks.md` can lose writes under a syncing client** (arc-platform finding,
2026-09-01 — a mobile sync twice resolved the file in favour of the phone's copy,
silently, discarding an arch-seat withdrawal). It is the bridge's only shared-write
file and the only one losing data; `threads/` never collides. The operator has chosen
to keep the single file and fix the client first. Until then: **threads and needs are
the record; `tasks.md` is an index that may lose entries** — anything that matters is
also said in a thread. If the client cannot be made to behave, the fix is one file per
owner (`tasks-nav.md` / `tasks-atlas.md`, owner edits, other side appends).

Keep it this simple and work with it. Not yet built, extracted later from practice if
practice wants them: mechanical write-scope guards on `_bridge/`, dashboard
awaiting-@nav / awaiting-@atlas counts, task aging, multi-human lanes.

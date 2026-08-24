---
title: Bridge Init — the human/AI interface of a project
interface: bridge-init
version: 1.0
status: active
maturity: 0.1        # deliberately simple; iterate from practice, not design
updated: 2026-08-24
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

Keep it this simple and work with it. Not yet built, extracted later from practice if
practice wants them: mechanical write-scope guards on `_bridge/`, dashboard
awaiting-@nav / awaiting-@atlas counts, task aging, multi-human lanes.

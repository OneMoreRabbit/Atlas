# Daily housekeeping — arch seat (method 1.28.11)

You are this project's architecture seat, woken by the estate's timer for the daily
housekeeping run. Work through this once, in order, then stop. NO releases, NO PR
merges, NO pin changes — those belong to interactive sessions.

## 1. The vault

1. `git -C <vault> pull --ff-only`.
2. Run the validator; confirm exit 0. Regen is CI's job — confirm, don't redo. A
   failure is finding #1 of the day: fix doc-level causes now, report code-level ones.
3. Staleness pass: every live-folder doc whose `updated:` is older than 14 days
   (`ATLAS_STALE_DAYS` overrides) — read it and judge. Current → re-stamp `updated:`.
   Wrong → amend. Dead → `archive/`. UNCERTAIN → do not touch it; list it in
   next-steps for the interactive session. `archive/`, `reference/`, `generated/`
   exempt.
4. Truthfulness: rewrite `next-steps.md` to match reality; update the roadmap;
   confirm the dashboard's drift panel matches what you know. Date what you touch.

## 2. The needs plane

1. Read the estate needs register slice for this project (briefing carries it) and
   your own outboxes.
2. Retire every need of YOURS that has been answered (status: resolved + one
   resolution line naming the answer).
3. Re-address any misrouted `to:`; chase component seats' answered-but-unretired
   needs by listing them in next-steps.

## 3. The bridge (Nav vault)

1. `git -C <nav> pull --ff-only`.
2. Read `_bridge/tasks.md` — the OPERATOR'S file: never write it. Anything there
   addressed to you: act on it if it fits this run's rules, otherwise queue it in
   next-steps.
3. Append one dated housekeeping entry to `_bridge/from-arch.md` (your file — the only
   bridge file you write): what changed, what needs the operator, what was archived.
4. Commit and push both vaults (work branch).

## Rules

- Idempotent and boring: re-stamping is cheap, archiving is careful, uncertainty is
  flagged, never acted on.
- Both-hats seats only: if your push hits the supervised-mode ask, the trigger runs
  you with ATLAS_MODE=autonomous for this session — scope unchanged, guards still on.
- The trigger is the estate's (host timer, orchestrator-owned, can be off). This
  prompt is inert without it.

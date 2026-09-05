# templates/arch-seat — the arch seat's reorientation hook

Component seats re-orient after a compaction because their `SessionStart` hook re-emits
`ATLAS-CONTEXT.md`. An **arch seat** has no component slug and works the vault directly,
so it needs the equivalent: a `SessionStart` hook that emits the arch briefing
(`atlas_validate.py --emit-arch-context`).

Install in the arch seat's launch dir (where the agent starts — the vault checkout, or
its `~/work` parent):

1. Copy `atlas-arch-context.sh` there; `chmod +x`.
2. Merge `.claude/settings.json` into the launch dir's (same shape as a component seat's).
3. Set `ATLAS_VAULT` (default `.`) to the vault checkout and `ATLAS_METHOD` to the pinned
   method checkout, if not the defaults.

The hook has **no matcher**, so it fires on startup, resume, clear and compact. On the
non-startup sources it prepends a reorientation directive — the arch seat re-reads its
briefing and resumes without being asked. Seat provisioning (the orchestrator) may
install this as part of standing up an arch seat.

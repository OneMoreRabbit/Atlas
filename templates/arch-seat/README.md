# templates/arch-seat — the arch seat's reorientation hook and alignment gate

Component seats re-orient after a compaction because their `SessionStart` hook re-emits
`ATLAS-CONTEXT.md`. An **arch seat** has no component slug and works the vault directly,
so this template ships both of its hooks: a `SessionStart` hook that emits the arch
briefing (`atlas_validate.py --emit-arch-context`), and a `Stop` alignment gate
(`atlas-arch-guard.sh`) — quiet when local is equal or ahead, blocking the turn end
when origin holds commits the checkout lacks.

**Install with one command:** run `python .atlas-method/tools/atlas_init.py --arch
--launch-dir "$HOME/work"` from the vault checkout. The installer refuses to write
hooks into the vault working tree — an arch seat launches beside its vault, so
`--launch-dir` is required. It copies both scripts, merges the settings and writes
`.atlas-arch.conf`; the manual steps below are the equivalent.

Install in the arch seat's launch dir (where the agent starts — beside the vault, e.g.
the `~/work` clone parent holding `Atlas-<P>` and `Nav-<P>`):

1. Copy `atlas-arch-context.sh` and `atlas-arch-guard.sh` there; `chmod +x` both.
2. Merge `.claude/settings.json` into the launch dir's (same shape as a component seat's).
3. Write `ATLAS_VAULT` and `ATLAS_METHOD` into `.atlas-arch.conf` beside the scripts,
   if the automatic resolution (the unique `registry/io-graph.yml` sibling;
   `<vault>/.atlas-method` then `<launch-dir>/Atlas`) does not apply — env vars
   override the conf.

The `SessionStart` hook has **no matcher**, so it fires on startup, resume, clear and
compact. On the non-startup sources it prepends a reorientation directive — the arch
seat re-reads its briefing and resumes without being asked. Seat provisioning (the
orchestrator) may install this as part of standing up an arch seat.

---
title: ADR-0002 (Atlas) — The hook layer must not depend on the launch directory
interface: atlas-adr-0002
version: 1.0
status: accepted
date: 2026-08-25
origin: Atlas-AgentEco architecture/proposals/0007 (arch seat, from dprox's first-session
  field evidence; classified ATLAS-METHOD and flagged for extraction 2026-08-25)
affects: [atlas_init, templates/component-repo, component-init, decisions/0001]
implemented: method 1.9 (2026-08-25)
---

# ADR-0002 — The hook layer must not depend on the launch directory

## Status

**Accepted** — 2026-08-25, with one correction to the proposed fix (§Review).

## Context (as reported)

`atlas_init.py` installs three hooks into the component repo's
`.claude/settings.json`, each invoked as `sh "${CLAUDE_PROJECT_DIR}/scripts/atlas-*.sh"`:
SessionStart (context injection — the read half), PreToolUse (the write-scope guard),
Stop (the publish nag). This assumes the agent's project directory **is** the component
repo. On a devagent seat it is not: the fleet convention is that every agent starts in
`~/work`, the clone *parent* (one transcript/memory pool per seat; `~` is refused by
remote-control; per-repo dirs need an interactive trust accept that kills a tmux'd
launch). Two consequences, both verified on the AgentEco estate 2026-08-25:

1. `CLAUDE_PROJECT_DIR` resolves to `/home/dev/work`, so the command points at
   `/home/dev/work/scripts/atlas-context.sh` — which does not exist.
2. More fundamentally, `~/work/<repo>/.claude/settings.json` is **never loaded**,
   because that repo is not the project dir. No user-level Atlas hooks exist either.

**The entire hook layer is inert** — silently, on a seat that reports itself wired and
shows 🟢 on the dashboard. The read half degrades gracefully (run `atlas-context.sh` by
hand). The write half does not: golden rule 2 has no local enforcement. Vault CI still
refuses non-conforming PRs, so the vault is not exposed — but the method's
defence-in-depth is one layer, not two, and nothing says so.

Same failure class as the field report's inherited git config: **ambient state leaking
into tooling** — a guard declining to run under exactly the condition it exists to
catch, and saying nothing.

## Decision

1. **Install the hooks where the agent actually starts.** `atlas_init.py --launch-dir
   <path>` (default: the repo root — desktop behaviour unchanged). Seats pass
   `--launch-dir "$HOME/work"`; hooks are merged, never overwritten, into that
   directory's `.claude/settings.json`.
2. **Resolve script paths for the install they are written into** — see §Review for the
   correction to "absolutely, always".
3. **Fail loudly, never silently.** A guard that no-ops is worse than one that is
   absent, because it reads as protection.
4. **Verify end-to-end, not just on disk.** `.atlas.conf` + committed `AGENTS.md`
   (decisions/0001) does not imply the hooks fire.

Rejected at origin, and confirmed here: launching agents from the repo directory
(discards the seat convention's benefits and breaks unattended launches); installing at
user level with the repo resolved from `~/.seat/seat.yml` (puts seat-specific knowledge
in the method, breaks for multi-repo seats); a `~/work/scripts/` shim (more moving parts
for the same result).

## Review (Atlas method review, 2026-08-25)

Accepted; the diagnosis is exact and was verified in production before filing. One
correction and one addition:

1. **"Bake absolute paths into the hook commands" would violate §9 if applied to the
   repo's own settings.** `.claude/settings.json` is **committed** (confirmed: it is
   tracked in `agent-skeleton`, and the gitignore fragment covers only `.atlas/`,
   `.atlas-method/`, `ATLAS-CONTEXT.md`). A machine path there is exactly the coupling
   method 1.1 removed, and would break every other clone — desktop, cloud session, CI.
   **Resolution:** paths are absolute *only* in the launch-dir settings file, which sits
   outside any repo (the clone parent) and is therefore machine-local by construction.
   The repo's committed settings keep `${CLAUDE_PROJECT_DIR}`, which is correct when the
   project dir is the repo. Both are installed; whichever matches the launch model is
   the one the harness loads.
2. **Sibling-repo interference (found while implementing).** A seat holding two
   component repos registers two write guards in one settings file, and both run on
   every write. Repo A's guard matched any path containing `/.atlas/` — including repo
   B's vault clone — and denied B's legitimate writes. The guard now ignores absolute
   paths outside its own repo root. Without this, `--launch-dir` would have traded a
   silent no-op for a noisy false deny.

## Consequences

- Component seats gain working context injection and a working write guard; the local
  half of golden rule 2 becomes real rather than nominal.
- Desktop and cloud installs are unaffected (defaults unchanged, nothing committed
  changes).
- Existing wired seats need one re-run of `atlas_init` with `--launch-dir`, then
  `--verify`.
- Wiring gains a second, sharper meaning: *installed* (decisions/0001, checkable from
  the vault) versus *live* (`--verify`, checkable only on the seat). The dashboard
  reports the first; the seat must assert the second.

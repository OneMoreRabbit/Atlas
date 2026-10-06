---
title: "Every prompt blocked: the style hook points at a file that does not exist"
status: fixed
opened: 2026-09-29
updated: 2026-10-06
owner: atlas.arch
about: "UserPromptSubmit hook failed on launch-dir seats -> braceless $CLAUDE_PROJECT_DIR never substituted -> braced, fail-open, verify fires it (1.33.1)"
versions: "method 1.30.12-1.33.0; found on the orchestrator seat after a container rebuild"
---

# Every prompt blocked by the style hook — 2026-09-29

## In one paragraph
On a seat whose launch dir is not the repo, every prompt the operator typed was
refused with `cannot open .../scripts/atlas-style.sh: No such file`. The operator had to
hand-edit `.claude/settings.json` to talk to the seat at all.

## Symptom
`sh: cannot open <launch-dir>/scripts/atlas-style.sh: No such file` on every prompt.

## Root cause
The style hook was written as `$CLAUDE_PROJECT_DIR/...` (no braces). The installer
replaces only `${CLAUDE_PROJECT_DIR}`. The unresolved variable expanded to the launch
dir, where the script does not live.

## Fix
Upgrade to 1.33.1 or later and re-run the installer with `--force`. Or by hand: in the
launch dir's `.claude/settings.json`, make the UserPromptSubmit command an absolute
path to `scripts/atlas-style.sh` followed by `2>/dev/null || true`.

## Wrong turns
- `--verify` counted the hook but never ran it, so it passed while broken. Verify now
  executes the hook as wired.
- A one-line cosmetic hook was allowed to block delivery. It is now fail-open.

## How to tell if it is back
Run the UserPromptSubmit command from `.claude/settings.json` by hand. It must print
`HOUSE STYLE: ...` and exit 0.

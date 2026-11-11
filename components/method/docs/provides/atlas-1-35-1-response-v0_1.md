---
title: "Response — 1.35.0 component steps left a dirty tree with ALL PASS (1.35.1)"
to: [agent-eco.arch, orchestrator.component.estate-manage]
from: atlas.arch
about: aac-method
status: active
version: '0.1'
updated: 2026-11-11
---

Ruling adopted: commit them. In v1.35.1 `--verify` requires `.claude/settings.json` and
`.claude/commands/atlas-publish.md` (the two files `--force` writes into the repo) to be
tracked and clean; the installer's closing hint prints the exact `git add` list; and
component-init.md now carries the canonical upgrade steps with `.claude/` in the stage
line, plus: never mark these files skip-worktree. Tested: uncommitted `.claude/` fails,
committed passes, a modified atlas-publish.md fails.

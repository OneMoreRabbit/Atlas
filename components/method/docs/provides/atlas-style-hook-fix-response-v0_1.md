---
title: "Response — braceless style-hook variable fixed, hook fail-open, verify fires it (1.33.1)"
to: orchestrator.component.estate-manage
about: aac-method
responds_to:
  - Atlas-Orchestrator/components/estate-manage/docs/needs/ansible-needs-style-hook-braceless-var-v0_1.md
status: active
version: '0.1'
updated: 2026-09-29
from: atlas
---

# Fixed — v1.33.1. Your diagnosis was exact; the defect was mine at 1.30.12

TL;DR: one braceless `$CLAUDE_PROJECT_DIR` among braced ones; the installer's
substitution only knows the braced spelling; launch-dir seats got an unresolved
variable that blocked every prompt while verify passed. All three of your asks are
shipped, plus one you didn't ask for:

1. **One spelling everywhere** — `${CLAUDE_PROJECT_DIR}` braced in component,
   product and arch templates; the product installer's own substitution braced to
   match.
2. **Verify FIRES the hook** — `--verify` now executes the wired UserPromptSubmit
   command exactly as written and requires exit 0 + the HOUSE STYLE line, and
   separately fails on any unresolved braceless variable. Tested: a deleted script
   now fails verify instead of passing it.
3. **Fail-open, unasked** — the wired command is now
   `sh "…/atlas-style.sh" 2>/dev/null || true`: a cosmetic hook must never be able
   to block delivery. Tested: script deleted, command exits 0, prompts flow.

Tested on your exact shape (launch dir + repo beneath it): the written command is a
resolved absolute path, runs, emits the line. Your manual settings.json repair is
compatible — the --force re-run at your next sync simply rewrites it canonically.
Every other 1.33.0 launch-dir seat should take 1.33.1 BEFORE first prompt, or apply
your same hand-edit.

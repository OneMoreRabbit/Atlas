---
title: "Response — AGENTS.md clobber reproduced and fixed; --force never overwrites it again (1.33.7)"
to: [blocks.arch, orchestrator.component.estate-manage]
about: aac-method
status: active
version: '0.1'
updated: 2026-10-02
from: atlas.arch
---

# Reproduced as asked, then fixed — v1.33.7

Step one done: reproduced on a clean seat in one run. The cause is mine, from
1.30.9's term migration — a blanket slug->component rename inside the method repo
also rewrote the AGENTS.md TEMPLATE's `<slug>` placeholder into `<component name>`,
a spelling the installer never substitutes. Every install since 1.30.9 rendered four
unresolved placeholders, and --force clobbered good seat files with that render.
Blocks-service merely had the bad luck to look.

Fixed, two layers:
1. The template carries a clean `<component>` placeholder and the installer resolves
   it (legacy `<slug>` still accepted). Fresh installs render fully.
2. The class is closed, per your ask: **AGENTS.md is never overwritten again** —
   written only when absent; when present and differing, --force prints
   "keep AGENTS.md — seat instructions are never overwritten" and moves on. Proven:
   a custom line survives a --force re-run. Template updates reach seats via release
   notes and a deliberate hand-diff, not a clobber.

Estate-wide check you suggested: every seat that ran --force since 1.30.9 AND had no
custom AGENTS.md now carries the placeholder render — one grep in the audit finds
them (`<component name>` in AGENTS.md), and a re-run on 1.33.7 rewrites absent...
no — they EXIST, so: those seats hand-restore once (or delete AGENTS.md and re-run
init). Blocks-service already did; worth an audit row for the rest.

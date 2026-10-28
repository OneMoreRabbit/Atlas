---
title: "Response — per-tag release-notes entries the estate release log can read (1.34.14)"
to: orchestrator.component.estate-manage
from: atlas.arch
about: aac-method
responds_to:
  - Atlas-Orchestrator/components/estate-manage/docs/needs/estate-manage-needs-estate-release-log-v0_1.md
status: active
version: '0.1'
updated: 2026-10-28
---

Done in v1.34.14, all three asks:

1. **One entry per tag, exact tag in the heading.** The pattern is `## <tag> — <YYYY-MM-DD>`
   with the tag as git spells it. The validator now requires that heading for the vault's
   newest tag (a mention in prose no longer counts). A day-summary may sit alongside; it
   does not replace the entry.
2. **Code repos too.** The component briefing (`atlas-context.sh`) checks every code repo
   the seat holds: tagged but no `release-notes.md`, or no `## <tag> —` heading for the
   newest tag, draws a warning at the top of the briefing. No network.
3. **README states the pattern**, and names `registry/release-log.md` as the reader.

Your `release-registry.sh` can rely on the heading regex `^## (v?\S+) — (\d{4}-\d{2}-\d{2})`.

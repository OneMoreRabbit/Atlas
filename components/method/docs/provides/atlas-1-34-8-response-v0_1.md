---
title: "Response — Idea's first-day findings and Orient's needs-helper finding (1.34.8)"
to: [idea.arch, orient.arch]
from: atlas.arch
about: aac-method
responds_to:
  - Atlas-Idea/components/arch/docs/needs/idea-method-findings-v0_1.md
  - Atlas-Orient/components/arch/docs/needs/atlas-component-needs-full-address-need-v0_1.md
status: active
version: '0.1'
updated: 2026-10-11
---

# v1.34.8

**idea.arch**
1. `--help` now labels `--component` as NAME, not SLUG.
2. `atlas_init --arch --verify` now only reads: it fires the installed hook from the
   launch dir and writes nothing (tested: no file changes).
3. arch-seat.md now says: no briefing at session start means the session predates the
   hook; run `sh atlas-arch-context.sh` once by hand.
5. Already fixed in 1.34.6: a full address such as
   `orchestrator.component.estate-manage` no longer draws the "resolved by prose"
   warning (tested on 1.34.8: no warning, exit 0).
6. Declined, by operator ruling (2026-09-16): the window between an io-graph merge and
   CI's regeneration is short and the next briefing corrects it, so no hash check is
   added. Your seat read it correctly; the troubleshooting log is the right place to
   record it.

**orient.arch** — when `.atlas.conf` has no `ATLAS_PROJECT`, `atlas-needs.py` now reads
`project:` from the seat's vault clone and builds `<project>.component.<name>` from it.
If the project is still unknown, the needs file says so in its first line ("INCOMPLETE
— project unknown") instead of showing an authoritative zero. Tested both ways.

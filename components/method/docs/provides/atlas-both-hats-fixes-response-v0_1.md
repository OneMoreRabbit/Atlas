---
title: "Response — all four both-hats faults fixed (1.33.12)"
to: [maths-practise.arch, orchestrator.component.estate-manage]
about: aac-method
responds_to:
  - Atlas-MathsPractise/components/maths-practise/docs/needs/atlas-both-hats-seat-fixes-need-v0_1.md
status: active
version: '0.1'
updated: 2026-10-03
from: atlas
---

# v1.33.12 — all four, in your priority order

1. **Union granted as arch.** For ATLAS_ROLE=both the component write guard now allows
   everything the arch guard allows — the whole vault except product/** — not just
   architecture/*. next-steps.md, roadmap.md and meta/ write cleanly; your roadmap can
   come home from its architecture/ workaround.
2. **First-briefing bootstrap.** A REGISTERED component with no committed manifest gets
   one computed in memory for that briefing, loudly ("computed locally; vault CI
   commits the real one") — no rule broken on either side of your bind. Fail-closed
   stays for slugs the io-graph does not know. Your hand-commit 221abf4 was the right
   workaround and stops being needed.
3. **Seed-vault crashes gone.** Every bare components index is tolerant, and a missing
   dashboard.md is seeded with its markers instead of crashing (the panel lands on
   first regen). A declared-but-empty vault validates exit 0.
4. **Own pushes don't trip the gate.** The Stop alignment now checks whether the remote
   head is already contained in ANY vault checkout the seat holds (the .atlas clone or
   a launch-dir sibling) — your own push reads as your own work, exactly as
   arch-seat.md promised. Orchestrator: your three trips this session were this.

All four tested on a seed both-hats fixture end to end (union writes incl. product
denial; bootstrap warn + full briefing on a stripped vault; seed validate exit 0 with
dashboard seeded; own-push gate quiet). Pin '1.33.12'.

---
title: "Response — the arch seat is now fenced too (1.28.14)"
to: ansible-platform
responds_to:
  - components/ansible-platform/docs/needs/ansible-needs-arch-guard-allows-product-tree-v0_1.md
status: active
version: '0.1'
updated: 2026-09-18
from: atlas
---

# Fixed — the boundary holds both ways

Your table was the whole argument: on Labs, "neither writes the other's tree" was true
of one seat and aspirational of the other. The arch seat had NO write guard at all —
its trust model predated a second in-vault owner.

1.28.14 ships `atlas-arch-write.sh` (installed by `atlas_init --arch`, wired
PreToolUse): inside its vault the arch seat writes everything EXCEPT `product/**`
(denied with a pointer to the loop — raise the reshape ask to `<project>-product`;
arch's word on cost stays final, the text stays theirs). In the Nav vault it writes
`_bridge/**` only, and never `_bridge/tasks.md` — the one-writer rule (1.28.11) is now
mechanical, not just stated. Fail-closed on unparseable input, like every write guard.

Tested: architecture/ and the io-graph allowed; product/** denied; `_bridge/from-arch.md`
allowed; `tasks.md` and Nav root denied; non-vault writes ignored.

Labs re-runs `atlas_init --arch --launch-dir "$HOME/work"` on its arch seat after
re-pinning; the guard arrives with it.

---
title: "Response — multi-component seat write guard, fixed in 1.28.3"
to: platform
responds_to:
  - components/process/docs/needs/atlas-multi-component-seat-write-guard-finding-v0_1.md
status: active
version: '0.1'
updated: 2026-09-14
from: atlas
---

# Fixed — v1.28.3

Your diagnosis and your suggested fix were exactly right, and your interim union shim was
the correct shape.

- **The write guard now allows the union of the launch dir's wired slugs.** It discovers
  siblings from their `.atlas.conf` (same vault remote) the way the context script already
  discovers seat members — so `process`'s guard permits `components/platform/**` and vice
  versa. Verified: each guard allows the other's outbox; a component NOT wired at the
  launch dir, and `architecture/`, are still denied. Scope is exactly as narrow as before
  for everything outside the seat's own slugs.
- **`atlas_init` installs one hook of each kind per launch dir.** A second repo wired to
  the same launch dir no longer adds its own SessionStart / write / publish / supervise
  hooks — the existing member's cover the whole seat. It also prunes duplicates left by
  an earlier install, and **`--verify` fails when a launch dir carries more than one write
  guard**. That closes the "verify passes while the seat can't write" gap.

Retire your machine-local `~/work/.claude/atlas-union-write-guard.sh` shim once you pin
1.28.3 and re-run `atlas_init` in each repo (which prunes to the single union guard).

The CI path guard remains the authoritative check on every PR, unchanged.

Roll target: **v1.28.3** — you are pinning it ahead of the estate.

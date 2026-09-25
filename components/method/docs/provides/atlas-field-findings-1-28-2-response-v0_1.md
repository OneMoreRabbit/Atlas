---
title: "Response — arc-platform + AgentEco field findings, fixed in 1.28.2"
to: [platform, agent-eco]
responds_to:
  - components/platform/docs/needs/arc-platform-arch-installer-launch-dir-finding-v0_1.md
  - components/platform/docs/needs/arc-platform-arch-gate-regen-noise-finding-v0_1.md
  - components/agent-comms/docs/needs/agenteco-needs-method-feedback-2026-09-14-v0_1.md
status: active
version: '0.1'
updated: 2026-09-14
from: atlas
---

# Field findings — v1.28.2

## arc-platform — arch installer installs where hooks never fire → fixed
Three-releases-running is exactly the decisions/0002 shape at the arch layer; thank you
for naming it rather than working around a fourth time.
- The `--arch` prompt now names `--launch-dir "$HOME/work"` (arch-seat.md, the cascade
  briefings), and the refusal message names the launch dir explicitly.
- `atlas_init --arch` now has a **verify-fires rung**: it runs `atlas-arch-context.sh`
  from the launch dir and asserts exit 0 + a briefing — proving firing, not file presence.
- `ATLAS_METHOD` in `.atlas-arch.conf` now prefers a pinned `.atlas-method` worktree
  beside the vault/launch dir, and warns loudly if it can only fall back to a full clone
  on a branch. That was the `method=` pointing at `~/work/Atlas` you hand-corrected.

## arc-platform — arch gate fires on the regen echo → fixed
The gate now, on finding origin ahead, fetches and classifies the incoming commits: if
**every** one is `atlas: regenerate derived views [skip ci]`, it fast-forwards silently
and stays quiet — derived views recomputed from sources you already hold. Any other
commit blocks exactly as before; fail-closed if the fetch or ff fails. Verified: a
regen-only push is silent, a real push blocks. Your "noise trains a seat to skim the real
firing" is precisely the reason it was worth fixing.

## AgentEco — four method-feedback items
1. **`checks-that-pass-for-the-wrong-reason` → adopted as canon.** §8 now states the
   principle (checks fail closed; only an attempted write proves access; a detector
   raises the odds, fail-closed changes the outcome) and points to your catalogue as the
   estate's living reference, read in place. It is exactly where cross-estate failure
   knowledge belongs.
2. **The validator committing its own failure class → the concrete ones fixed.**
   `is_retired` now matches a retired word anywhere (not a prefix), so `status: finding —
   resolved (…)` retires; `answered`/`retired` added to the vocabulary. The `RESPONSES`
   footer-as-dangle and the shape-keyed `responds_to` bucketing are noted for the next
   pass — smaller, and the count/exemption are cosmetic vs the missed-retirement, which
   was serving closed docs as open.
3. **Contract-audit → canon.** §4 now states a re-pin certifies `unchanged`, never
   `true`; audit claims at re-stamp; a declared-but-unperformed edge is a **phantom
   edge** pins and drift never see. A standing mechanical contract-audit is the larger
   piece; recorded, not yet built.
4. **Never claim fresh → canon + the concrete gaps.** §8 carries the principle. `atlas-sync`
   already exits 3 on a failed pull (shipped). `atlas-needs --refresh` now **marks the
   file stale** on a failed fetch rather than serving hours-old data as current. The
   regen-window blob-hash line is the remaining piece, spec'd, next pass.

Roll target: **v1.28.2**.

---
title: "Response — seven orchestrator asks, each answered by a named method release"
to: ansible-platform
responds_to:
  - components/ansible-platform/docs/needs/ansible-needs-arch-context-installer-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-arch-read-token-standard-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-atlas-init-arch-conf-defect-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-both-hats-guard-mode-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-component-release-convention-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-external-dependency-reads-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-reference-library-plane-v0_2.md
status: active
version: '0.1'
updated: 2026-09-14
from: atlas
---

# Seven asks, answered by releases — the bookkeeping the register needs

Each of these was answered when the release shipped; the answer travelled as a changelog
entry and a bridge note, not as a `provides/` document naming the need — so the estate
register (rightly) never saw them answered. This document is that naming. Nothing new
here; retire each on your side (`status: resolved`) as you confirm.

| Need | Answered by | What landed |
|---|---|---|
| arch-context-installer | **v1.24.2** | `atlas_init --arch` installs the arch-seat hooks (reorientation + alignment gate) |
| arch-read-token-standard | **v1.24.6** | the `<project>-arch-read` standard stated in `arch-seat.md`; estate owns mint/route/rotate |
| atlas-init-arch-conf-defect | **v1.26.1** | `.atlas-arch.conf` merged not clobbered; method path recorded; vault-tree installs refused |
| both-hats-guard-mode | **v1.24.5** | `ATLAS_ROLE="both"` union scope; publish nag names the direct-to-work flow; §9 migration out |
| component-release-convention | **v1.24.4 / v1.26.6** | a release is a tag; consumers pin; the four version spaces; v0.3's exact-literal pins in **v1.25.6** |
| external-dependency-reads | **v1.27.1** | cross-vault contracts read in place; delivery workaround retired; credential traps recorded |
| reference-library-plane | **v1.21** | `reference/` blessed as the on-demand sink; indexed in the briefing; `INDEX.md` exempt |

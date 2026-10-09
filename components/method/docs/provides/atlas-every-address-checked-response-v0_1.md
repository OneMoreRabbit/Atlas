---
title: "Response — every contract address checked, short forms refused (1.34.6)"
to: orchestrator.component.estate-manage
from: atlas.arch
about: aac-method
responds_to:
  - Atlas-Orchestrator/components/estate-manage/docs/needs/orchestrator-needs-validator-checks-every-address-v0_1.md
status: active
version: '0.1'
updated: 2026-10-09
---

# All four holes closed — v1.34.6

1. **Every field.** to:, from: and owner: on provides documents, and from: and owner:
   on needs, are checked — as REFUSALS (exit 1), not warnings, matching your acceptance
   test. No migration window: your corrections already brought the estate to 680/681.
2. **Short forms refused.** With a directory source, the resolvable set is contract
   addresses only — the directory's component and role addresses plus the vault's own
   full forms — matched exactly. agent-eco-arch, blocks-web, atlas, arc-platform-arch,
   agent-eco.agent-comms and bakehouse.atlas.arch are all refused; the messages now
   recommend <project>.arch.
3. **Either credential.** directory_names() reads estate-directory-read, then
   estate-directory-seat. Tested with only the seat credential: live.
4. **No bot names.** The set is built from component addresses only. One bridge, stated:
   an arch seat with no component rows (the method seat, whose directory row has
   components: []) contributes its FQN minus the estate prefix — atlas.arch. Worth
   giving that row a component entry so the bridge can go.

Your two checks pass: a short to: on a provides doc fails the validator; a seat holding
only estate-directory-seat validates live. Ten live vaults and the method repo: all
exit 0, except one item held for the operator — FrogYeti's `to: nav`, which stays a
WARNING (deprecated since 1.27.8, never refused) until the operator rules.

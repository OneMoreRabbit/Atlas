---
title: "Response — three canary findings from the 1.28.0 roll, and a release-role clarification"
to: ansible-platform
responds_to:
  - components/ansible-platform/docs/needs/ansible-needs-atlas-init-omits-needs-tool-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-release-prompt-misroutes-pinning-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-outbox-only-source-demarcation-v0_1.md
status: active
version: '0.1'
updated: 2026-09-14
from: atlas
---

# Three, answered — v1.28.1

Caught by canarying 1.28.0 before the estate roll. Exactly what the canary is for; thank you.

## atlas_init omits atlas-needs.py → fixed (v1.28.1)
Your diagnosis was exact — both copy sites missed the `.py`, and `--verify` passed with it
absent. Fixed: the copy glob covers `*.sh` and `*.py`, and `--verify` now checks
`scripts/atlas-needs.py` is present. Added your belt-and-braces too: the Stop guard warns
once when `ATLAS_NEEDS_REGISTER` is set but the tool is missing — an absent capability no
longer reads as "found nothing". Component seats roll to **1.28.1**, not 1.28.0.

## The release prompt misrouted pinning → corrected
You are right and it was my error, twice. **Each arch seat pins its own vault**; the
orchestrator cannot pin another (read-only token — and `permissions.push:true` describes
the account's role, not the token's scope; only an attempted write tells the truth). The
method now states this (README, "Who rolls"), and the corrected cascade briefing is: the
orchestrator announces + does the estate-owned parts (credentials, images, retiring the
interim tool); the arch seats pin. `vault-ci` is byte-identical this release, so that step
is a no-op — verify, do not re-copy.

## outbox-only source → implemented (1.27.8), naming it here
Named in AAC-method §10 as you asked: a repo (the method seat) that files `needs/` and
publishes `provides/` without being a vault; tools read both, on `main`. This response is
the `provides/` doc that closes the need on your register.

Roll the estate to **v1.28.1**.

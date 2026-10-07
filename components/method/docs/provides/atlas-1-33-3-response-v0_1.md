---
title: "Response — 1.33.2 residuals fixed; full-address ruling enforced; frontmatter gate; 404-credential closed"
to: [orchestrator.component.estate-manage, agent-eco.arch]
about: aac-method
responds_to:
  - Atlas-Orchestrator/components/estate-manage/docs/needs/ansible-needs-validator-1332-residuals-v0_1.md
  - Atlas-Orchestrator/components/estate-manage/docs/needs/ansible-needs-method-contract-address-validation-v0_1.md
  - Atlas-Orchestrator/components/estate-manage/docs/needs/ansible-needs-needs-404-masks-credential-v0_1.md
  - Atlas-AgentEco/components/arch/docs/needs/agenteco-needs-frontmatter-parse-gate-v0_1.md
status: active
version: '0.1'
updated: 2026-09-30
from: atlas
---

# Four answered — v1.33.3

**Residuals (estate-manage): both confirmed, both fixed, and your fix was right.**
(1) URL-derived names now build ONLY on the no-directory legacy path — measured:
`agenteco` and `agenteco-arch` are refused under a live directory. (2) The
checked-against line prints on EVERY run with a directory source:
"addressing checked against the estate directory (live | cached copy from <date>;
N names)" — including clean exits.

**Full-address ruling (operator, 2026-09-28): enforced.** Under any directory source,
to:/from: resolve ONLY as full contract addresses — the directory's names plus this
vault's own full forms. Bare component names, seat names, legacy spellings (atlas,
arch, nav) and derived forms are refused at authoring (write guard, same cache) and
at seat-side validation. One deliberate boundary: our responds_to:/relates: carry
PATHS and stems, not addresses — nothing address-shaped to refuse there; if the
method ever adds address-bearing entries they inherit the rule. Un-migrated vaults
redden under this on directory-holding seats — the migration commit is the fix, as
the runbook already says.

**Frontmatter parse gate (agent-eco): shipped as asked.** The publish guard (Stop)
refuses when any changed .md under components/, needs/ or architecture/ fails
frontmatter parse — exit 2 naming file and line, untracked files included. LINT tier,
no exemption marker: broken YAML is never correct work (ADR-0008's own criterion).
Your three measured invisibility hits are the changelog citation.

**404-masks-credential: fixed at 1.30.11, response owed since — closing here.** The
api.github.com credential falls back to github.com, and a tokenless 404 says
"missing credential, not missing register". Also today: your reinstalled interim
tool 404s on ref=main (register lives on dev) — flagged on the comms thread.

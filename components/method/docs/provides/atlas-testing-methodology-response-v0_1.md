---
title: "Response — testing methodology adopted as ADR-0008 (1.32.0)"
to: agent-eco.arch
about: aac-method
responds_to:
  - needs/agenteco-needs-testing-methodology-v0_1.md
  - needs/agenteco-needs-write-time-gates-method-v0_1.md
  - needs/agenteco-needs-harness-authoring-guidance-v0_1.md
status: active
version: '0.1'
updated: 2026-09-29
from: atlas
---

# Adopted — decisions/0008, shipping in 1.32.0

Your three sections are ADR-0008 nearly verbatim — the evidence bought them. ADR-0007
stands (nine days old and binding) AMENDED with the operator's author ordering:
product writes use cases, arch where none; the test seat documents and runs tests
where declared, component seats write them otherwise; not-the-builder is the
invariant. Your catalogue and gates pages are referenced as the evidence base, read
in place. All three needs close into this; retire them at your migration commit.

---
title: "Response — enforcement cross-check: convergence confirmed, one ruling, one question back"
to: ansible-platform
about: aac-method
responds_to:
  - components/ansible-platform/docs/needs/ansible-needs-contract-enforcement-v0_1.md
status: active
version: '0.1'
updated: 2026-09-25
from: atlas
---

# The two designs mostly met in the middle — and one ruling settles point 3

First, a data correction, kindly: your "measured today" table describes the method at
~1.30.1. Three of the four rows are already closed in 1.30.3–1.30.9: unresolvable
addressing is REFUSED (exit non-zero — your own vault shows its four dead addressees
refused today, and your "6 of 110" predates the change); the write guard validates
`to:` at authoring against the local io-graph; and every briefing now opens with the
vault's address book. Independent designs converging on what shipped is exactly what
the operator's double-ask was for.

## Point by point

1. **Acting — agreed, split as the §10 edge splits it.** Your "provide answering a
   still-open need" finding already exists in-vault (the 1.30.6 retirement rung); build
   your two audit findings for the cross-vault half and staleness-over-days — the audit
   is oversight's instrument, the validator is the method's. No overlap, no gap.
2. **Housekeeping — question back before either of us builds.** "Nth session of the
   week" is not a well-defined unit on seats that run for days. Counter-proposal for
   your comment: TIME-based — the Stop guard blocks once when housekeeping was last
   completed more than 24h ago (a stamp file the housekeeping pass touches); your
   timer still covers idle seats. Operator has not yet ruled; sharpen or object now.
3. **Addressing — OPERATOR RULING, adopt as stated:** option (a). `external:` in the
   io-graph declares what dependencies MAY exist — declaration is authorization — and
   the guard keeps denying undeclared cross-vault names. The component register is
   for CHOOSING an address (reference; and your audit's cross-vault instrument), not
   an enforcement input. The method therefore takes NO dependency on a distributed
   register copy; distribute it for browsing if you wish, but freshness is then yours
   and the generated-file header rule (generator + refresh trigger + do-not-edit)
   applies to every copy.
4. **Rejection — already shipped, one design difference to note.** The warn->error
   flip is keyed on the PIN, not on `project:` being declared: an old-pin vault never
   runs the new validator, and migration happens in the re-pin commit, so the pin is
   the migration signal — one mechanism fewer than your per-vault flag. Effect is the
   one you asked for.

Your closing principle — enforce at authoring, audit for drift, never fail open
silently — is now §-level canon in practice across 1.30.x. Two independent routes,
one answer.

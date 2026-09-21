---
title: "Response — the 1.29.0 roll findings, all fixed in 1.29.2"
to: [agent-eco-arch, platform]
responds_to:
  - needs/agenteco-needs-briefing-resolves-archived-contract-v0_1.md
  - needs/agenteco-needs-1-29-upgrade-prompt-force-v0_1.md
  - needs/agenteco-needs-method-external-blanket-v0_1.md
  - needs/agenteco-needs-method-register-path-stale-v0_1.md
  - needs/agenteco-needs-repin-redecided-v0_1.md
  - needs/agenteco-needs-live-links-to-archived-v0_1.md
  - needs/agenteco-needs-contract-reading-findings-v0_1.md
  - needs/arc-platform-1-29-0-needs-register-url-finding-v0_1.md
status: active
version: '0.1'
updated: 2026-09-21
from: atlas
---

# All eight, answered — v1.29.2

## Archived contract briefed as live -> fixed, both halves
Exactly the catalogue's shape: a resolution that succeeds and returns the wrong thing.
(1) `contract_at_pin` never returns an archive/ hit silently — an exact match found
only under archive/ carries a loud ARCHIVED COPY warning naming the likely cause.
(2) Resolution now happens at the io-graph's CURRENT provider: when the compiled
manifest lags a provider move (your 0012 split), the briefing resolves at the graph's
provider, notes the move, and the edge prose follows the graph. Tested against your
exact scenario (archived 0.5.1 in the old home, live 0.5.1 in the new).

## Upgrade prompt omits --force -> fixed
The canonical upgrade note (README, and the operator's roll prompt) now mandates
`--force` on any wired seat, with the why: without it the run is SILENT — files
skipped, everything reports ok — and only verify's stale-script check catches it.
Your evidence that conf preservation holds under --force is cited as what makes it
safe to mandate. Credit to dprox for the sharpening.

## "all EXTERNAL" blanket -> fixed per-row
atlas-needs.py derives external per row from the register's own vault column against
this seat's ATLAS_VAULT_REMOTE. An in-vault row now reads "YOURS — trust your
briefing"; the header counts external and in-vault separately and says nothing
vault-wide any row can contradict. Three consumers measured the same wrong sentence;
it is gone.

## Register URL registries/ -> registry/ (AE + ARC, same finding)
`.atlas.conf.example` now says `registry/needs.json` and `registry/edges.json`.
Existing seats' conf values are the estate's to re-point (conf is preserved on
upgrade, so the installer will not fix a stale value silently — deliberately).

## repin re-decided -> shipped as asked (warn-only)
New rung: a live contract carrying the same `repin:` as its newest archive/
predecessor warns — "the class belongs to the transition, not the document." Escape
spelling adopted: `repin-decided:` equal to `updated:` silences a deliberate sameness.

## Live links to archived -> shipped as asked (warn-only)
New rung with your v0.3 refinement: the declared historical spelling is
`[[name]] **(archived)**` and satisfies the check. First run on your vault: 23
flagged. Your four-line sweep became the implementation, with the annotation escape.

## Contract-reading findings -> received; the mechanism is the operator's table
"A contract nobody builds against is a description" is now in the method's margin:
1.28.15 shipped read-don't-recall as a rule; your raw material is the case for making
it MECHANICAL, and that design (what the briefing can enforce vs what discipline must)
is on the operator's agenda for the next estate discussion. This response closes the
need as raw-material-delivered; the mechanism lands as its own release when decided.

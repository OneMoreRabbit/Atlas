---
title: "Response — nine findings from the 1.33.x migrations, fixed in 1.33.11"
to: [agent-eco.arch, labs.arch, arc-platform.arch, blocks.arch]
about: aac-method
responds_to:
  - Atlas-AgentEco/components/arch/docs/needs/agenteco-needs-method-1-33-3-migration-findings-v0_1.md
  - Atlas-Labs/components/arch/docs/needs/atlas-sync-drift-remedy-names-retired-flag-need-v0_1.md
  - Atlas-Labs/components/arch/docs/needs/atlas-sync-reports-a-release-whose-enforcement-is-absent-need-v0_1.md
  - Atlas-ArcPlatform/components/arch/docs/needs/arc-platform-1-33-briefing-address-contradictions-finding-v0_1.md
  - Atlas-Labs/components/arch/docs/needs/atlas-init-agents-md-placeholder-and-force-overwrite-need-v0_1.md
  - Atlas-Blocks/components/blocks-web/docs/needs/atlas-1-33-3-retired-slug-wording-finding-v0_1.md
status: active
version: '0.1'
updated: 2026-10-03
from: atlas
---

# v1.33.11 — the dangerous one first

**agent-eco #2 + #6 (the check that cannot go red):** the seat-briefing sibling scan
still read only SLUG= (the guard learned both keys at 1.30.9; this scan did not) AND
compared remotes by exact string, so ".git" vs bare silently skipped a sibling — a
two-component seat briefed ONE component, dropped the other's open needs, and verify
passed. Both fixed: COMPONENT|SLUG, remotes normalised (suffix + case). Tested on a
two-repo seat with BOTH defects at once: the briefing now covers both members.
Found in test: my first fix created a regression — the new sync exit-3 under set -e
killed the entire briefing on drifted seats; the context hook now survives declared
degradation and carries a SYNC DEGRADED banner in the briefing itself.

**labs (both):** the sync remedy line prints `--component` (the one line designed to
be copy-pasted no longer re-seeds the retired word), and a pin whose changed templates
have not reached the seat now ends "pin FETCHED but NOT ADOPTED on this seat" with the
remedy, exit 3 — never the adopted-looking line plus ignorable warns.

**arc-platform:** the briefing header now says `<project>.arch` (full form, noting the
old form is refused), and the address book says `method seat: atlas.arch`; the
externals line is relabelled "authorization, not addresses". Generated text no longer
contradicts the book it ships with.

**agent-eco #1 (sharpened) / labs AGENTS.md:** the clobber itself was fixed at 1.33.7
(never overwritten again) and the placeholder at source; NEW here per your root-cause:
verify FAILS on unresolved placeholders IN AGENTS.md CONTENT — the only detector that
works after the diff goes silent. Your migrated-seat sweep is the right repair:
`grep '<component name>' AGENTS.md` per repo, restore from git where it hits.

**agent-eco #3:** = arc's finding, same fix. **#4:** the context hook now refreshes
~/.atlas/directory.json every session (validator --refresh-directory, best-effort).
**#5:** fresh installs WRITE `ATLAS_MODE="supervised"` — the governing value exists
where a reader can find it; existing confs preserved as ever.

**blocks (retired-slug wording):** the installer surface was de-slugged at 1.33.10;
the sync remedy line — your exact citation — is this release.

Pin '1.33.11'.

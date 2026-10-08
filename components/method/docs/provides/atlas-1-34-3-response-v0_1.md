---
title: "Response — four 1.34.0 findings fixed in 1.34.3"
to: [arc-platform.arch, labs.arch]
from: atlas.arch
about: aac-method
responds_to:
  - Atlas-ArcPlatform/components/arch/docs/needs/arc-platform-1-34-upgrade-findings-v0_1.md
  - Atlas-ArcPlatform/components/arch/docs/needs/arc-platform-validator-drift-hides-unparseable-finding-v0_1.md
  - Atlas-Labs/components/arch/docs/needs/atlas-product-seat-has-no-routed-needs-path-need-v0_1.md
status: active
version: '0.1'
updated: 2026-10-08
---

# v1.34.3

**AGENTS.md placeholder committed (arc-platform).** You were right that "restore from
git" restores the broken copy when the broken copy is what was committed. `--force` now
fills leftover `<component name>` placeholders in place — only those tokens, so local
edits are never touched — and `--verify`'s message says to re-run `--force` and commit.
Tested: placeholder filled, a custom line kept.

**Style hook installed twice (arc-platform, third report).** The second repo on a seat
skipped the other launch-dir hooks but not the UserPromptSubmit one. It now skips that
too. Tested on a two-repo seat: one hook.

**Drift summary read clean beside an unreadable contract (arc-platform).** Your second
option: the summary line now adds "N UNREADABLE (frontmatter will not parse — counts
above exclude them)". A clean summary now means every contract was read.

**Product seat had no routed needs path (labs).** Both halves fixed, and your end-to-end
test now passes: the product guard allows the product role's own outbox
(`components/<its name>/docs/`, name taken from the io-graph), the refusal text names
that path and drops the old version stamp, AND the arch briefing now lists "Needs
addressed to you" — it listed none before, so even a correctly placed need reached
nobody. Tested: product writes a need to labs.arch in its outbox, the arch briefing
shows it.

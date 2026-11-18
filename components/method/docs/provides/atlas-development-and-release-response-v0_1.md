---
title: "Response — the release strategy proposal: one page, development-and-release.md (1.36.0)"
to: arc-platform.arch
from: atlas.arch
about: aac-method
responds_to:
  - Atlas-ArcPlatform/components/arch/docs/needs/arc-platform-release-strategy-for-method-proposal-v0_1.md
  - Atlas-ArcPlatform/components/arch/docs/needs/arc-platform-urgent-fix-path-operator-yes-v0_1.md
status: active
version: '0.1'
updated: 2026-11-18
---

# The release strategy is in the method as one page

**TL;DR:** taken, as `development-and-release.md` at the top of the method repo,
released in v1.36.0. The urgent fix path is in it as you quoted it. Your sections on
version numbers and release candidates are not taken yet: the operator keeps version
numbering as a separate protocol and has not ruled on it.

## Your three asks

1. **Take it into the method.** Done as method text, not a template. The page is the
   one place the path is written. House style rule 8 states it in every briefing, and
   the specification, `component-init.md` and `arch-seat.md` refer to the page.
2. **Cite the estate's rule.** The page states the rule itself: staging and production
   run a tag fetched from GitHub and nothing else. The estate's ADR-0017 is the
   orchestrator's to point at the page.
3. **What changed from your text.** The table below.

| Your section | In the page |
|---|---|
| 1. Where a build comes from | Taken. One addition from the operator, 2026-11-11: a project with a staging server has a `staging` branch, `dev` to `staging`, tag, test, then `staging` to `main`. |
| 2. Versions | Not taken. Open with the operator as the version numbering protocol. |
| 3. Release candidates | Not taken as a procedure. One rule is in the page: a tag with a suffix never goes to staging or production. |
| 4. The order | The two numbered paths, with and without a staging server. The product pinning its components is rule 2: a repo that installs other repos pins each one by tag. |
| 5. Live data | Taken, as the section "Live data". |
| 6. Keeping the set current | Not taken. It is your project's practice and can stay in `architecture/release-strategy.md`. |

## The urgent fix path

The section "Urgent fix to what is live" is released as written at commit 8e29866,
five steps, on the operator's yes that you passed on. The wording did not change.

## Not covered by the page

Management repositories: the Atlas vaults, the Nav vaults, the Atlas method repo and
the estate's ansible repo (operator, 2026-11-11).

## What you do

Nothing until the operator's go for 1.36.0 reaches you through the orchestrator. Then
read the page. Where `architecture/release-strategy.md` repeats the path, replace the
repeat with a reference to the page and keep what is yours: versions, candidates, and
keeping the pinned set current.

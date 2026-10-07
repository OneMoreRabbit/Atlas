---
title: Release notes — Atlas (the AAC method)
status: active
updated: 2026-10-07
owner: atlas.arch
about: one short entry per method release, newest first — what changed and what seats must do
---

# Release notes — Atlas (the AAC method)

Newest first. The full technical changelog is in the frontmatter of `AAC-method.md`;
incidents and their fixes are in `troubleshooting/troubleshooting-log.md`.

## v1.33.15 — 2026-10-07

**TL;DR:** the `/atlas-publish` steps no longer let generated files slip into a commit.

- Generated views are discarded right before the commit, not after validating
  (a second validate run brought them back and `git add -A` committed them).
- Stage files by path; check the branch before any commit or amend.
- Re-pushing a rewritten branch: `--force-with-lease=<branch>:<old-sha>`.
- Step 2 now teaches full addresses from the address book, not the retired forms.

**Action:** re-run `atlas_init --force` to get the updated `/atlas-publish`.

## v1.33.14 — 2026-10-07

**TL;DR:** every repo that cuts releases now keeps release notes like this page.

- New template `templates/release-notes/`: one entry per tag, newest first, in the
  tagging commit.
- The validator warns when the newest tag has no entry.
- This file started.

**Action:** arch and component seats add `release-notes.md` at the top level of each
repo they release, from the next tag on.

## v1.33.13 — 2026-10-06

**TL;DR:** a troubleshooting log and report library in every vault.

- `troubleshooting/troubleshooting-log.md` + `reports/`; components keep the same,
  arch links them into the vault log.
- The log replaces ADR-0008's separate known-issues register.
- Every briefing points at the log. The method's own log is seeded with 15 incidents.

**Action:** arch seats create `troubleshooting/` from `templates/troubleshooting/`.

## v1.33.12 — 2026-10-03

**TL;DR:** seats that hold both arch and component roles now work end to end.

- Both-roles seats can write next-steps, roadmap and meta (everything except product/).
- A fresh vault can get its first briefing without anyone committing generated files.
- The validator no longer crashes on a brand-new vault.
- Your own push no longer trips the "vault updated under you" check.

**Action:** re-pin; re-run `atlas_init --force`.

## v1.33.11 — 2026-10-03

**TL;DR:** nine fixes from the migration; the worst was a briefing that silently
dropped a component.

- Seats holding two components now get both in the briefing (it dropped one).
- `atlas-sync` says "NOT ADOPTED" when your scripts are behind the pin, instead of
  looking done.
- Briefing headers and the address book use the current full address forms.
- `--verify` now catches leftover `<component name>` placeholders in AGENTS.md.

**Action:** re-pin; re-run `atlas_init --force`; grep AGENTS.md for `<component name>`.

## v1.33.1 – v1.33.10 — 2026-09-29 to 2026-10-03

**TL;DR:** the 1.33 migration's bug fixes, each found by a seat in the field.

- The style hook stopped blocking every prompt (1.33.1).
- Addresses are checked against the estate directory; made-up names are refused
  (1.33.2–1.33.3).
- `project:` must be declared (1.33.4). CI ownership and wiring checks read
  `component:` (1.33.4–1.33.5).
- Steps that write `.github/workflows/` belong to the orchestrator (1.33.6).
- AGENTS.md is never overwritten by `--force` (1.33.7). Context compaction
  re-injects the re-orientation steps (1.33.8).
- `--verify` checks files are committed, not just present (1.33.10).

**Action:** re-pin to the latest 1.33.x; re-run `atlas_init --force`.

## v1.33.0 — 2026-09-29 (estate release)

**TL;DR:** contract addressing, the test role, and a testing method for every project.

- Contracts address full names: `<project>.arch`, `<project>.component.<name>`.
- Optional test role; use cases written by someone other than the builder (ADR-0007).
- Testing method: run rules, unit tests demoted, the lint loop (ADR-0008).
- "TL;DR first" house style in every briefing and every turn.

**Action:** each vault migrates in one commit, per the migration runbook.

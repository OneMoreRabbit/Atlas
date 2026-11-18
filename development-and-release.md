---
title: Development and release
status: active
version: "1.0"
owner: atlas.arch
updated: 2026-11-11
about: the one path from development to production — every other document refers here
---

# Development and release

**TL;DR:** develop on your seat or the dev box and commit to `dev`. Release by tag.
Staging and production run only that tag, fetched from GitHub. This page is the one
place the path is written; every other document refers here.

It covers software that is deployed. It does not cover management repositories, which
need no development machine: the Atlas vaults, the Nav vaults, the Atlas method repo
and the estate's ansible repo (operator, 2026-11-11). Version numbering is a separate
protocol (AAC-method §9, "Which release is which").

## Where things run

| Place | For | Runs |
|---|---|---|
| Your seat, or the project's dev box when there is one | developing and testing | work in progress, however the seats like |
| Staging server, when the project has one | a final check of a release before it is live | a tag, fetched from GitHub |
| Production | the live service | a tag, fetched from GitHub |

## Branches

| Branch | Holds |
|---|---|
| `dev` | development. Every commit made while developing goes here. |
| `staging` | the release under test. Only in a project that has a staging server. |
| `main` | what is released. |

## The path — project with a staging server

1. Develop and test on your seat or the dev box.
2. Commit to `dev`. Push.
3. Tested on dev and ready to go live: merge `dev` into `staging`.
4. Tag the release — an annotated tag `vX.Y.Z`. The version in the code equals the tag.
5. The staging server fetches that tag from GitHub and runs it.
6. Test on staging. If it fails: fix on `dev`, go back to step 3, cut a new tag.
7. It works: merge `staging` into `main`.
8. The arch seat sends the orchestrator the deploy ask: the tag and its commit.
9. On the operator's word, production fetches the same tag from GitHub and runs it.

## The path — project without a staging server

1. Develop and test on your seat or the dev box.
2. Commit to `dev`. Push.
3. Tested on dev and ready to go live: merge `dev` into `main`.
4. Tag the release — an annotated tag `vX.Y.Z`. The version in the code equals the tag.
5. Prove the tag: fetch it from GitHub into a clean environment, build it, run the
   tests, and record the tag, its commit and the result.
6. The arch seat sends the orchestrator the deploy ask: the tag and its commit.
7. On the operator's word, production fetches that tag from GitHub and runs it.

## Urgent fix to what is live

For when `dev` holds work that is not ready to go live.

1. Branch from the live tag.
2. Fix and test on that branch.
3. Merge it into `main` (into `staging` first, when there is one). Tag the next patch.
4. Prove and deploy it as above.
5. Merge the fix into `dev`.

## Live data

Once production holds real data:

1. Production data is kept. Database changes only go forward and keep existing rows.
2. A change that destroys data needs the operator's explicit word.
3. A release's database changes run on a copy of production first.
4. That copy leaves out anything holding a credential or a session.

## Rules in every case

1. **Staging and production run a tag fetched from GitHub and nothing else.** No seat
   checkout, no file copied from a seat or a dev box, no branch, no untagged commit.
2. **A release holds everything it needs, or pins it exactly**: every package at an
   exact version (no ranges), every container base image by digest. A repo that
   installs other repos pins each one by tag, and those are tagged first. If a deploy
   needs anything from outside the tag, the release is not ready.
3. **Production runs the tag that was proved**: tested on staging, or built from GitHub
   in a clean environment. A test on the dev box does not prove a tag; the dev box may
   run things the tag does not hold. Where the tag was laid does not matter.
4. **Only a plain annotated `vX.Y.Z` is a release.** A tag with a suffix (`rc1`, `dev`)
   never goes to staging or production.
5. **A tag is laid once.** Never moved, never reused, never deleted. A fix is a new tag.
6. **`staging` and `main` change only by merge.** Nobody commits to them directly.
7. **The running service reports its version.** After a deploy it must equal the tag.
8. **The dev box is free.** Seats run what they like on it. None of the rules above
   apply there.

## Who does what

| Who | Does |
|---|---|
| The seat that owns the repo | develops, commits to `dev`, merges, tags, proves the tag |
| The project's arch seat | confirms the proof; sends the orchestrator the deploy ask with the tag and its commit |
| The operator | tests, and says deploy, each time |
| The orchestrator | checks the tag against the commit, deploys it, checks the running version, reports |

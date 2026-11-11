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

It covers code that is deployed. Vaults and the method repo are not deployed
(AAC-method §9). Version numbering is a separate protocol (AAC-method §9, "Which
release is which").

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
| `main` | what is live. |

## The path — project with a staging server

1. Develop and test on your seat or the dev box.
2. Commit to `dev`. Push.
3. Tested on dev and ready to go live: merge `dev` into `staging`.
4. Tag the release — an annotated tag `vX.Y.Z`. The version in the code equals the tag.
5. The staging server fetches that tag from GitHub and runs it.
6. Test on staging. If it fails: fix on `dev`, go back to step 3, cut a new tag.
7. It works: merge `staging` into `main`.
8. On the operator's word, production fetches the same tag from GitHub and runs it.

## The path — project without a staging server

1. Develop and test on your seat or the dev box.
2. Commit to `dev`. Push.
3. Tested on dev and ready to go live: merge `dev` into `main`.
4. Tag the release — an annotated tag `vX.Y.Z`. The version in the code equals the tag.
5. On the operator's word, production fetches that tag from GitHub and runs it.

## Rules in both cases

1. **Staging and production run a tag fetched from GitHub and nothing else.** No seat
   checkout, no file copied from a seat or a dev box, no branch, no untagged commit.
2. **A release holds everything it needs, or pins it to an exact version.** If a deploy
   needs anything from outside the tag, the release is not ready.
3. **Production runs the tag that was tested.** Where the tag was laid does not matter.
4. **A tag is laid once.** Never moved, never reused, never deleted. A fix is a new tag.
5. **`staging` and `main` change only by merge.** Nobody commits to them directly.
6. **The running service reports its version.** After a deploy it must equal the tag.
7. **The dev box is free.** Seats run what they like on it. None of the rules above
   apply there.

## Who does what

| Who | Does |
|---|---|
| The seat that owns the repo | develops, commits to `dev`, merges, tags |
| The operator | tests, and says deploy |
| The orchestrator | deploys the tag to staging and production |

---
title: Next steps
owner: atlas.arch
updated: 2026-11-18
---

# Next steps

**TL;DR:** **v1.36.0, v1.36.1 and v1.36.2 released 2026-11-18** (the operator's
instructions). The estate's pin is 1.36.1. 1.36.2 fixes two faults found in the rollout
and rides with the next estate release: no pin moves for it alone.
1.36.0 is the estate release: it rolls up 1.35.1 to 1.35.10. 1.36.1 puts every vault on
`dev` with no `main`, Nav vaults included, and changes no seat script. The orchestrator
has the steps for every kind of seat. Every seat re-copies its scripts and every Atlas
vault deletes `main`: `release-notes.md`, entries v1.36.0 and v1.36.1. Open after the
release: eleven Nav vaults have only `main` and four have an old `main` to delete, each
moved on the operator's word; the skills repo has no `dev` and the project's policy says
`dev`; the estate's install play for skills is not built. Three needs and two hub asks
are owed; three more asks need an operator ruling.

## Rolled into 1.36.0 (since 1.35.0, 2026-11-10)

| Patch | What |
|---|---|
| 1.35.1 | `--verify` covers the `.claude/` files the installer writes |
| 1.35.2 | staging and production run only a tagged release (now on the page of 1.35.3) |
| 1.35.3 | `development-and-release.md`, the one page for the path to production; house style rule 8; needs helper works on GitHub-App seats |
| 1.35.4 | seat hooks for every agent runtime; Codex added |
| 1.35.5 | `/atlas-publish` step 6b is one script, `scripts/atlas-discard-views.sh` |
| 1.35.6 | `atlas-sync.sh` leaves a code repo with uncommitted changes on its branch; the briefing states the branch |
| 1.35.7 | a failed needs refresh puts a dated line at the top of the list and exits 1 |
| 1.35.8 | one branch per vault: Atlas vaults `dev`, no `main` |
| 1.35.9 | the session-start hook prints a head; the briefing is in files the head lists |
| 1.35.10 | `skills.md`; what a vault holds; house style rules 9 to 11 |
| 1.36.0 | the dashboard's branch table reads a vault listed as a component as a vault |
| 1.36.1 | Nav vaults follow the same rule: `dev`, no `main`. Released after 1.36.0, the same day |

1.35.3 to 1.35.10 were never tagged.

Also: the public-readiness scan (estate review, 63 repos, full history) is merged — no
credentials in any public repo; three live credentials in private Nav-AgentEco await the
operator's rotation.

## Reported in the 1.36 rollout (2026-11-18, hub #15695)

1. ~~Codex trust step~~ (ai-tutor.arch): text corrected in 1.36.2, `context-plane.md`,
   "Runtimes". 1.36.3 on `dev`, not released, adds: a person does it from a shell, and a
   session never restarts itself (hub #15932); Codex must trust the launch dir before it
   lists any hook, and `atlas_init` warns when it does not (hub #15948); a re-install
   without `--launch-dir` keeps the recorded launch dir. Still open: a person does it at each seat; a test seat has no briefing, so nothing shows that its
   hooks are trusted.
2. ~~Release notes warning names an `rc` tag~~ (arc-platform.arch): fixed in 1.36.2, the
   check skips a tag with a suffix. Component seats get it when their vault next moves
   its pin.
3. ~~Product and test seat text~~ (ai-tutor.arch): my hub text gave the component seat's
   first briefing line. Corrected on the hub. The steps in `release-notes.md` were right.

## Owed by the method seat (in order)

1. ~~Briefing needs count/list mismatch~~ (arc-platform): marked resolved by
   arc-platform.arch 2026-11-11, answered in 1.35.0.
2. ~~Needs helper fails on GitHub-App seats~~ done in 1.35.3 (asks git with the repository
   path). The `<project>.<seat>` form is not matched: the validator refuses it at write.
3. **Card stamp on needs-only publishes** (arc-platform): stamp `component.md` only when
   the component itself changes.
4. ~~Backlog template beside `roadmap.md`~~ (Idea): withdrawn by idea.arch 2026-11-11;
   the backlog section in `roadmap.md` serves.
5. **Vault `.gitignore` fragment** + check (estate review PR #63).
6. **Public-readiness rule**: pre-commit secrets scan, CI scan, `--verify` checks for
   README, LICENSE, `.gitignore` (shaped by the scan report).
7. View on the stray-documents check proposal (estate review PR #58): sound if the
   exception list lives in the io-graph.
8. **Two active versions of one interface** (agent-eco sync-compile, 2026-11-12, hub
   #13279; need in Atlas-AgentEco `components/sync-compile/docs/needs/`): the validator
   passes two `status: active` documents with one `interface:`. Sound. Measured at every
   vault's remote head 2026-11-12: one live case, Atlas-Blocks `blocks-service-api` 0.8
   and 0.9. Proposed: warn in the release that adds the check, error from the next estate
   release; an old version still honoured is `deprecated`. Needs the go.
9. **Feature branches in code repos** (agent-eco sync-compile, 2026-11-17, hub #14459):
   `atlas-sync.sh` switches a clean code repo on any named branch to the work branch at
   every briefing. sync-compile builds each fix on a feature branch its arch reads before
   the tag, and was moved four times in one day. The urgent fix path on
   `development-and-release.md` also works on a branch from the live tag, which the script
   switches away from. Proposed: switch only when the repo is on the `release` branch;
   leave any other named branch alone and name it in the briefing. This changes the branch
   policy in `AAC-method.md` section 9, so it needs the operator's ruling. The uncommitted
   changes half is done in 1.35.6.
10. **Drift report reads clean when a consumer is behind** (agent-eco.arch, 2026-11-12; need
   in Atlas-AgentEco `components/arch/docs/needs/agenteco-needs-drift-version-parsing-v0_1.md`).
   Both halves confirmed in `tools/atlas_validate.py`, 2026-11-17. (1) An unquoted
   `version: 0.10` is read by YAML as the number 0.1, so every pin above 0.1 reads aligned.
   No vault has such a version live today; agent-eco quoted theirs. An unquoted
   `pinned: 0.10` in the io-graph is misread the same way. Proposed: the validator reads the
   version as written in the file, so no vault has to change. Refusing unquoted versions
   instead would turn Atlas-AgentEco (101 live contracts) and Atlas-Orchestrator (7) red on
   adoption. (2) The drift label takes `repin` from the newest version only, so a
   `terms-change` version is hidden by a later additive one. Proposed, as asked: the label
   takes the most severe class among all versions after the pin, archived ones included.
   Needs the go.
11. ~~Urgent fix path has the operator's yes~~ and ~~the release strategy proposal~~
   (arc-platform): answered at 1.36.0 by
   `components/method/docs/provides/atlas-development-and-release-response-v0_1.md`.

## Migration to 1.36.0 and 1.36.1

The steps for the orchestrator and for each kind of seat are in `release-notes.md`,
entries v1.36.0 and v1.36.1. The rollout of 1.36.0 started at 09:35 UTC on 2026-11-18
and was held a minute later for 1.36.1. By then three vaults were pinned 1.36.0
(Orchestrator, AiTutor, Labs) and three had the pull request open (Idea, ArcPlatform,
Blocks). Nothing is undone: each moves its pin to 1.36.1. The Nav vault move was
rehearsed on a scratch repo, with a copy holding an unpushed commit and an uncommitted
change: both survived. Rehearsed 2026-11-18 on a copy of the orchestrator's vault from pin
1.35.0: arch seat, component seat, product seat and test seat. Not rehearsed: GitHub's
branch protection, the vault CI run on the migration pull request, a Codex seat.

Measured 2026-11-18 at every vault's remote head:

- **Atlas vaults with a `main` to delete, eight:** AgentEco, DiscoCat, FrogYeti, Idea,
  MathsPractise, MicoManager, Orchestrator, Orient. The other six have none. All
  fourteen have `dev` as the default branch. `main` is protected in Atlas-AgentEco and
  Atlas-Orchestrator: the operator removes the protection.
- **Nav vaults with only `main`, eleven:** Nav-AgentEco, Nav-ArcPlatform, Nav-ArcWeb,
  Nav-Atlas, Nav-Blocks, Nav-DiscoCat, Nav-FrogYeti, Nav-Labs, Nav-MathsPractise,
  Nav-Orchestrator, Nav-Orient. The orchestrator moves each to `dev` on the operator's
  word, because his own copy of the vault changes branch. Steps: `release-notes.md`,
  entry v1.36.1.
- **Nav vaults with `dev` and an old `main`, four:** Nav-AiTutor, Nav-ArcGIS, Nav-Idea,
  Nav-MicoManager. `dev` is the default branch in all four, and `main` holds nothing
  `dev` lacks. The orchestrator deletes each `main` on the operator's word.
- **Pins** (orchestrator's `registry/audit.md`): eleven vaults at 1.35.0; MathsPractise
  1.34.0, DiscoCat 1.28.0, FrogYeti 1.26.0. Those three first follow `README.md`,
  "Upgrading an existing vault to a new method version".
- `templates/vault-ci/` has not changed since v1.35.0. `registry/io-graph.yml` changes
  only in the pin: `release: main` stays for code repos.

A seat that moves its pin and does not re-copy keeps the old script: its briefing is cut
as before, and the SYNC DEGRADED warning leads it.

Not built: a project that declares `work: main` for its code keeps its Atlas vault on
`main`, because the scripts take the vault's branch from `work`. No estate project does.
Build a separate vault branch only when a project needs it.

## Skills and what a vault holds (released in 1.36.0)

Design: `Nav-Atlas/_bridge/threads/atlas-1-35-10-design.md`. `skills.md` says what the
orchestrator has built, from its briefings of 2026-11-18 (hub #15411, #15418) and from
the skills repo itself. Open:

1. **The estate's part** is the orchestrator's (need
   `components/method/docs/needs/atlas-orchestrator-estate-skills-need-v0_1.md`; its
   answer `Atlas-Orchestrator`,
   `components/estate-manage/docs/provides/atlas-estate-skills-response-v0_1.md`). Built
   by 2026-11-18: the skills repo and the estate-skills seat, which answers on the hub.
   Not built: the install play, the view on the estate monitor, reading the repo from
   every seat. The need stays open until the install play has run on real seats.
2. **The estate-skills seat cannot merge yet** (hub #15418): its agent program's
   permission check refused its first merge. With the operator. `skills.md` says so in
   "What exists"; take the line out when the orchestrator says it merges.
3. **The proposal route is settled** (operator, 2026-11-18, by the orchestrator's
   briefing): a seat publishes in its own vault and raises one short need; the
   estate-skills seat opens the pull request. New skills are approved by the operator.
4. **Found in the sense check, told to the orchestrator, theirs to fix:**
   `tools/check_skills.py` in the skills repo refuses the folder `.codex/`, which the
   method's installer writes from 1.35.4, so the skills repo's own check fails once its
   seat re-copies its scripts. `.codex` has to join `SKIP_DIRS` first.
5. **The skills repo has one branch, `main`; the orchestrator project declares
   `work: dev`.** The seat's briefing carries the branch warning and the project's
   dashboard shows a red row. Nothing is refused. Two ways: the repo gets a `dev`, or
   the method lets a component declare its own work branch. The second is a rule change
   and needs the operator.
6. **Not checked by the method seat:** Codex was tested by estate-manage on 0.160.0 in
   a scratch home, not on a live seat. Switching off one account plugin per seat is not
   tested. Licence terms of the off-the-shelf skills; three of twelve say
   "Proprietary".
7. **Not built:** a briefing line that compares a seat's assigned skills with its
   installed ones. It needs the directory's selections and the install play first.
8. **Not built:** the method's own skills. `/atlas-publish` stays a command file.
9. `development-and-release.md` lists the management repos it does not cover. The
   skills repo is one more and is not on the list. The list is the operator's.

## Memory folders and operational seats (designed, not built)

The operator's direction, 2026-11-18: memory for every seat is a folder mounted from
beaver. This part of the method is built and released when the mounts exist. Design:
`Nav-Atlas/_bridge/threads/memory-and-operational-seats-design.md`. Nothing is built.
It waits for AgentEco's mounts and the operator's go.

## Briefing head (released in 1.36.0)

Tested: `tools/tests/test_briefing_head.py`; a fixture seat as component,
arch and both roles, at pins 1.35.9, 1.35.2 and 1.28.6; one real Claude Code 2.1.295
session, which received the head whole, read the files unasked and answered from them.
The real AgentEco vault gives heads of 3,600 to 4,800 characters. Open:

1. **Not tested:** Codex, and Claude Code versions after 2.1.295.
2. **Real-seat test** (orchestrator, in the rollout): each seat reports the first line of
   its new briefing. Still to learn: whether seats read the listed files unasked.
3. **Largest head measured:** a seat holding three AgentEco components and the arch role,
   after a compaction, is 9,638 characters. It is cut to 8,942, the head says so, and the
   whole head is saved as `0-head-in-full.md`. No estate seat is that shape today.
4. **Not built:** the product seat's script prints its briefing whole. It is one line per
   requirement and per ask, so it is short; change it when one passes 10,000 characters.
5. **Not built:** a check that a seat has read the files before its first write. Build it
   only if seats are seen to skip the files.
6. `method-ci.yml` (orchestrator's file) does not run `test_briefing_head.py` until it
   runs every `tools/tests/test_*.py` (Codex seats, item 3). Its fixture seat pins 1.28.6,
   so CI runs the new scripts against an old method and checks the size line.
7. `context-plane.pdf` is not regenerated and still says the whole briefing is injected.
   No browser here can print it. `context-plane.md` and `context-plane.html` are current.

## Blocked on @nav

- **The estate rollout of 1.36.1**: the operator's go, through the orchestrator. Until a
  seat re-copies its scripts it sees only the first 2,000 characters of its briefing.
- **Fifteen Nav vaults to bring to `dev` only** (1.36.1): the operator's word for each.
  In the eleven that have only `main`, his own copy switches to `dev`.
- **`method-ci.yml`**: the change that runs every test file waits for the operator's key
  (`Nav-Atlas/_bridge/threads/method-ci-all-tests.md`).
- **Root `.gitignore` ownership**: arch seats cannot change their vault's root
  `.gitignore` (guard refuses root files; outboxes grant directories only). Rule needed:
  an exact-file grant, and who owns Nav vault roots (arch writes `_bridge/` only).
- **Nav-AgentEco credentials**: rotate the three the scan found.
- **Version numbering protocol**: the method says patch numbers are untagged development
  states; ArcPlatform tags fix releases and uses candidates. One rule needed (operator,
  2026-11-11: keep it a separate protocol from the path).

## Codex seats and other runtimes (released in 1.36.0)

Proved through the real Codex CLI 0.160.0 against a stand-in model:
briefing, style line, write guard, shell guard and turn-end gate, for component, arch and
product seats. Open:

1. **Real-seat test** (orchestrator): `bakehouse.arc-gis.arch` and
   `bakehouse.ai-tutor.product`. Not provable here: a write inside the scope landing
   (this container cannot start Codex's sandbox), and the briefing after a compaction.
2. **Codex trust with no person at the seat** (operator, 2026-11-18: "I just don't want
   this mess next time we deploy"). In the 1.36 rollout the operator trusted the folder
   and the hooks by hand at each Codex seat, because a seat started by the seat tool is
   never asked and seat provisioning writes neither.
   - Folder trust: the orchestrator's, in seat provisioning. The method only reports it.
   - Hook trust: `tools/codex_trust.py`, on `dev` as 1.36.3. It asks Codex for the hooks
     and has Codex record the trust, for hooks that run the method's own scripts only.
     Tested with the real Codex CLI 0.160.0 and a scratch Codex home.
   - Real seat, 2026-11-18 (estate-monitor, hub #15993): the report works with the
     seat's session running. The record was not tried: the operator had already
     trusted every hook there by hand.
   - Report on nineteen Codex seats, 2026-11-18 (hub #15995): sixteen ready. Not
     ready: agent-comms and agent-skeleton (folder trusted, five hooks untrusted),
     arc-gis arch (folder not trusted).
   - Open: the record on a real seat. agent-comms and agent-skeleton are the first two
     it can run on. They are agent-eco's; the orchestrator waits for agent-eco.arch
     and the operator. No release of the tool before the record passes on one.
   - Open: the estate's install and upgrade steps call it (orchestrator's play).
3. **`method-ci.yml`** (orchestrator's file): parse `templates/seat-hooks.json`; run every
   `tools/tests/test_*.py` (`test_seat_hooks.py` is not in CI until then); `sh -n` the
   product-seat and test-seat scripts; stop parsing the two files in item 4.
4. **Temporary, remove when the `method-ci.yml` change of item 3 lands:**
   `templates/component-repo/.claude/settings.json` and
   `templates/arch-seat/.claude/settings.json`. The installer no longer reads them; they
   stay only because `method-ci.yml` parses them by name. They were to go at 1.36.0 and
   could not: the workflow change waits for the operator's key.
5. `context-plane.pdf` is not regenerated; the Runtimes section is in `context-plane.md`.
6. Component repos keep their committed `AGENTS.md`; the installer never overwrites it, so
   its wording stays as installed.

## Backlog (ideas raised, not yet scheduled)

- **Nav vault as a deployable template** + inbox lifecycle + bridge/inbox generic
  definitions (operator, 2026-11-10; assessed, awaiting go).
- **Ideas-to-work cascade** (operator voice note 2026-10-24, via orchestrator 2026-11-11):
  compare Jira's product idea → epic → task → one-developer work item with Atlas's
  roadmap → contracts → needs → bridge tasks; how a business idea enters the product
  cycle, keeps its context and links, and cascades into bite-size work. Note in
  Nav-Orchestrator `_bridge/archive/inbox-2026-11-11/`. No action asked yet.

## Housekeeping, theirs

- 33 needs the method has answered still carry `status: open` in their raisers' vaults
  (orchestrator 18). Retiring is the raiser's.

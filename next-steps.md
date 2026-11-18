---
title: Next steps
owner: atlas.arch
updated: 2026-11-18
---

# Next steps

**TL;DR:** 1.35.10 is prepared on `dev` and NOT released (operator's decisions, 2026-11-18): `skills.md`, what a vault holds, three house style rules; the skills repo, its seat and the install play are the orchestrator's, planned and not built, and `skills.md` follows its plan; the operator said hold until the skills work is done; the memory part is a later release (see "Skills and what a vault holds" and "Memory folders and operational seats"). 1.35.9 is prepared on `dev` and NOT released (operator's go to build, 2026-11-17): the
session-start hook prints a short head and the briefing is in files the head lists, because
Claude Code cut every briefing to 2,000 characters; every seat re-copies its scripts at the release
(see "Migration at the next estate release" and "Briefing head"). 1.35.8 is prepared on `dev` and NOT released (operator ruling 2026-11-17): a vault
has one branch, Atlas vaults `dev` and Nav vaults `main`; the release that carries it deletes
`main` in every Atlas vault (see "Migration at the next estate release"). 1.35.7 is prepared on `dev` and NOT released (orchestrator, hub #14571): a failed
read of the needs register puts a dated line at the top of the list and exits 1. 1.35.6 is prepared on `dev` and NOT released (sync-compile fault report, hub #14459):
`atlas-sync.sh` no longer switches a code repo that has uncommitted changes, and the briefing states
the branch; whether a clean feature branch is left alone needs the operator's ruling (owed item 9).
1.35.5 is prepared on `dev` and NOT released (dprox finding, hub #13341): the
`/atlas-publish` step 6b is one script with no argument, so it can no longer discard a component's
own page; the drift check now covers the publish steps file (hub #13380). 1.35.4 is prepared on `dev` and NOT released (operator go to build, 2026-11-12, hub
#13225): seat hooks for every agent runtime, Codex added; see "Codex seats" below. 1.35.3 is prepared on `dev` and NOT released (operator, 2026-11-11: the orchestrator
reviews it first): `development-and-release.md`, the one page for the path from development to
production, text approved by the operator; needs helper works on GitHub-App seats. `main` is at v1.35.2. **v1.35.0 released 2026-11-10** (estate release, rolled up 1.34.1 to
1.34.16); the estate is migrating to it. Since then: 1.35.1 (verify covers `.claude/`), 1.35.2
(tagged releases only, now superseded by the page). Three needs and two hub asks are owed; two
more asks need an operator ruling.

## Since the last estate release (1.34.0, 2026-10-08)

| Patch | What |
|---|---|
| 1.34.1 | `--verify` fails on uncommitted atlas files (tracked was not committed) |
| 1.34.2 | validator warns on responses that name an address the directory does not know |
| 1.34.3 | arch briefing lists needs addressed to the arch seat; product outbox routed; `--force` fills AGENTS.md placeholders; drift summary counts unreadable contracts; one style hook per seat |
| 1.34.4 | `repin-decided:` later than the predecessor counts as a re-decision |
| 1.34.5 | `to:` is the one address key; variants warned and still checked |
| 1.34.6 | every contract address checked (to/from/owner on needs and provides); short forms, bot names and comms names refused; either directory credential works |
| 1.34.7 | `_bridge/inbox/` rule in bridge-init (estate ADR-0004) |
| 1.34.8 | needs helper derives the project from the vault clone; `--arch --verify` reads only; `--help` says NAME |
| 1.34.9 | `inbox:` key in the io-graph (enabled, auto_approve) |
| 1.34.10 | `outboxes:` lets a vault grant a component extra write paths; both guards honour it, arch-owned |
| 1.34.11 | CI guard gives `atlas/arch/<topic>` branches the arch write set (all but `product/**`, `_bridge/**`) |
| 1.34.12 | validator reaches the live directory without a token (seats without one fell back to cache silently) |
| 1.34.13 | pin moves only on the operator go: guard refuses `method:` and workflow changes on seat branches; `atlas/migration/<version>` is the route; house style rule 7 |
| 1.34.14 | release-notes headings carry the exact tag; checked on vaults and code repos; feeds the estate release log |
| 1.34.15 | inbox is `_inbox/` at every vault root; arch guard allows `_inbox/archive/` |
| 1.34.16 | operator's three rules for inboxes and task lists in any vault; nothing else enforced outside dev projects |

Also: the public-readiness scan (estate review, 63 repos, full history) is merged — no
credentials in any public repo; three live credentials in private Nav-AgentEco await the
operator's rotation.

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
11. **Urgent fix path has the operator's yes** (need from arc-platform.arch, 2026-11-11,
   quoting the operator: "Urgent fix path is fine"). The section stays in
   `development-and-release.md` as written and is released with 1.35.3. Owed at that
   release: the formal response naming the need.

## Migration at the next estate release

**One branch per vault (1.35.8).** Goes in that release's migration note. Per Atlas vault:

1. Orchestrator: remove the branch protection on the vault's `main`.
2. Arch seat: `git fetch origin`, then
   `git log --no-merges --oneline origin/dev..origin/main`. Anything listed other than
   "atlas: regenerate derived views" goes to `dev` by PR first.
3. Arch seat: `git push origin --delete main`.
4. Arch seat: run the validator. The dashboard's vault row reads "one branch, `dev`".
5. Orchestrator: `git ls-remote --heads` on each Nav vault shows `main` only.

Measured 2026-11-17 at every vault's remote head: nine Atlas vaults have a `main`
(ArcPlatform, AgentEco, Blocks, DiscoCat, FrogYeti, Idea, MathsPractise, Orchestrator,
Orient); ArcWeb and Labs have none. In all nine, `main` holds nothing `dev` lacks: only
merge commits, and in three vaults one regenerated-views commit. `registry/io-graph.yml`
does not change: `release: main` stays for code repos. The vault CI files do not change.

Not built: a project that declares `work: main` for its code keeps its Atlas vault on
`main`, because the scripts take the vault's branch from `work`. No estate project does.
Build a separate vault branch only when a project needs it.

**Briefing head (1.35.9).** Goes in that release's migration note. Per seat, after the
vault's pin moves:

1. Component seat, in each code repo:
   `python3 .atlas-method/tools/atlas_init.py --component <slug> --force --launch-dir <launch dir>`,
   commit the scripts, then the same command with `--verify` in place of `--force`.
2. Arch seat, in the vault checkout:
   `python3 .atlas-method/tools/atlas_init.py --arch --launch-dir <launch dir>`.
3. Both: the verify line "prints no more than the hook carries" reads PASS.
4. Both: start a new session. The briefing's first line is
   `# ATLAS-CONTEXT: read these files before you act`.

A seat that moves its pin and does not re-copy keeps the old script: its briefing is cut
as before, and the SYNC DEGRADED warning leads it.

**Skills and what a vault holds (1.35.10).** No step. The text arrives with the pin.

## Skills and what a vault holds (1.35.10, built, not released)

Built on `dev` on the operator's decisions of 2026-11-18. Design:
`Nav-Atlas/_bridge/threads/atlas-1-35-10-design.md`. Tested:
`tools/tests/test_skill_folders.py`; the validator over a copy of the orchestrator's
vault, whose three skills pass. Open:

1. **The orchestrator's, asked by need**
   (`components/method/docs/needs/atlas-orchestrator-estate-skills-need-v0_1.md`),
   answered 2026-11-18 with a plan and the five answers (`Atlas-Orchestrator`,
   `components/estate-manage/docs/provides/atlas-estate-skills-response-v0_1.md`, hub
   #15293). Nothing is built yet. `skills.md` follows that plan.
2. **Temporary:** `skills.md`, "Until the skills repo exists". Delete the section when
   the orchestrator says the repo and its seat are live.
3. **The proposal route.** The operator agreed on 2026-11-18 that a pull request alone
   carries a change. A seat cannot push to the skills repo: every seat is one GitHub
   account and pushing a branch is the same permission as merging. So `skills.md` says
   a need naming the files in the seat's own vault, and the estate-skills seat opens
   the pull request. The orchestrator has put the other way to the operator: every seat
   pushes, and one more permission on the GitHub App. If he chooses it, `skills.md`
   changes in two sections.
4. **Hold.** The operator, 2026-11-18: hold the release while the orchestrator deploys
   skills. The orchestrator's order of work rolls the method out after its first run on
   real seats. Both on the operator's word.
5. **Not checked by the method seat:** Codex was tested by estate-manage on 0.160.0 in
   a scratch home, not on a live seat. Switching off one account plugin per seat is not
   tested. Licence terms of the off-the-shelf skills; three of twelve say
   "Proprietary".
6. **Not built:** a briefing line that compares a seat's assigned skills with its
   installed ones. It needs the directory's selections and the install play first.
7. **Not built:** the method's own skills. `/atlas-publish` stays a command file.

## Memory folders and operational seats (designed, not built)

The operator's direction, 2026-11-18: memory for every seat is a folder mounted from
beaver. This part of the method is built and released when the mounts exist. Design:
`Nav-Atlas/_bridge/threads/memory-and-operational-seats-design.md`. Nothing is built.
It waits for AgentEco's mounts and the operator's go.

## Briefing head (1.35.9, built, not released)

Built on `dev`. Tested: `tools/tests/test_briefing_head.py`; a fixture seat as component,
arch and both roles, at pins 1.35.9, 1.35.2 and 1.28.6; one real Claude Code 2.1.295
session, which received the head whole, read the files unasked and answered from them.
The real AgentEco vault gives heads of 3,600 to 4,800 characters. Open:

1. **Not tested:** Codex, and Claude Code versions after 2.1.295.
2. **Real-seat test** (orchestrator, after the release): one component seat and one arch
   seat re-copy, start a session, and report whether the seat read the files.
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

- **Release of 1.35.3 to 1.35.9**: waits for the operator's word. 1.35.9 is the fix for
  the briefing cut at 10,000 characters; until it is released and seats re-copy their
  scripts, every seat still sees only the first 2,000 characters of its briefing.
- **Root `.gitignore` ownership**: arch seats cannot change their vault's root
  `.gitignore` (guard refuses root files; outboxes grant directories only). Rule needed:
  an exact-file grant, and who owns Nav vault roots (arch writes `_bridge/` only).
- **Nav-AgentEco credentials**: rotate the three the scan found.
- **Next estate push**: 1.34.x accumulates on `main` until called (likely 1.35.0).
- **Version numbering protocol**: the method says patch numbers are untagged development
  states; ArcPlatform tags fix releases and uses candidates. One rule needed (operator,
  2026-11-11: keep it a separate protocol from the path).

## Codex seats and other runtimes (1.35.4, built, not released)

Built on `dev` and proved through the real Codex CLI 0.160.0 against a stand-in model:
briefing, style line, write guard, shell guard and turn-end gate, for component, arch and
product seats. Open before release:

1. **Real-seat test** (orchestrator): `bakehouse.arc-gis.arch` and
   `bakehouse.ai-tutor.product`. Not provable here: a write inside the scope landing
   (this container cannot start Codex's sandbox), and the briefing after a compaction.
2. **Codex trust on unattended seats** (orchestrator): Codex skips untrusted hooks with no
   warning. Seat provisioning has to trust them.
3. **`method-ci.yml`** (orchestrator's file): parse `templates/seat-hooks.json`; run every
   `tools/tests/test_*.py` (`test_seat_hooks.py` is not in CI until then); `sh -n` the
   product-seat and test-seat scripts; stop parsing the two files in item 4.
4. **Temporary, remove at the next estate release (1.36.0):**
   `templates/component-repo/.claude/settings.json` and
   `templates/arch-seat/.claude/settings.json`. The installer no longer reads them; they
   stay only because `method-ci.yml` parses them by name.
5. `context-plane.pdf` is not regenerated; the Runtimes section is in `context-plane.md`.
6. Component repos keep their committed `AGENTS.md`; the installer never overwrites it, so
   its wording stays as installed.

## Backlog (ideas raised, not yet scheduled)

- **Nav vault as a deployable template** + inbox lifecycle + bridge/inbox generic
  definitions (operator, 2026-11-10; assessed, awaiting go; would be 1.35.1).
- **Ideas-to-work cascade** (operator voice note 2026-10-24, via orchestrator 2026-11-11):
  compare Jira's product idea → epic → task → one-developer work item with Atlas's
  roadmap → contracts → needs → bridge tasks; how a business idea enters the product
  cycle, keeps its context and links, and cascades into bite-size work. Note in
  Nav-Orchestrator `_bridge/archive/inbox-2026-11-11/`. No action asked yet.

## Housekeeping, theirs

- 33 needs the method has answered still carry `status: open` in their raisers' vaults
  (orchestrator 18). Retiring is the raiser's.

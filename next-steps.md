---
title: Next steps
owner: atlas.arch
updated: 2026-11-12
---

# Next steps

**TL;DR:** 1.35.5 is prepared on `dev` and NOT released (dprox finding, hub #13341): the
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

1. **Briefing needs count/list mismatch** (arc-platform): count and list from one query,
   scoped to the briefed component's address.
2. ~~Needs helper fails on GitHub-App seats~~ done in 1.35.3 (asks git with the repository
   path). The `<project>.<seat>` form is not matched: the validator refuses it at write.
3. **Card stamp on needs-only publishes** (arc-platform): stamp `component.md` only when
   the component itself changes.
4. **Backlog template** beside `roadmap.md` (Idea; operator ask 2026-10-17).
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

## Blocked on @nav

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

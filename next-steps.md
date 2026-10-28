---
title: Next steps
owner: atlas.arch
updated: 2026-10-28
---

# Next steps

**TL;DR:** estate is pinned at **1.34.0** (operator hold). Fourteen patches since
(1.34.1 to 1.34.14) sit on `main`, all tested, CI green. Three needs and three hub asks
are owed; two more asks need an operator ruling. The seat was signed out 13 to 27
October; nothing was lost.

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

Also: the public-readiness scan (estate review, 63 repos, full history) is merged — no
credentials in any public repo; three live credentials in private Nav-AgentEco await the
operator's rotation.

## Owed by the method seat (in order)

1. **Briefing needs count/list mismatch** (arc-platform): count and list from one query,
   scoped to the briefed component's address.
2. **Needs helper fails on GitHub-App seats** (orchestrator): use the estate token broker
   when present; match the `<project>.<seat>` form.
3. **Card stamp on needs-only publishes** (arc-platform): stamp `component.md` only when
   the component itself changes.
4. **Backlog template** beside `roadmap.md` (Idea; operator ask 2026-10-17).
5. **Vault `.gitignore` fragment** + check (estate review PR #63).
6. **Public-readiness rule**: pre-commit secrets scan, CI scan, `--verify` checks for
   README, LICENSE, `.gitignore` (shaped by the scan report).
7. View on the stray-documents check proposal (estate review PR #58): sound if the
   exception list lives in the io-graph.

## Blocked on @nav

- **Root `.gitignore` ownership**: arch seats cannot change their vault's root
  `.gitignore` (guard refuses root files; outboxes grant directories only). Rule needed:
  an exact-file grant, and who owns Nav vault roots (arch writes `_bridge/` only).
- **Nav-AgentEco credentials**: rotate the three the scan found.
- **Next estate push**: 1.34.x accumulates on `main` until called (likely 1.35.0).
- **This seat's `gh` sign-in** lapsed with the 13 October sign-out; git transport works,
  the GitHub API and `gh` do not.

## Housekeeping, theirs

- 33 needs the method has answered still carry `status: open` in their raisers' vaults
  (orchestrator 18). Retiring is the raiser's.

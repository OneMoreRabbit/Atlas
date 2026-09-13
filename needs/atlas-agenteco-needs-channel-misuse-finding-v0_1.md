---
title: "Finding — AgentEco is using needs/ as a push channel; 10 of 24 open needs are not asks"
to: agent-eco
need: retire 3 stale needs, convert 10 that are rulings/notices/relays into their proper channel, route 1 method question to atlas
status: open
version: '0.1'
updated: 2026-09-13
from: atlas
---

# needs/ is an outbox for asks — half of AgentEco's open needs are not asks

Reviewed all 24 open needs in Atlas-AgentEco on 2026-09-13 against method 1.27.1.
**10 are genuine and correctly filed. 10 misuse the channel. 1 is misrouted. 3 are stale.**

## Why it matters

A need is an ask: it sits in the addressee's briefing **in full until answered**. A
ruling, a release notice, a drift nag or an ADR relay is not an ask, so nobody answers
it — it stays UNANSWERED in every addressee's briefing indefinitely. Ten of them is the
same mechanism that gave rbac-compile a 3–5× briefing (1.25.2), rebuilt by hand.

The channel table (component-init / arch-seat, method 1.21) is the rule:

| You want to convey | Channel |
|---|---|
| a durable rule | constitution or a contract |
| a decision | proposal → ADR; consequences land in constitution/contracts |
| an ask that needs an answer | `needs/` addressed to a slug |
| a one-off instruction | the session or the hub — no document |

And 1.26.2: never hand-mint a need that duplicates a derived signal (drift, ROUTING).

## The 24, assessed

**Genuine, correctly filed — leave (10)**
`agent-comms-comms-directory-generation`, `agent-comms-notify-command-unset`,
`agenteco-needs-daemon-supervision`, `agenteco-needs-install-requires-seat-restart`,
`agenteco-needs-queue-gc-loses-messages`, `agenteco-needs-ratify-registry-app-block`,
`agenteco-needs-stale-personal-repo-duplicates`, `agent-image-contract-repin-request`
(correct 1.26.9 practice), `agenteco-needs-address-legacy-needs`,
`agent-skeleton-seat-helper-withdrawal` (its own update says the helpers are gone —
confirm and retire).

**Channel misuse — convert or delete (10)**

| Need | What it actually is | Where it belongs |
|---|---|---|
| `agenteco-needs-ghcr-namespace` | a ruling | constitution (or an ADR); delete the need |
| `agenteco-needs-cut-the-seven-releases` | an instruction + a rule | rule (`vX.Y.Z` everywhere) → constitution; "cut your release" → session/hub; delete the need |
| `rbac-compile-release-repin-brief` | a release notice | the contract version bump IS the notice — drift shows it; delete |
| `agenteco-needs-clear-drift-repins` | a drift nag | the dashboard already says it; delete |
| `agenteco-needs-locality-{agent-compile, agent-image, ansible-platform, ingstr, rbac-compile, sync-compile}` (6) | an accepted ADR relayed per component | ADR-0010 + its rollout doc + `affects:`; the dev cycle's step 1 reads it. Delete the six (or keep ONE pointer if you must) |

**Misrouted — send to atlas (1)**
`agent-compile-external-consumer-contracts-orphaned` is a method question (no
`external:` equivalent for what a component *provides* to a consumer that left the
vault), addressed to nav. Under 1.27.1 read-in-place the edge lives in the *consumer's*
`external:`; the provider declares nothing. The residual gap — a provider cannot see
cross-vault consumers on its own dashboard — is real; re-address it `to: atlas`.

**Stale — retire (3)**
`sync-compile-atlas-context-exit-status` (fixed in v1.20.1, open since August);
`ingstr-needs-qdrant-stack` and `dprox-needs-qdrant-collection` (July, no `to:` — they
fail open into every briefing in range; add `to: ansible-platform` / `to: ingstr` or
archive).

## Ask

1. Retire the 3. 2. Convert the 10 per the table. 3. Re-address the 1 to atlas.
Result: 24 → ~10 real needs, and a materially lighter briefing for every AgentEco seat.

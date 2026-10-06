---
title: "Two-component seat briefs only one component — the other's needs vanish while verify passes"
status: fixed
opened: 2026-10-03
updated: 2026-10-06
owner: atlas.arch
about: "seat briefing silently dropped a sibling component -> sibling scan read SLUG= only and compared remotes by exact string -> both fixed in 1.33.11"
versions: "method 1.33.3-1.33.10; found on agent-eco's agent-skeleton/agent-seat and dprox seats"
---

# Two-component seat briefs only one component — 2026-10-03

## In one paragraph
A seat holding two components (one launch dir, two repos) got a briefing for only one
of them. The other component's contracts and open needs — including needs addressed
to the operator — were missing, and `atlas_init --verify` passed. Two causes in the
same loop of `scripts/atlas-context.sh`; both fixed in 1.33.11.

## Symptom
Briefing header reads `# ATLAS-CONTEXT — <one name>` instead of
`# ATLAS-CONTEXT — seat briefing — a, b`. No error anywhere.

## Root cause
1. The sibling scan read `SLUG=` from each repo's `.atlas.conf`. Since 1.30.9 the key
   is `COMPONENT=`; a re-initialised sibling had no `SLUG=` and was skipped.
2. The scan compared `ATLAS_VAULT_REMOTE` by exact string. `...Atlas-AgentEco.git` and
   `...Atlas-AgentEco` are accepted everywhere else; here the mismatch skipped the
   sibling. Two upgrade prompts had spelled the remote differently.

## Fix
Upgrade to 1.33.11 or later and re-run `atlas_init --component <name> ... --force` in
each repo. The scan now reads `COMPONENT` then `SLUG`, and compares remotes with
`.git` and case stripped.

## Wrong turns
- The 1.30.9 migration updated the write guard's sibling scan but not this one — two
  copies of the same loop, one fixed. The lesson: when a key changes, grep every
  reader of it, not just the one you are looking at.
- The first fix added exit 3 to `atlas-sync.sh` for drifted pins; under `set -e` that
  killed the whole briefing. Caught in test; the context hook now survives exit 3
  and prints a SYNC DEGRADED line in the briefing.

## How to tell if it is back
On a multi-repo seat: `sh scripts/atlas-context.sh | head -1` must list every
component the seat holds.

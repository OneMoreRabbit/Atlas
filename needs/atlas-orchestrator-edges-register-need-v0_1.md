---
title: "Need — publish an estate edges register beside the needs register"
to: ansible-platform
need: publish registries/edges.json — every vault's `external:` entries — so a provider can see which other vaults pin its contracts (method 1.28, agent-compile finding)
status: open
version: '0.1'
updated: 2026-09-14
from: atlas
relates: provides/atlas-estate-findings-response-v0_1.md
---

# Publish `registries/edges.json`

Method 1.28 rules that a provider is entitled to see its cross-vault consumers (the
agent-compile finding: from a provider's vault, an absent edge and no consumer look
identical). The mechanism mirrors `atlas-needs`: the estate publishes a register, every
seat reads it in place. The consumer side is shipped; the register does not exist yet.

## Shape

Same daily rebuild as `needs.json`, beside it:

```json
{ "updated": "2026-09-14", "generated_by": "estate-audit",
  "edges": [
    { "vault": "Atlas-Orchestrator", "consumer": "ansible-platform",
      "provider": "agent-compile", "interface": "agent-registry-app-block",
      "pinned": "0.3" } ] }
```

One entry per `external:` item in every vault's `registry/io-graph.yml` — `vault` is the
consuming vault, `consumer` the pinning component (the vault's arch if vault-level),
`provider`/`interface`/`pinned` copied from the entry (`pinned` omitted when absent).

## What consumes it

`atlas-needs.py --refresh` (1.28) reads `ATLAS_EDGES_REGISTER` from `.atlas.conf` and
writes `~/.atlas/consumers.md` — the provider's own contracts, pinned where. The briefing
carries it. Until the register exists the section is simply absent.

Set `ATLAS_EDGES_REGISTER` on seats in the same run that sets `ATLAS_NEEDS_REGISTER`.

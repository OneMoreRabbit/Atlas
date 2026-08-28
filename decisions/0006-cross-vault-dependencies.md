---
title: ADR-0006 (Atlas) — Depending across vaults; the orchestration scope
interface: atlas-adr-0006
version: 1.0
status: accepted
date: 2026-08-28
origin: Atlas-AgentEco ADR-0008 (operator decision to promote ansible-platform to its own
  vault) via Atlas PRs #2/#3 from its arch seat, plus the operator's Architecture Note
  (Nav-Atlas, 2026-08-28) defining the scope model
affects: [aac-method, atlas_validate]
implemented: method 1.16 (2026-08-28)
---

# ADR-0006 — Depending across vaults; the orchestration scope

## Status

**Accepted** — 2026-08-28. Enables the estate's first Scope-1B entity
(`Atlas-Orchestrator`), per the operator's Architecture Note.

## Context

The estate's scope model is now explicit (Architecture Note, Nav-Atlas): **1A** the
method (this repo); **1B** orchestration — deployment, configuration and estate
management on behalf of all projects; **2** a project's architecture; **3** a component.
Infrastructure had been modelled as a Scope-3 component (`ansible-platform`) inside one
Scope-2 vault (AgentEco) while serving five projects — it sat *above* the vault that
contained it. Nothing outside that vault could declare a dependency on it: `io-graph.yml`
is per-vault, and a vault with zero components could express no dependency at all, since
every `needs/` hung off a component.

## Decision

1. **`external:` in the io-graph** — a pinned dependency on a contract homed in another
   vault, deliberately the same shape as the `method:` pin (which was already exactly
   this). Provider keeps one home; consumer pins deliberately; drift is reported on the
   dashboard (latest fetched in CI via a blobless clone of the provider vault; offline
   runs show "unchecked"). Major drift is red and fails the run, like any breaking edge.
2. **Vault-level `needs/`** — project-level asks that belong to no single component,
   governed by component-outbox rules. Delivered by addressee like any need; an external
   provider's slug is a valid addressee (no warning); naming canon applies.
3. **Depend on a capability, not an implementation** — the operator's guidance, kept in
   §5: consumers ask for "a seat", the provider chooses what serves it.

## Consequences

- A Scope-1B vault can exist without stub components in every consumer, and its
  consumers see drift against it exactly as they do against the method.
- Cross-vault asks rely on the provider's arch seat *reading consuming vaults* — a new
  duty that lands in the orchestrator's seat protocol, not in the method's tooling.
- The validator gains its second CI-only content fetch (after wiring); plain local runs
  stay offline.

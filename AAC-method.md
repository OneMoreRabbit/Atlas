---
title: Architecture-Above-Code (AAC) — The Method
interface: aac-method
version: 1.0
status: active
maturity: 1.0
updated: 2026-07-03
# 2026-07-03 pre-release amendments (v1.0 was never committed/adopted, so amended in place):
#   - outbox folders renamed downstream/->provides/, upstream/->needs/ (inbox-misreading hazard)
#   - validator promoted from "optional, deferred" to the required generator of derived views
---

# Architecture-Above-Code (AAC)

> The documentation that used to live *inside* the code — docstrings, READMEs, scattered
> design notes — now lives *above* it, in a single governing vault. When you direct
> components instead of hand-writing them, the architecture layer becomes the primary
> artefact and the code is produced beneath it.

**Atlas** is this method repo; each project instantiates the method as an `Atlas-<Project>`
vault next to its code (the `atlas-` pattern). Project vaults **pin** a version of this document
(`method:` block in their `io-graph.yml`) — so the method is governed by its own drift rules.

---

## 1. The core idea

Two planes hold the system in alignment:

| Plane | Direction | Mechanism | Answers |
|---|---|---|---|
| **Vertical** | component ⇄ architecture | Proposals → review → ADRs → constitution | "Is everyone building to the same overall design?" |
| **Horizontal** | component ⇄ component | Contracts in `docs/provides` / `docs/needs`, routed by the I/O graph, version-pinned | "Do two specific components agree on their interface?" |

High-level alignment flows **down** from the constitution. Low-level detail flows
**sideways** through contracts. Drift is made **visible** as a number (pinned vs latest)
rather than discovered weeks later.

---

## 2. The golden rules

1. **One home per document.** Every document has exactly one author and one location, next
   to the component that owns it. Nobody ever copies another component's document. You
   *reference* it in place (`[[wikilink]]` or a path from your I/O manifest).
2. **Folders are outboxes.** A component only ever **writes** to its own folders and only
   ever **reads** other components' folders.
3. **Latest for awareness, pinned for building.** You always *see* the newest contract
   (real-time review). You *build* against a pinned version and bump it deliberately.
4. **Changes to shared architecture go through a proposal.** You never edit the constitution
   directly; you raise an ADR in `architecture/proposals/`.
5. **The dashboard is derived, never authored.** It only reads frontmatter others maintain.

---

## 3. Folder semantics

Each component lives at `components/<slug>/`:

```
components/<slug>/
  component.md            # identity + frontmatter the dashboard reads (REQUIRED)
  docs/                   # reference: design briefs + user manuals (this component's own)
    archive/              # retired briefs/manuals (MAJOR/MINOR milestones)
  docs/provides/          # OUTBOX: "what I provide" — contracts my consumers build against
    archive/              # retired versions of my provided contracts
  docs/needs/             # OUTBOX: "what I need" — requests/feedback aimed at my providers
    archive/              # retired versions of my asks
```

> **Root rule:** `docs/` root holds ONLY component-level reference documents — the
> architecture doc, the user manual, and a development plan/status. **Every document
> addressed to or negotiated with another component** (proposal, reply, response, finding,
> question, handoff, review, schema) **lives in `provides/` or `needs/` — never in the
> root.** Rule of thumb: *asking side* (proposal, request, finding, question, reply-in-your-
> own-thread) → `needs/`; *answering/committing side* (response, handover, agreement,
> published schema) → `provides/`.

> Naming note: the folders are named by **content** (`provides`/`needs`), not by direction
> (`downstream`/`upstream`), because direction-names invite the inbox misreading —
> "`upstream/` must be stuff *from* upstream." It isn't; nothing is ever delivered into
> your folders. *Upstream*/*downstream* remain the terms for the **relationship** (§9).

For an edge where **A feeds B** (A is upstream/provider, B is downstream/consumer):

- A publishes the contract to `A/docs/provides/`. B **reads** it to define its inputs.
- B publishes its needs to `B/docs/needs/`. A **reads** it to see what its consumer wants.
- The pair `A/docs/provides` (provider-stated) + `B/docs/needs` (consumer-stated) is
  the **bilateral contract** for that edge. Where they disagree is the negotiation surface —
  the place silent drift used to hide. (Consumer-driven contracts; Fowler 2006.)

---

## 4. Versioning

Git is the substrate (full history, diffs, blame). On top of git, one semantic layer:

**Filenames carry `MAJOR.MINOR`** — `dprox-endpoints.v0.2.md`. Frontmatter may carry the
full `MAJOR.MINOR.PATCH`.

| Level | When | Action | Folder impact |
|---|---|---|---|
| **PATCH** | typo, clarification | commit to same file | none |
| **MINOR** | additive, backward-compatible | new `…v1.4.md`, move prior to `archive/` | +1 in archive |
| **MAJOR** | breaking change | new `…v2.0.md`, deprecate `1.x`, move to `archive/` | +1 in archive |

- **`0.x`** = unstable / in development. Breaking changes allowed freely between minors.
- **`1.0`+** = stable contract. MAJOR-is-breaking discipline applies. Crossing to `1.0` is
  the deliberate signal "this interface is now ratified."
- The **live folder holds only current versions** (one file per interface). Retired
  MAJOR/MINOR milestones live in `archive/`, viewable in-vault. Git holds everything else.

Required frontmatter on every contract document:

```yaml
---
interface: dprox-endpoints     # stable id, independent of filename
version: 0.2                   # MAJOR.MINOR (.PATCH optional)
status: draft | active | deprecated | superseded
updated: 2026-06-30
supersedes: 0.1                # optional
---
```

---

## 5. The I/O graph (registry)

`registry/io-graph.yml` is the single source of truth for who depends on whom. It is the
edge list of a directed graph. Each edge pins the version the consumer builds against:

```yaml
edges:
  - from: agent-image          # provider (upstream)
    to: agent-compile          # consumer (downstream)
    interface: snapshot-instance-fields
    mode: collaboration        # team-topologies mode: x-as-a-service | collaboration | facilitation
    pinned: 0.2                 # version agent-compile currently builds against
```

From the graph, each component's reading list is fully determined:
- **My inputs** = the `docs/provides/` of every component where `to == me`.
- **My consumers' feedback** = the `docs/needs/` of every component where `from == me`.

This may be hand-resolved by an agent, or mechanically emitted to
`registry/.compiled/<slug>/io-manifest.yml` by the validator (§8).

---

## 6. The session protocol (how a component stays aligned)

Every agent session working on a component MUST, before doing work:

1. Read `architecture/constitution.md` — the global principles.
2. Resolve its edges from `registry/io-graph.yml` (or its compiled `io-manifest.yml`).
3. Read each **upstream provider's** `docs/provides/` at the **pinned** version — these
   are its inputs. Note any **latest** version ahead of the pin (drift to review).
4. Read its **own consumers' feedback** in their `docs/needs/` — requests it must answer.
5. Check `architecture/proposals/` for in-flight changes affecting it.

After doing work, it publishes outputs to its own `docs/provides/` (new contracts) and
`docs/needs/` (new asks), bumping versions per §4.

The entry hook lives in each **code repo** as `AGENTS.md`, pointing back to its Atlas
component folder and the constitution — that is what makes alignment real-time: every
session pulls current state from Atlas before touching code.

---

## 7. The proposal / ADR flow (vertical plane)

When work in a component implies a change to **shared** architecture:

1. The component drops an ADR in `architecture/proposals/NNNN-title.md`, `status: proposed`,
   listing `affects: [components]`.
2. It is reviewed at the architecture level (you, or a designated reviewer).
3. If accepted: `status: accepted`, moved to `architecture/decisions/`, and the constitution
   / system-context / io-graph are updated. If rejected: `status: rejected`, kept for record.
4. Because every component reads the same constitution, the decision propagates without
   manual tracing. Affected edges show as drift until consumers re-pin.

ADRs use the Nygard format: Context → Decision → Status → Consequences.

---

## 8. Tooling — the validator

AAC is achieved by **policy + documents**; an agent reading the files performs the whole
protocol. The single permitted tool is the **validator** (the Atlas repo’s `tools/atlas_validate.py`, run from the project-vault root or given the vault path as first argument), and its
scope is fixed: it makes the *derived views* genuinely derived. It parses `io-graph.yml` +
contract frontmatter and regenerates:

- `registry/graph.md` — the rendered Mermaid graph + edge table;
- the drift panel in `dashboard.md` (between `atlas:generated` markers);
- the edge block in each `component.md` (between markers);
- `registry/.compiled/<slug>/io-manifest.yml` — each component's reading list;

and prints a **drift report** (every edge where `pinned ≠ latest`; exit non-zero on breaking
drift, for CI). **Rule: edge facts are edited only in `io-graph.yml`; generated blocks are
never edited by hand.** This exists because hand-maintained copies of the graph were found
drifting within a day of being written — the method applies to itself.
It mirrors the ecosystem's pattern: read YAML, emit YAML/views, never mutate system state.

---

## 9. Glossary

- **Upstream** — a component you depend on (it provides; you consume). A *relationship*
  term — the folder holding material aimed at your upstreams is `docs/needs/`.
- **Downstream** — a component that depends on you (you provide; it consumes). The folder
  holding material for your downstreams is `docs/provides/`.
- **Contract** — a versioned document describing an interface between two components.
- **Pin** — the contract version a consumer currently builds against.
- **Drift** — `pinned < latest`. Patch/minor = informational; major = review required.
- **Constitution** — the inviolable, global principles every component reads first.
- **ADR** — Architecture Decision Record; the unit of the vertical proposal flow.

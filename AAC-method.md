---
title: Architecture-Above-Code (AAC) — The Method
interface: aac-method
version: 1.2
status: active
maturity: 1.0
updated: 2026-08-19
# 2026-07-03 pre-release amendments (v1.0 was never committed/adopted, so amended in place):
#   - outbox folders renamed downstream/->provides/, upstream/->needs/ (inbox-misreading hazard)
#   - validator promoted from "optional, deferred" to the required generator of derived views
# 1.1 (2026-08-19): transport rework — git is the transport, no shares or machine paths.
#   - vaults are git repos with remotes; code repos resolve them by cloning ($ATLAS_VAULT)
#   - session protocol (§6) made mechanical: validator --emit-context compiles the reading
#     list into one ATLAS-CONTEXT.md, injected by a SessionStart hook
#   - registry/.compiled/ promoted from scratch artefact to committed, published contract
# 1.2 (2026-08-19): the write model — golden rule 2 made mechanical, like §6 made the reads.
#   - vault writes are path-scoped by branch (atlas/<slug>/<topic>); CI guard enforces scope
#   - components author, main generates: derived views are committed only by CI after merge
#   - ceremony follows path: outbox-only PRs auto-merge; proposals/io-graph edits get review
#   - method pin honoured: atlas-sync checks out the method repo at the vault's pinned tag
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

**Scope rule (decides the home of every document):** a document owned by ONE component
lives in that component's folders below. A document that *spans two or more components* —
platform architectures, cross-component designs, shared schemas' rationale — lives in
`architecture/` at the vault root, beside the constitution and system-context. Components
then pin thin contracts in `provides/` that *reference* the architecture doc for the
shared design (never copy it down). **`architecture/` is written by the architecture
session alone; components contribute to it only via `proposals/`.**

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
> your folders. *Upstream*/*downstream* remain the terms for the **relationship** (§10).

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

Component entries may carry an optional `sink: true` flag (terminal downstream sink —
rendered distinctly in the graph). Note `role:` on a component entry is free prose;
rendering semantics live in explicit flags, never inferred from slugs or prose.

From the graph, each component's reading list is fully determined:
- **My inputs** = the `docs/provides/` of every component where `to == me`.
- **My consumers' feedback** = the `docs/needs/` of every component where `from == me`.

The validator (§8) mechanically resolves this into
`registry/.compiled/<slug>/io-manifest.yml` — each component's version-pinned reading
list. The compiled manifests are **committed to the vault repo**: they are the published
retrieval payload every session builds its context from, not a local scratch artefact.

---

## 6. The session protocol (how a component stays aligned)

Every agent session working on a component MUST, before doing work, have read:

1. `architecture/constitution.md` — the global principles.
2. Its edges, resolved from `registry/io-graph.yml` (compiled: its `io-manifest.yml`).
3. Each **upstream provider's** `docs/provides/` contract at the **pinned** version —
   its inputs. Any **latest** version ahead of the pin is drift to review.
4. Its **own consumers' feedback** in their `docs/needs/` — requests it must answer.
5. `architecture/proposals/` entries in flight that affect it.

These five reads define **what the session's context contains** — but the session does not
perform them by browsing. The validator's `--emit-context <slug>` mode (§8) compiles all
five, in that order, into a single **`ATLAS-CONTEXT.md`**, each section headed with its
source path and version, plus a drift summary. A `SessionStart` hook in the code repo
syncs the vault and injects this artefact automatically — the protocol is mechanical, not
trust-based; a session that starts has already "done the reads."

> **The retrieval invariant: a session reads `ATLAS-CONTEXT.md`, never the vault.**
> If the context is insufficient for the work, the io-graph is missing an edge — fix
> `registry/io-graph.yml` and recompile. Free browsing of the vault is how "dump
> everything into the window" returns; the single generated artefact is the boundary
> that keeps retrieval explicit, measurable, and replaceable.

After doing work, the session publishes outputs to its own `docs/provides/` (new
contracts) and `docs/needs/` (new asks), bumping versions per §4, stamps `updated:` in
`component.md`, recompiles derived views, and pushes the vault — packaged as the
`/atlas-publish` command in each code repo (see [[component-init]]).

The entry hook lives in each **code repo** as a **committed** `AGENTS.md`, resolving the
vault via `$ATLAS_VAULT` (§9) — never a machine path. That is what makes alignment
real-time *and* portable: every session, on any machine, pulls current state from Atlas
before touching code.

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
- the drift panel in `dashboard.md` (between `atlas:drift` markers);
- the edge block in each `component.md` (between `atlas:edges` markers);
- `registry/.compiled/<slug>/io-manifest.yml` — each component's reading list
  (**committed**, §5);

and prints a **drift report** (every edge where `pinned ≠ latest`; exit non-zero on breaking
drift — run it as a CI gate on the vault repo, on push and nightly, so drift surfaces with
no local machine switched on).

A second mode serves the session protocol (§6): **`--emit-context <slug>`** reads the
component's committed `io-manifest.yml` and concatenates the five protocol reads into one
`ATLAS-CONTEXT.md` (stdout, or `--out <path>`), each section headed with source path and
version, ending in a drift summary. It prints a byte/token estimate to stderr — the cost
of a session's context is a number you can watch. Its dependency is pinned in
`tools/requirements.txt`; a fresh VM installs it in one line.

**Rule: edge facts are edited only in `io-graph.yml`; generated blocks are
never edited by hand.** This exists because hand-maintained copies of the graph were found
drifting within a day of being written — the method applies to itself.
It mirrors the ecosystem's pattern: read YAML, emit YAML/views, never mutate system state.

---

## 9. Transport — git is the substrate, everywhere

The method has **no filesystem assumptions**. Every artefact class lives in a git repo
with a remote; nothing is ever addressed by a machine path, LAN share, or sibling
directory. This is what makes a session equivalent whether it runs on the authoring
desktop, a fresh cloud VM, or a phone-driven remote session.

| Repo | Contents | Access |
|---|---|---|
| Method (`Atlas`) | this spec, `component-init`, the validator | cloned per session (`$ATLAS_METHOD`, default `./.atlas-method`) |
| Project vault (`Atlas-<Project>`) | constitution, ADRs, io-graph, component docs, compiled manifests | cloned per session (`$ATLAS_VAULT`, default `./.atlas`) |
| Code (one per component) | the code, plus the hooks: `AGENTS.md`, `scripts/atlas-sync.sh`, `.claude/` | where the session runs |

- **Resolution is by env var with a default, never by path.** `scripts/atlas-sync.sh`
  clones or fast-forwards `$ATLAS_VAULT` and `$ATLAS_METHOD`. A local layout that already
  has the vault checked out just points the vars at it — same script, no clone.
- **Publishing is `git push`.** There are no mirrors or copy steps; a "publish to share"
  step is a smell that the vault lacks a remote.
- **Vault repo hygiene:** `.gitattributes` with `* text=auto eol=lf` (mixed
  Windows/Linux/mobile editing otherwise produces CRLF churn in every note), and a
  `.gitignore` limited to editor workspace cruft (e.g. `.obsidian/workspace*.json`,
  `.obsidian/cache`, `.trash/`) — **not** `registry/.compiled/`, which is committed (§5).
- **Vault writes from sessions arrive as branches/PRs**, reviewable as diffs from any
  device; generated documents carry provenance frontmatter (`generated_by:`,
  `generated_at:`, `source:`, `status: draft|reviewed`).
- **The method pin is honoured, not just declared.** `atlas-sync.sh` reads the vault's
  `method:` pin from `registry/io-graph.yml` and checks out `$ATLAS_METHOD` at the
  matching tag (`v<pinned>`); method releases are tagged. A session never silently gets
  whatever the method repo's default branch happens to hold.

### The write model — golden rule 2, mechanical

One vault, many writers, safe because writes are to **disjoint paths**. The same
principle as the retrieval invariant in §6, applied to the write side:

- **Vault writes are path-scoped by branch.** A component session publishes on
  `atlas/<slug>/<topic>` and may write only `components/<slug>/**`, an additive
  `architecture/proposals/` entry (`status: proposed`), and edges in
  `registry/io-graph.yml` naming itself at one end. A CI guard on the vault repo
  enforces this from the branch name alone. The architecture session is the exception:
  it owns `architecture/` and the constitution, works against the vault directly, and is
  the reviewer, not a PR author.
- **Components author; `main` generates.** Generated views (`registry/graph.md`,
  `dashboard.md`, the `component.md` edge blocks, `registry/.compiled/**`) are **never
  committed by a component PR** — the validator rewrites every component's derived files
  on each run, so committing them would put cross-component writes in every publish and
  conflict under concurrency. Instead, CI on the vault's default branch regenerates and
  commits them after each merge (and nightly), so the compiled manifests reflect merged
  truth rather than the last publisher's local run. In a component session the validator
  runs as a **check only** (a red exit blocks publishing); its local output is discarded.
- **Ceremony follows path, not habit.** A PR touching only `components/<slug>/**`
  auto-merges once the guard and validator pass — that is publishing to your own outbox,
  and review adds nothing. A PR touching `architecture/proposals/**` or
  `registry/io-graph.yml` waits for the architecture session — that is proposing.
  Without the split, routine contract bumps queue behind a human and the outbox model
  stops being real-time.

Template workflows for the guard and the regeneration job ship in this repo under
`templates/vault-ci/` — copy them into the vault's `.github/workflows/`.

---

## 10. Glossary

- **Upstream** — a component you depend on (it provides; you consume). A *relationship*
  term — the folder holding material aimed at your upstreams is `docs/needs/`.
- **Downstream** — a component that depends on you (you provide; it consumes). The folder
  holding material for your downstreams is `docs/provides/`.
- **Contract** — a versioned document describing an interface between two components.
- **Pin** — the contract version a consumer currently builds against.
- **Drift** — `pinned < latest`. Patch/minor = informational; major = review required.
- **Constitution** — the inviolable, global principles every component reads first.
- **ADR** — Architecture Decision Record; the unit of the vertical proposal flow.

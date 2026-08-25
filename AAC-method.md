---
title: Architecture-Above-Code (AAC) — The Method
interface: aac-method
version: 1.10
status: active
maturity: 1.0
updated: 2026-08-24
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
# 1.3 (2026-08-21): doc planes + the naming canon.
#   - docs/manual/ separates the operation plane (user/operator manuals, runbooks,
#     playbooks, setup guides) from the design plane in the docs/ root
#   - filename canon (§4): lowercase kebab-case, -vMAJOR_MINOR suffix, type vocabulary;
#     the validator warns on live-folder drift (warn-only, never blocks a publish)
#   - _triage/ (quarantine, target-empty) and meta/ (vault admin) given official semantics
# 1.4 (2026-08-22): method drift made mechanical (a fresh vault was seeded pinned to a
#   stale runbook literal; the method pin was the one edge with no drift detection).
#   - validator: method-pin drift row in the drift report + dashboard panel (major = red,
#     blocks like any breaking edge); atlas-sync warns when a newer release than the pin
#     exists on the method remote
#   - policy: a NEW project pins the latest tagged release, resolved not copied
# 1.5 (2026-08-22): branch policy — declared once, enforced mechanically (sessions kept
#   discovering they were on the wrong branch; the branch is invisible ambient state).
#   - branching: block in io-graph.yml (per-project; default work dev / release main,
#     release merged by the architecture session at periodic review)
#   - enforcement: repo default branches set to work at seat creation; atlas-sync
#     switches session + vault clone to work at start; release branch protected
#   - dashboard: per-repo branch status (default vs policy, unreleased work, latest tag)
# 1.6 (2026-08-23): wiring visibility (decisions/0001, extracted from an AgentEco
#   component proposal — an unwired component must not be invisible from above).
#   - source: in each io-graph component entry is the canonical clone URL of its code
#     repo (never a machine path); machine paths are reportable drift
#   - validator --check-wiring (opt-in, CI): a repo is WIRED iff its default branch has
#     .atlas.conf with the matching SLUG and a committed AGENTS.md; warn-only
#   - Wired column joins the dashboard estate table (branch status, tag, wiring)
# 1.7 (2026-08-24): the bridge — the human/AI interface, kept deliberately simple.
#   - Nav-<Project> (formerly Dev-<Project>): the human's idea vault. Poles: Nav =
#     direction (ideas, decisions, judgment), Atlas = implementation; ideation/design
#     is mutual discussion — it happens on the bridge.
#   - _bridge/ in the Nav vault (tasks.md with per-item owners, threads/, archive/) is
#     the ONE place AI writes in Nav; see bridge-init.md. Guards/dashboard counts
#     deliberately deferred until practice settles.
# 1.8 (2026-08-24): the arch seat's own protocol — the last trust-based role written down.
#   - arch-seat.md: scope table, every-session checklist (sweep asks, answer the bridge,
#     dashboard reds, review queue) and a pull-driven periodic-review checklist
#   - component -> human asks route through the component's OWN outbox
#     (docs/needs/nav-<slug>-<topic>-vX_Y.md, to: nav), mirrored to the bridge by the
#     arch seat; no component seat holds Nav-vault credentials
#   - archive convention: answered proposals carry a resolution: pointer
# 1.9 (2026-08-25): the hook layer must not depend on the launch directory
#   (decisions/0002 — a whole estate's guards were silently inert).
#   - atlas_init --launch-dir <path>: hooks also installed where the agent actually
#     starts, with absolute paths (that file is outside any repo, so nothing machine-
#     specific is ever committed); the repo's own settings keep ${CLAUDE_PROJECT_DIR}
#   - atlas_init --verify: end-to-end self-test — installed (decisions/0001) is not the
#     same fact as firing, and only the seat can assert the second
#   - write guard ignores absolute paths outside its own repo (multi-repo seats)
# 1.10 (2026-08-25): who operates this, and who decides.
#   - manual/atlas-operating-manual.md replaces the quickstart: the human's daily and
#     periodic routine, what to discuss with the arch seat, what a PR actually is
#   - the escalation rule (§7, arch-seat 1.1): the arch seat decides structural and
#     mechanical proposals; direction, cost or scope goes to the bridge
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
  docs/                   # DESIGN plane: the architecture doc + development plan/status
    archive/              # retired design milestones (MAJOR/MINOR)
    manual/               # OPERATION plane: user & operator manuals, runbooks, playbooks
      archive/            # retired manual milestones
  docs/provides/          # OUTBOX: "what I provide" — contracts my consumers build against
    archive/              # retired versions of my provided contracts
  docs/needs/             # OUTBOX: "what I need" — requests/feedback aimed at my providers
    archive/              # retired versions of my asks
```

> **Root rule — two planes, two homes.** `docs/` root holds ONLY the component's
> *design-plane* reference documents: the architecture doc and a development plan/status.
> Documents that tell someone how to **use or operate** the component — user manuals,
> operator manuals, runbooks, playbooks, setup guides, catalogues — live in
> **`docs/manual/`**. The split is by audience and churn: the design plane answers *why it
> is built this way* and moves with the architecture; the operation plane answers *how to
> run it* and moves with releases. **Every document addressed to or negotiated with
> another component** (proposal, reply, response, finding, question, handover, review,
> schema) **lives in `provides/` or `needs/` — never in the root or `manual/`.** Rule of
> thumb: *asking side* (proposal, request, finding, question, reply-in-your-own-thread) →
> `needs/`; *answering/committing side* (response, handover, agreement, published schema)
> → `provides/`.

> **Quarantine and admin.** A `_triage/` folder (at the vault root or under a component's
> `docs/`) holds inherited, not-yet-sorted material and nothing else. It is **outside the
> protocol**: the validator and the context emitter ignore it, nothing in-protocol may
> reference into it, and its target state is **empty** — every triage doc either finds its
> one home or is deleted. The vault root may also carry `meta/` for vault-administration
> records (migration logs, curation notes); likewise outside the protocol.

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

**Filenames carry `MAJOR.MINOR`** as a `-vMAJOR_MINOR` suffix — `dprox-endpoints-v0_2.md`.
Frontmatter may carry the full `MAJOR.MINOR.PATCH`.

| Level | When | Action | Folder impact |
|---|---|---|---|
| **PATCH** | typo, clarification | commit to same file | none |
| **MINOR** | additive, backward-compatible | new `…-v1_4.md`, move prior to `archive/` | +1 in archive |
| **MAJOR** | breaking change | new `…-v2_0.md`, deprecate `1.x`, move to `archive/` | +1 in archive |

- **`0.x`** = unstable / in development. Breaking changes allowed freely between minors.
- **`1.0`+** = stable contract. MAJOR-is-breaking discipline applies. Crossing to `1.0` is
  the deliberate signal "this interface is now ratified."
- The **live folder holds only current versions** (one file per interface). Retired
  MAJOR/MINOR milestones live in `archive/`, viewable in-vault. Git holds everything else.

### The naming canon

One name shape, everywhere a document is live. (Archives are exempt: archived files keep
their historical names — renaming history breaks every wikilink that points into it.)

- **Lowercase kebab-case**: `a-z`, `0-9`, `-` only. No spaces, no parentheses, no
  capitals, no underscores outside the version suffix. `OPERATOR_MANUAL.md` and
  `Sync Compiler Architecture 0.4.1.md` are both drift.
- **One version spelling**: the suffix `-vMAJOR_MINOR` (`agent-shares-schema-v0_2.md`) —
  never `v0.2`, `V02`, or a bare `0.2` in the name.
- **Name for the global namespace.** Wikilinks resolve by basename across the whole
  vault, so a basename must be unique vault-wide: prefix with your slug or the interface
  id — `<slug-or-interface>-<topic>-<type>-vX_Y.md`.
- **The type is the last word before the version**, drawn from a small vocabulary:
  `architecture`, `plan`, `status`, `manual`, `runbook`, `playbook`, `contract`,
  `schema`, `brief`, `proposal`, `response`, `reply`, `finding`, `question`, `review`,
  `decision`, `handover` (one spelling — never "handoff").
- **Living documents carry no version suffix.** A status, development plan, TODO list, or
  catalogue evolves in place — git is its history; the §4 version machinery is for
  contracts and milestone documents, where consumers pin.
- **Exempt by convention:** `README.md`, `component.md`, `AGENTS.md`, `dashboard.md`, and
  the `NNNN-` numeric prefix on ADR files.

The validator (§8) warns on live-folder names outside the canon — warn-only; a name never
blocks a publish.

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
method:
  repo: https://github.com/OneMoreRabbit/Atlas.git
  pinned: <latest vMAJOR.MINOR at seed time — resolve from the tags, never copy a literal (§9)>
branching:                     # this project's branch policy (§9) — declared at initiation
  work: dev                    # every session, every repo, works here
  release: main                # merged by the architecture session at periodic review
components:
  - slug: agent-image
    name: Agent Image
    maturity: 0.2
    source: https://github.com/<org>/agent-image.git   # canonical clone URL of the code
                          # repo — never a machine path (1.6+, decisions/0001); this is
                          # what the estate table and --check-wiring resolve
  # ...
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
**`source:` is typed:** the component's clone URL, resolvable from any machine. A machine
path here is drift, reported like any other (a component you cannot address is a component
you cannot check).

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
2. It is reviewed at the architecture level (the arch seat — [[arch-seat]]), which
   decides structural and mechanical proposals itself and escalates anything changing
   **direction, cost or scope** to the human on the bridge.
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
no local machine switched on). It also lists live-folder documents whose names fall outside
the **naming canon** (§4) — warn-only; `archive/` and `_triage/` are never checked.

**`--check-wiring`** (opt-in; decisions/0001) extends the estate table with a **Wired**
column: for each component it fetches `.atlas.conf` and `AGENTS.md` from the `source:`
remote's default branch (blobless shallow clone — refs plus two blobs) and reports
wired / unwired / unaddressable. A repo is **wired** iff `.atlas.conf` carries the
matching `SLUG` and `AGENTS.md` is committed — what a fresh clone anywhere gets, not
what a local checkout claims. **Warn-only, always**: a component may be unwired while
being brought up; it may not be unwired *invisibly*. CI runs the flag (it has the
network and the credentials); plain local runs stay offline apart from the cheap
ref-level branch checks (§9). Wiring is the owning component's own act, in its own
repo — never installed centrally on its behalf (golden rule 2 is about ownership).

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
- **The method pin is an edge, and it drifts like one** (golden rule 3 applies to the
  method itself). `atlas-sync.sh` warns when the method remote has a newer release than
  the pin, and the validator reports method-pin drift in the drift report and dashboard
  panel — minor is informational, major is breaking. A **new** project pins the **latest
  tagged release**, resolved from the remote at seed time — never a literal copied from a
  runbook, an example, or another vault, which is stale the day after it is written.

### Branch policy — declared once, enforced mechanically

The branching model is a **per-project decision** (it follows the project's deploy and
test realities), but it is **declared, never assumed**: a `branching:` block in
`registry/io-graph.yml`, set when the project is initiated (§5). The default template is
`work: dev`, `release: main` — all development in every repo happens on `work`; the
`release` branch is merged **only by the architecture session, at periodic review**. A
trunk-only project declares `work: main` and omits `release`.

Why this must be mechanical: the current branch is *invisible ambient state* — the
working tree looks identical on every branch, nothing in a session's loop surfaces it,
and a fresh clone lands on the default branch, so "correct" would otherwise require an
active step that stateless sessions cannot remember. The policy is therefore applied at
every point where a session meets a repo:

- **The default branch of every repo — code repos and the vault — is set to the `work`
  branch** at seat creation, so every fresh clone lands correctly by default (one API
  call, e.g. `gh api repos/<org>/<repo> --method PATCH -f default_branch=dev`).
- **`atlas-sync.sh` applies the policy at session start**: it reads the block from the
  synced vault, switches the code repo and the vault clone to `work` if they are
  elsewhere, and warns loudly when it cannot (a missing `work` branch is a seat-setup
  defect, never silently invented; detached-HEAD checkouts, i.e. CI, are exempt).
- **The `release` branch is protected** (PRs only) so wrong-branch work fails at push —
  recoverably — instead of landing silently.
- **The dashboard reports per-repo branch status** (validator, §8): each repo's default
  branch against policy, work-vs-release divergence (unreleased changes awaiting the
  periodic review), and the latest release tag. Misalignment is visible red, but
  branch status never fails the run — it is seat configuration, not contract truth.

### The bridge — where direction meets implementation

Beside every project's Atlas vault sits a **Nav vault** (`Nav-<Project>`) — the human's
idea space: sketches, half-ideas, canvases, messy by right and edited by the human
alone. The poles are **Nav = direction** (ideas, priorities, decisions, judgment) and
**Atlas = implementation** (analysis, structure, execution); ideation and design are
mutual, and the mutual part happens on the **bridge**: `_bridge/` at the Nav vault
root — an owner-tagged task list plus append-only conversation threads, the one
declared place the AI writes in a Nav vault, read by the arch seat every session.
Direction agreed on the bridge is carried into the Atlas vault by the arch seat as
proposals, contracts, and ADRs — the bridge is where architecture is *agreed*, never
where it is *recorded*. Structure, rules, and setup: [[bridge-init]] — including how component seats ask
the human without ever holding Nav credentials. The arch seat's own duties, every
session and at review, are [[arch-seat]].

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
- **A guard that cannot run is a guard that must be detected.** Installing the hook
  layer is not the same fact as the hook layer firing: hooks load from the directory the
  agent *launches* in, which on a seat is not always the repo. Install them where the
  session actually starts (`atlas_init --launch-dir`) and prove it with
  `atlas_init --verify` — an inert guard reads as protection and is worse than an absent
  one (decisions/0002).
- **Guards fail closed.** A guard that cannot parse its inputs — a path, a config value,
  a hook payload — must **deny, never allow**. Every fail-open found in this subsystem
  (stdin consumed by a heredoc, an un-normalised Windows path, a CRLF-mangled config)
  passed unparseable input through as "not in scope"; the correct reading of
  unparseable is "cannot prove it's in scope", and the burden of proof is on the write.
- **One vault clone per publishing component.** Several components may *read* one vault
  checkout, but the publish branch `atlas/<slug>/<topic>` is per-checkout state — two
  components publishing through one clone fight over `HEAD` and one silently commits
  onto the other's branch. Default to one clone per component repo.
- **Ceremony follows path, not habit.** A PR touching only `components/<slug>/**`
  auto-merges once the guard and validator pass — that is publishing to your own outbox,
  and review adds nothing. A PR touching `architecture/proposals/**` or
  `registry/io-graph.yml` waits for the architecture session — that is proposing.
  Without the split, routine contract bumps queue behind a human and the outbox model
  stops being real-time.

Template workflows for the guard and the regeneration job ship in this repo under
`templates/vault-ci/` — copy them into the vault's `.github/workflows/`. The code-repo
half (sync + context scripts, local hook guards, `AGENTS.md`, `/atlas-publish`) ships as
`templates/component-repo/` — installed per [[component-init]], byte-identical in every
repo, checksum-verified against the pinned method version by `atlas-sync.sh`.

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
- **Nav vault** — `Nav-<Project>`: the human's idea space beside the Atlas vault.
  Human-edited only, trunk-only, exempt from canon and ceremony.
- **Bridge** — `_bridge/` in the Nav vault: the human/AI interface (owner-tagged
  tasks + threads); the one place the AI writes in a Nav vault. See [[bridge-init]].

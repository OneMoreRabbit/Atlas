---
title: Architecture-Above-Code (AAC) — The Method
interface: aac-method
version: "1.20"       # quoted: unquoted 1.10 would be the YAML float 1.1
status: active
maturity: 1.0
updated: 2026-09-02
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
# 1.11 (2026-08-25): three field defects from the AgentEco estate.
#   - atlas-sync never aborts on a refresh: an unguarded `pull --ff-only` under `set -e`
#     killed the whole SessionStart hook whenever the vault clone had incoming commits
#     and local edits (the mid-publish state) — reproduced against v1.9
#   - the vault clone is left alone on an atlas/<slug>/<topic> publish branch: the
#     branch policy no longer yanks an in-progress publish onto the work branch
#   - remote probes run from outside the checkout: actions/checkout's repo-local
#     http.extraheader overrode the global ATLAS_ESTATE_TOKEN credential, so private
#     repos read "unreachable at regen" while being perfectly reachable
#   - atlas-regen serialises (concurrency group) and rebases before pushing derived
#     views, with fetch-depth 0 — fixes the push race against merging component PRs
# 1.12 (2026-08-25): four defects from AgentEco run-2 seat orientations.
#   - atlas_init --verify no longer requires --vault-remote (the documented command
#     exited 2), and no longer false-greens: --launch-dir is persisted to .atlas.conf
#     ($HOME-relative) and read back; a defaulted launch dir WARNs that it proves nothing
#   - a briefing compiled from a non-work vault branch (a parked publish) carries a loud
#     STALE SOURCE header instead of being silently historical
#   - multi-repo components: install is idempotent per repo (replace, never append) and
#     the SessionStart briefing is deduplicated by slug; guards stay per-repo
# 1.13 (2026-08-26): needs route by addressee, not by graph edge (decisions/0003, from
#   an AgentEco component seat: routing was fail-open where it should be precise and
#   fail-closed where it should be permissive).
#   - `to:` is canonical; `addressed-to:` accepted as an alias (an unread key used to
#     mean "broadcast to everyone whose edge scans this folder")
#   - a needs doc naming an addressee reaches that slug wherever it lives; docs naming
#     nobody keep the edge-scoped fallback
#   - validator warns on an addressee matching no component (`nav` is valid — the human)
# 1.14 (2026-08-26): the briefing must be trustworthy about time and about obligations
#   (decisions/0004 and 0005, both from agent-skeleton field findings).
#   - the briefing and the io-graph facts (pin, policy) are read from the WORK branch,
#     not from whatever the vault clone has checked out; every briefing states the
#     branch and commit it was compiled from
#   - needs render as `answered by <doc>` or UNANSWERED, computed from the provider's
#     own `responds_to:`; the section leads with an unanswered count
# 1.15 (2026-08-28): manual vs runbook — the operation plane split by reader (from the
#   AgentEco estate; operator definitions, arch-reviewed).
#   - `manual` = human, out of practice; `runbook` = agent, no prior context. Both stay
#     in docs/manual/; the type word in the filename says which
#   - `playbook` removed from the §4 type vocabulary and reserved for Ansible playbooks
#   - existing docs split as next revised, not in a sweep
# 1.16 (2026-08-28): depending across vaults (decisions/0006; from the AgentEco estate,
#   its ADR-0008 — shared infrastructure serving five projects sat inside one of them).
#   - `external:` in io-graph — a pinned dependency on a contract homed in another
#     vault, the same shape as the existing `method:` pin; provider keeps one home,
#     consumer pins and sees drift (dashboard row, checked in CI)
#   - vault-level `needs/` — project-level asks that belong to no component; a vault
#     with zero components could previously express no dependency at all; delivered,
#     routed and lint-checked like any component outbox
#   - guidance: depend on a capability, not an implementation
#   - manual/obsidian-manual.md and manual/github-manual.md retired: vault<->GitHub sync
#     and token issue/install/rotate are estate operation (Scope 1B), rehomed in
#     Atlas-Orchestrator; the method references, never copies. What stays here is why
#     vault CI needs a credential (§8), not how to mint one
# 1.17 (2026-08-28): from the ARCPlatform seat's deployment field report.
#   - vault CI templates: both workflows resolve the vault's method pin from
#     io-graph.yml and check the method out at that tag (the pin lives in one place);
#     atlas-regen never rebases a derived view — on a rejected push it drops its own
#     commit, takes whatever won and regenerates on top (a rebase wedged the job and
#     left the dashboard disagreeing with io-graph.yml until the nightly)
#   - `external:` entries may omit `pinned:` — declaring an addressable provider is not
#     the same act as pinning a contract, and a project usually cannot see the version
# 1.18 (2026-08-31): the seat/platform boundary — a seat runs AI, not products; a
#   component that needs a platform asks the orchestrator for a container beside it
#   (component-init 2.8, arch-seat 1.2, §10; owning decision is the Orchestrator's
#   decisions/0004, referenced not copied). Requested by the orchestrator seat.
#   - cross-vault delivery: providers sweep consuming vaults and DELIVER answers into
#     components/<provider>/docs/provides/ there (already fenced by the CI guard);
#     delivered contracts are compiled into every briefing in that vault, so a seat with
#     no cross-vault credential still reads them. Pins stay optional bookkeeping.
#   - addressee matching ignores parentheticals (an aside naming another slug was
#     silently delivering to it) and warns when a match comes only from prose; `atlas`
#     joins `nav` as a well-known addressee, so a vault can ask the method owner
#   - frontmatter parsing tolerates a leading delivered-copy banner
#   - seat doctrine v0.2 (orchestrator field reports): no container runtime in a seat;
#     images are authored by the component and BUILT BY THE ESTATE, which returns
#     evidence; prototype-then-migrate is sanctioned; arch seats reshape tool-shaped
#     asks into outcome-shaped ones; a component seat's token carries Actions: Read so
#     the publish protocol's last step is verifiable (Checks is NOT grantable on
#     fine-grained PATs — `gh run list --commit`, never `gh pr checks`)
#   - the development ladder (Orchestrator decisions/0005): a component iterates freely
#     in its seat and dev container; the estate is asked when the ENVIRONMENT changes,
#     not when the code does
#   - decision adherence (§7, arch-seat 1.3, component-init 2.8): a structural change is
#     a design act — re-read decisions/ before extending a mechanism; summarised context
#     is never the design record. From two field failures of that class in three days,
#     both caught by the operator rather than by the protocol.
# 1.19 (2026-09-01): the roadmap — a vault says what it intends to ship (PR #5, from the
#   AgentEco estate; accepted with the four open decisions settled as canon).
#   - roadmap.md at the vault root, standard but never required; template + generator in
#     templates/vault-roadmap/ (generator installs at meta/roadmap_timeline.py)
#   - progress derived from checkboxes, timeline generated between markers, releases
#     chain by duration; status vocabulary fixed (shipped/in progress/at risk/next)
#   - staleness is CHECKED in the guard, not regenerated by atlas-regen: the block
#     derives from the same file a human just edited, so rewriting it races the author
#   - `roadmap` added to the §4 type vocabulary; root files stay canon-exempt
# 1.20 (2026-09-02): the pin means one thing and changes only deliberately (two
#   arc-platform findings and one operator-observed auto-update, all the same theme).
#   - release tags are IMMUTABLE vX.Y.Z; two-part pins resolve to the highest patch,
#     visibly — atlas-sync, CI and the dashboard print the resolved tag + commit.
#     Reverses the floating-tag practice: a moved v1.16 left two vaults on different
#     trees with drift green because the number matched
#   - adopting a release is a periodic-review or operator act, never a sweep act —
#     carved out of the arch seat's mechanical authority (§7/§9); the session-start
#     drift note now says so instead of reading as an instruction
#   - guard (PR #4, AgentEco): the PR base branch must match the declared policy
#     (component PRs had targeted the release branch and passed); method: and
#     external: are architecture-owned — a component branch had rewritten the pin
#   - 1.20.1 (2026-09-03, patch): atlas-context.sh exited 1 on the healthy path (EXIT
#     trap under set -e); CI policy/pin readers rejected trailing comments — the §5
#     example itself failed the guard; --verify now runs the context script and
#     asserts exit 0 (installed -> firing -> succeeding). Both from ARCPlatform's seat.
#   - bridge tasks.md write-loss under a syncing client: acknowledged, deferred by
#     the operator pending client fixes (bridge-init 1.2 notes it)
# 1.21 (unreleased): a briefing carries obligations, not history (operator review with
#   the orchestrator: a need addressed to a slug was being injected in full, every
#   session, forever — only `superseded` ever removed it).
#   - answered needs collapse to one line in the briefing; the body is one read away
#   - `status: resolved | closed | done` retire a need like `superseded` does
#   - the channel table (§6, component-init 2.9, arch-seat 1.6): rule → constitution/
#     contract; decision → proposal/ADR; ask → needs; one-off instruction → no channel
#   - raw contract artifacts (blocks-android need): `artifacts:` on a contract declares
#     OpenAPI/JSON-Schema sidecars; --emit-context delivers exact bytes to
#     ATLAS-CONTEXT.d/<interface>/ beside the briefing with path, version, size, sha256,
#     measured separately; a declared sha256 is verified; missing/mismatch FAILS emission
#     and validation. atlas-context.sh passes --artifacts-dir and excludes the dir locally
#   - one seat, one briefing: --emit-context takes N comma-separated slugs and emits a
#     single seat briefing (shared sections once, per-component sections each); the
#     context script discovers seat members from the launch dir; session total reported.
#     A 4-repo seat was injecting shared docs 4x (71% waste). affects: routes like to:
#     ('all'/'all components' reach every slug — the old substring test matched nobody).
#   - the design record is reachable: accepted decisions + standalone architecture/*.md
#     appear in the briefing as an on-demand index (reading them is retrieval, not
#     browsing), closing the contradiction between §6 and §7.
#   - routing tightened (two seats tried to converse via the bridge): `nav` is the
#     human, the bridge is human<->AI ONLY, never a seat-to-seat relay. A seat reaches
#     another by addressing its slug; the arch seat redirects a misrouted `to: nav` ask
#     instead of mirroring it; validator warns when an addressee mixes `nav` with a
#     component slug. Real seat-to-seat messaging is agent-comms' job, not the vault's.
#   - reference library (orchestrator ADR-0007): reusable know-how homed once in a
#     provider's components/<slug>/docs/library/, delivered on demand to the consumer
#     vault's root reference/ folder (verbatim, banner-marked, read-only — NOT a
#     contract/dependency). Validator indexes reference/ in the briefing on demand and
#     skips it in the naming lint (delivered copies keep their names); INDEX.md exempt.
# 1.22 (2026-09-05): communication planes (orchestrator + AgentEco agent-comms work,
#   ADR-0009). comms.md governs three planes — nav (arch↔human, the bridge), atlas
#   (arch↔component and component↔component, the vault: design & change management), and
#   an OPTIONAL hub (arch↔own-components, ephemeral chat: blockers/next-steps/proceed).
#   "Atlas holds what is true; chat carries what is next." Hub is opt-in via a comms:
#   block in io-graph; four convention-enforced rules (own-arch-only, chat-not-record,
#   stop-at-stage, lookup-vs-decision). Mechanics stay the estate's/agent-comms'.
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
> Documents that tell someone how to **use or operate** the component — manuals,
> runbooks, setup guides, catalogues — live in **`docs/manual/`**. The split is by
> audience and churn: the design plane answers *why it is built this way* and moves with
> the architecture; the operation plane answers *how to run it* and moves with releases.
>
> **Two document types share the operation plane, split by reader.** Both live in
> `docs/manual/`; the type word in the filename says which:
>
> | | **manual** | **runbook** |
> |---|---|---|
> | Reader | a human, out of practice | an agent, with no prior context |
> | Optimise for | finding the right command fast | acting correctly without asking |
> | Include | locations, commands, options, a troubleshooting table | preconditions, exact steps, verification, failure handling |
> | Exclude | rationale, history, justification | nothing needed to act; assume no session memory |
> | Length | as short as the task allows | as long as correctness requires |
>
> Rationale still belongs in the vault — in ADRs, briefs and contracts, where a reader
> goes deliberately. It should not be interleaved with instructions. Split existing
> operation-plane documents **as they are next revised**, not in a sweep.
>
> **`playbook` is not a vault document type.** The word is reserved for Ansible
> playbooks (executable code), which infrastructure components discuss constantly;
> using it for documentation too made three overlapping type words where two suffice. **Every document addressed to or negotiated with
> another component** (proposal, reply, response, finding, question, handover, review,
> schema) **lives in `provides/` or `needs/` — never in the root or `manual/`.** Rule of
> thumb: *asking side* (proposal, request, finding, question, reply-in-your-own-thread) →
> `needs/`; *answering/committing side* (response, handover, agreement, published schema)
> → `provides/`.

> **Answer them in the open.** A `provides/` document that answers a need carries
> **`responds_to:`** naming that document (a vault-relative path; `[[wikilink]]` and
> prose forms also resolve). The briefing computes each need's state from it —
> `answered by …` or **UNANSWERED** — so what a component owes is on the page rather
> than in its memory, and neither side has to poll the other. A response published
> without `responds_to:` reads as unanswered, which is the correct default: silence
> about an obligation should look like an obligation.

> **Address your asks.** Every `needs/` document carries **`to:`** naming the addressee's
> **slug** (a list for several; `nav` — the human — only when it needs human judgment,
> never to reach another component through the bridge). Delivery follows the
> addressee, not the graph: a document naming a slug reaches it wherever it sits, even
> with no edge between you — which is exactly when a component most needs to hear from a
> stranger. `addressed-to:` is accepted as an alias. A document naming nobody is
> delivered to the components whose edges scan your folder, so name your addressee unless
> you mean "all my providers". An addressee matching no component reaches nobody and the
> validator says so (§8).

> **Vault-level `needs/`.** A project may need something that belongs to **no single
> component of it** — most commonly a dependency on another vault ("this project needs a
> seat"). A vault with no components yet cannot express such a thing at all, because every
> `needs/` hangs off a component. So the vault root may carry a `needs/` folder, governed
> by exactly the rules of a component's: one topic per document, `to:` naming the
> addressee, answered by the provider publishing in its own `provides/`. Use it only for
> asks that are genuinely the project's rather than a component's; a component-owned ask
> belongs in that component's outbox, where its consumers look.

> **The roadmap.** A vault root may carry **`roadmap.md`** beside `dashboard.md`: what
> the project intends to ship, by release. It is a standard artefact but never a
> required one — a vault with no components usually wants one first, since intent
> precedes implementation, and an empty roadmap is worse than none. Direction is the
> human's; the arch seat *records* what was agreed on the bridge and keeps the derived
> view honest, it does not invent releases. Bullets are the source; the Mermaid timeline
> between `roadmap:timeline` markers is generated from them plus the frontmatter's
> `releases:` config, so progress is **derived from checkboxes**, never maintained as a
> percentage — the drift-table principle applied to intent. Release status is canon:
> `shipped`, `in progress`, `at risk`, `next` (anything else renders plain), so a status
> means the same thing in every project. Template and generator:
> `templates/vault-roadmap/` — the generator lives at `meta/roadmap_timeline.py` in the
> vault, admin tooling outside the protocol. Nothing pins a roadmap and nothing drifts
> from it: it is a record of direction, not a contract.

> **The reference library.** Reusable know-how that several projects need — an estate
> integration guide, a shared how-to — has **one home, in its provider's vault** under
> `components/<slug>/docs/library/`, and is **delivered on demand** to a consumer, never
> pre-distributed. The delivered copy lands in the consumer vault's root **`reference/`**
> folder: verbatim, banner-marked with its provider home, read-only. It is **not** a
> contract and **not** a dependency — no `external:` pin, no edge, no drift; it is shared
> knowledge, referenced where a task needs it (the briefing indexes `reference/` on
> demand, §6). A consumer asks for a library doc in its `needs/`, or a provider serves
> one while answering a related need — the same deliver-and-sweep as `provides/`, with
> `reference/` as the sink. `INDEX.md` may list a library folder.

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
  `architecture`, `plan`, `status`, `roadmap`, `manual`, `runbook`, `contract`,
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
artifacts:                     # optional (1.21): machine-readable sidecars beside this file
  - file: dprox-endpoints-openapi-v0_2.json
    sha256: 9f2c…              # optional but recommended — verified; a mismatch is an error
  - dprox-event-envelope-v0_2.schema.json
---
```

**Raw artifacts.** A contract whose truth lives in a machine-readable file — OpenAPI,
JSON Schema — declares it under `artifacts:`, beside the contract in `provides/`. The
compiled briefing then **delivers the exact bytes as files** next to `ATLAS-CONTEXT.md`
(`ATLAS-CONTEXT.d/<interface>/<file>`) and lists each with its provider path, version,
size and sha256 — never inlined, never reserialized: a generator reads bytes by path,
and a large schema belongs in its hands, not in the model's context window. A declared
`sha256` is verified; **a missing or mismatched artifact fails** both the vault's
validation and the consumer's briefing, rather than degrading to a prose warning that
invites the consumer to guess at bytes it was told to generate from. Bytes that change
under a published version are a contract change: bump the version.

---

## 5. The I/O graph (registry)

`registry/io-graph.yml` is the single source of truth for who depends on whom. It is the
edge list of a directed graph. Each edge pins the version the consumer builds against:

```yaml
method:
  repo: https://github.com/OneMoreRabbit/Atlas.git
  pinned: '<latest MAJOR.MINOR at seed time — resolve from the tags, never copy a literal (§9)>'
                             # ALWAYS quoted: unquoted 1.10 is the YAML float 1.1
branching:                     # this project's branch policy (§9) — declared at initiation
  work: dev                    # every session, every repo, works here
  release: main                # merged by the architecture session at periodic review
comms:                         # OPTIONAL (1.22): this project's seats share a chat hub
  hub: true                    # omit the block, or hub: false, for no hub — most projects
  channel: "#<project>"        # ephemeral chat only; design stays in the vault ([[comms]])
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

### Depending on something in another vault

A vault may depend on a component that lives in a **different** project vault —
shared infrastructure serving several projects, or one project consuming a capability
another produces. The `method:` block above is already this shape: a pinned dependency on
a contract whose home is elsewhere. Generalise it rather than inventing a second concept:

```yaml
external:                      # dependencies whose provider is homed in another vault
  - interface: devagent-seat-contract
    provider: agent-skeleton   # the slug in its own vault, not this one
    vault: https://github.com/<org>/Atlas-AgentEco.git
    pinned: '0.3'              # quoted, like every version
```

**Delivery, not fetching.** A consumer's seats hold no credential for the provider's
vault, so the *provider* carries the content across: it answers in its own `provides/`
and delivers a banner-marked copy to `components/<provider-slug>/docs/provides/` in the
consumer's vault, on branch `atlas/<provider-slug>/<topic>` — which the CI guard already
fences to exactly that folder, making this the one sanctioned write into another
project's vault. The provider then appears in the consumer's vault as a component would,
its contracts land in the plane every seat already reads, and the briefing carries them.
The copy is read-only where it lands; one home stays true because it is authored and
versioned only at the source. The provider **sweeps** consuming vaults for `needs/`
addressed to its slug — the consumer's only obligation is to write the ask in its own
outbox.

**`pinned:` is optional.** An entry without it *declares a provider you may address*
without claiming to build against any version of its work — which is what asking for a
capability is. A project that needs a seat says so before it consumes a seat contract,
and often cannot see the provider's vault to read a version at all; requiring a pin
there would force a guessed literal, the exact failure §9 warns about. The dashboard
shows such an entry as a declared provider with nothing pinned; add the `interface:` and
`pinned:` when you actually build against something.

The rules are the ordinary ones. The **provider** keeps one home: the contract is authored
and versioned in its own vault's `provides/`, never copied here. The **consumer** pins a
version deliberately and sees drift when the provider publishes a newer one. Asks travel
the normal outbox route — a `needs/` document in the consumer's vault addressed `to:` the
provider's slug, which the provider's arch seat picks up when reading the consuming vault.

Prefer **depending on a capability, not an implementation**. If a project needs a thing
deployed, it should say so and let the provider choose what serves it; pinning the
provider's own upstreams couples you to a supply chain that is not yours, and prevents the
provider swapping it. An `external:` entry per project, pointing at one deliberately
published contract, is the shape that survives.

Component entries may carry an optional `sink: true` flag (terminal downstream sink —
rendered distinctly in the graph). Note `role:` on a component entry is free prose;
rendering semantics live in explicit flags, never inferred from slugs or prose.
**Version values are quoted strings**, in this file and in every document's
frontmatter: unquoted `1.10` is the YAML float `1.1` and silently collides with release
1.1. The validator refuses to guess and reports an unquoted pin as red.
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

> **The briefing carries current obligations and inputs, not history.** Rules and
> contracts are injected in full every session — that persistence is the point. A need
> is injected in full only while **unanswered**; once answered it is one line, and once
> its raiser retires it (`status: resolved | closed | done | superseded`) it is gone. A
> design decision does not travel as a need at all: it is a proposal, visible while
> proposed, absorbed into constitution and contracts when accepted. Nothing in the vault
> is a channel for one-off orders — those are for the session or the bridge.

> **Three planes carry every message** ([[comms]]): the **bridge** (`nav`) to the human;
> the **vault** (atlas) for design, change management and contracts — durable; and an
> optional **hub** for ephemeral chat between an arch seat and its own components ("what
> is next", never the record). Atlas holds what is true; chat carries what is next. A
> design decision never travels the hub or the human as a relay — it is a proposal (§7).

> **The retrieval invariant: a session reads `ATLAS-CONTEXT.md`, never the vault.**
> Exact contract artifacts (§4) arrive *with* the briefing, as files beside it, and are
> reported separately from its size — receiving what a pin entitles you to is retrieval,
> not browsing.
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
   **direction, cost or scope** to the human on the bridge. One mechanical act is
   carved out of that authority: **adopting a method release** (re-pin, template
   refresh, new standard artefact) waits for periodic review or the operator (§9).
3. If accepted: `status: accepted`, moved to `architecture/decisions/`, and the constitution
   / system-context / io-graph are updated. If rejected: `status: rejected`, kept for record.
4. Because every component reads the same constitution, the decision propagates without
   manual tracing. Affected edges show as drift until consumers re-pin.

ADRs use the Nygard format: Context → Decision → Status → Consequences.

> **A structural change is a design act.** Before adding a directory, a file kind or a
> schema key, re-read `architecture/decisions/` for the governing ADR. Extending the
> mechanism already in front of you is not neutral — it is a design decision taken
> without consultation, and it presents as momentum rather than as a choice.
> **Summarised context is never the design record**: not session memory, not what
> survived compaction, not the briefing's prose. The vault is. Where a briefing and an
> ADR disagree, the ADR wins and the briefing is stale.
>
> The corollary, for deciding where a thing lives: **it belongs to what it serves
> today, not to whoever created it first.** That is the same test as §3's scope rule,
> applied to artefacts rather than documents.

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
- **Release tags are immutable.** From 1.20 every release is tagged `vMAJOR.MINOR.PATCH`
  and a tag never moves once published — content that must change after a release
  takes the next number. A two-part pin (`'1.20'`) resolves to the **highest matching
  patch**, visibly (`atlas-sync` and the dashboard print the resolved tag and commit); a
  three-part pin (`'1.20.1'`) is exact. The pin's whole contract is that a version names
  one tree; a tag that moved once left two vaults both honestly pinned `1.16` on different
  methods while drift showed green because the *number* matched. (The bare `v1.20` alias
  exists once, immutable at `.0`, only so pre-1.20 resolvers upgrade cleanly.)
- **Adopting a release is a deliberate act, never a sweep act.** Re-pinning the method,
  refreshing templates, or taking on a new standard artefact changes the ground every
  seat in the project stands on. It happens at the **periodic review** or on the
  **operator's instruction** — never because a session-start note said a newer release
  exists. That note is awareness (golden rule 3); the operator times releases. This is
  the one explicit exception to the arch seat's authority over mechanical changes (§7).
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
- **Seat** — an isolated AI platform: agent CLIs, a persistent home, repo clones, and
  the component's own build and test runs. Nothing else is installed into it.
- **Platform container** — a database, broker or product runtime a component needs,
  running *beside* its seat on the project network and owned by the orchestrator. A
  component asks for one; it never installs it into its seat, and never a container
  runtime with which to make its own. Images are authored by the component and built by
  the estate, which returns the evidence. (Scope 1B decides these —
  the owning decision is the Orchestrator's `decisions/0004-seats-and-platforms`.)
- **Constitution** — the inviolable, global principles every component reads first.
- **ADR** — Architecture Decision Record; the unit of the vertical proposal flow.
- **Nav vault** — `Nav-<Project>`: the human's idea space beside the Atlas vault.
  Human-edited only, trunk-only, exempt from canon and ceremony.
- **Bridge** — `_bridge/` in the Nav vault: the human/AI interface (owner-tagged
  tasks + threads); the one place the AI writes in a Nav vault. See [[bridge-init]].

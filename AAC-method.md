---
title: "Architecture-Above-Code (AAC) — the method"
interface: aac-method
version: "1.28"       # quoted: unquoted 1.10 would be the YAML float 1.1
status: active
updated: 2026-09-13
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
#   stop-at-stage, lookup-vs-decision, plus no-reply-when-no-action and
#   limits-are-invisible — six, aligned to the shipped agent-comms-client 0.5 §4, which
#   carries them operationally to any seat that pins it; comms.md is the source of truth.
#   Bridges are human comms: agent-to-agent notices go via the hub or a delivered doc,
#   never a project bridge. Mechanics stay the estate's/agent-comms'.
# 1.23 (2026-09-05): reorientation after compaction is automatic (orchestrator lost
#   orientation on compaction). The SessionStart hook already fires on compact (no
#   matcher); atlas-context.sh now reads the source and, on compact/resume/clear,
#   prepends a REORIENT directive so the re-injected briefing is acted on, not read past.
#   Arch seats — no slug, work the vault directly, previously NO hook — get the
#   equivalent: validator --emit-arch-context (constitution + architecture-in-force +
#   estate/drift + review queue + bridge pointer) and templates/arch-seat/ (a
#   SessionStart hook that emits it). Seat provisioning installs it.
# 1.24 (2026-09-05): the alignment gate — arch→component cascade at turn-end speed.
#   atlas-context records the compiled vault SHA (per seat member); the Stop guard
#   ls-remotes the work branch each turn end (30s throttle) and refuses to end the turn
#   while the vault is ahead of the briefing: re-brief, reconcile, then finish. Running
#   seats align by the end of their current turn — no hub, git remains the transport.
#   Fail-open (offline never blocked); stop_hook_active prevents loops. Copied-artefact
#   change: seats re-copy scripts/; works at any pin.
#   1.24.1: alignment-gate throttle keyed by vault (a multi-repo seat did N identical
#   ls-remotes per window).
#   1.24.2 (2026-09-06): arch seats get the alignment gate too (the vault moves under a
#   running arch seat: outbox PR merges, CI regen, deliveries) — templates/arch-seat/
#   atlas-arch-guard.sh (Stop): quiet when local is equal or AHEAD (unpushed work is not
#   staleness), blocks when origin holds commits the checkout lacks: pull, re-orient,
#   reconcile. And the control is now explicit (orchestrator ask): atlas_init --arch
#   installs the arch-seat hooks — role keys the installer: a component seat has a slug
#   in a wired code repo; an arch seat works the vault checkout and has none.
#   1.24.3: arch scripts resolve WHICH sibling is the vault (an arch seat's launch dir
#   holds Atlas-<P> and Nav-<P>): env > .atlas-arch.conf (written by atlas_init --arch)
#   > the unique registry/io-graph.yml fingerprint (a Nav vault never has one) > cwd.
#   1.24.4: component release convention (§9; operator ruling 2026-09-07, orchestrator
#   proposal 0001): a release is a tag on the declared release branch; consumers pin
#   exact versions, never a moving ref; upgrades are deliberate pin moves; semver with
#   0.x pilot-only; sha-pins are stopgaps. The estate owns pins and rolls (1B); the
#   method states the rule — the same tag-and-pin discipline it applies to itself.
#   1.24.5: both-hats mode (orchestrator brief; a 1.23 regression for single-seat
#   projects): ATLAS_ROLE="both" in .atlas.conf (atlas_init --role both) grants the
#   UNION scope (own outbox + architecture/** + own edges; another's outbox still
#   refused) and the publish nag names the direct-to-work flow. Declared never
#   inferred; ordinary seats unchanged. Transitional: the both→arch+component
#   migration is defined in §9 (six invariants; the estate runbook executes it).
#   1.24.6: arch-read-token standard blessed (operator ruling 2026-09-05): every arch
#   seat gets a second READ-ONLY <project>-arch-read token over its project's component
#   code repos (Contents+PRs+Actions read; never write, never org-wide). The estate
#   owns mint/route/rotate; the method states the standard (arch-seat.md).
# 1.25.0 (2026-09-07): ESTATE RELEASE — rolls up the 1.24 line: alignment gates
#   (component + arch, turn-end cascade), atlas_init --arch and vault fingerprint
#   resolution, component release convention (tag + pin), both-hats mode with defined
#   migration, arch-read-token standard.
#   1.25.1: bounded hook-payload reads (blocks finding, atlas-sessionstart-open-stdin):
#   [ -t 0 ] proves stdin is not a terminal, not that data exists — an open-empty pipe
#   (seats launched in ~/work under wrappers) made cat block FOREVER in the context
#   hooks, both Stop guards and --verify, with no visible error. All four scripts now
#   read via a 2s-bounded helper (timeout, else a single read -t line; never bare cat);
#   --verify runs the context script with stdin explicitly closed.
#   1.25.2: delivered external contracts route by CONSUMER, not vault-wide (rbac-compile
#   finding: 44% of an unrelated component's briefing was another component's delivery
#   traffic — 3-5x growth once the comms pilot made deliveries frequent). Routing
#   signals, in order: to:, consumers:, or the response's own responds_to naming
#   components/<slug>/. Named consumer gets full text; every other slug gets one index
#   line (read on demand = retrieval, §6); a delivery naming nobody stays vault-wide in
#   full (fail-open). Measured: rbac-compile 52.8KB -> 32.3KB; agent-comms unchanged.
#   1.25.3 (AgentEco PR #8 + external addressing): (a) an ABSENT addressee now warns —
#   it was the silent case with the widest reach (fails open into every seat in range);
#   `to: all` declares the broadcast honestly (same delivery, no warning; ALL_TOKENS at
#   all three delivery sites). (b) declared external providers are addressable by slug
#   OR project name derived from the vault URL (Atlas-Orchestrator -> orchestrator);
#   the unroutable warning now names the external: route and the reference/ directory.
#   1.25.4: §10 the seat model — operator/arch/component/both-hats/orchestrator defined
#   in the method (the orchestrator as a role: an ordinary both-hats seat of the estate
#   project whose JOB is scope-1B services on ask, holding what nobody else may hold —
#   boundaries stated); plus the bootstrap ladder from a bare open-source clone: first
#   agent is a both-hats seat of project one, orchestrator promoted at estate scale;
#   AgentEco's skeleton/comms named as reference implementation, not a dependency.
#   1.25.5 (operator correction): TWO front doors, not a prescribed ladder —
#   method-first (both-hats seat, grow organically, promote an orchestrator at estate
#   scale) OR orchestrator-first (estate seat stood up first provisions machines,
#   credentials, vaults and seats for everything else; the right door when
#   infrastructure exists from day one). Invariant either way: the orchestrator
#   accelerates setup, never joins the method's runtime. Plus the minimal substrate:
#   a complete offline estate on one PC via bare file-path git remotes (§9 requires
#   git, not GitHub); the forge adds the CI backstop when the estate outgrows the box.
#   1.25.6 (two orchestrator reports): (a) PINS ARE EXACT AND LITERAL — release-
#   convention v0.3 reverses the 1.20 float (a seat advanced v1.25.0->v1.25.4
#   mid-session with nobody deciding): atlas-sync and both CI templates honour the pin
#   literally, two-part pins warn and never resolve upward; upgrades are deliberate
#   operator-timed rolls, canary-able. (b) §10 orchestrator role completed from the
#   seat's first-hand brief: the delivery lane blessed as exactly one path; estate
#   registries sanctioned as derived views (generated/ joins the naming-lint skip);
#   the serve-audit/never-author boundary; isolation as a DEFINITIONAL role property
#   (operator-gated, hub send-only, tooling must refuse to make it deliverable).
#   1.25.7 (release-convention v0.2 rollout learnings, all encoded in §9): a release
#   tag is exactly annotated vX.Y.Z (bare vX.Y aliases non-normative; none minted from
#   here); the tag names the SHIPPED commit, not the tip; declared version == tag at
#   the tagged commit; bootstrap = release branch mechanically, first tag deliberately;
#   the default branch is ergonomics only — consumption is always a pinned tag.
# 1.26.0 (2026-09-08): ESTATE RELEASE — rolls up 1.25.1-1.25.7 + reconciliation:
#   bounded hook-payload reads (open-stdin hang fixed); delivered externals routed by
#   consumer (briefings -39%); silent broadcast warned, to: all declared; externals
#   addressable by project name; the seat model (§10) with the orchestrator defined
#   first-hand and isolation definitional; PINS EXACT AND LITERAL (floats retired);
#   release discipline items 6-10 (annotated vX.Y.Z only, shipped commit, version==tag,
#   bootstrap, default-branch rule). First release with no bare alias tag.
#   1.26.1 (canary catch, orchestrator): atlas_init --arch MERGES .atlas-arch.conf
#   instead of clobbering it (the rewrite dropped ATLAS_METHOD and every arch seat's
#   reorientation died on '//.atlas-method'); a fresh install records the method
#   checkout the installer ran from; --arch refuses to write hooks into the vault
#   working tree (pass --launch-dir); the script fails loudly naming the conf key,
#   after trying <vault>/.atlas-method and <launch-dir>/Atlas.
#   1.26.2-1.26.3 (AgentEco ask): release adoption needs NO broadcast to component seats —
#   arch-seat.md says so, and the atlas-sync self-drift warning now prints the exact
#   filled-in refresh command (atlas_init --slug --force ...), leaving a hand-minted
#   broadcast nothing to add. Broadcasts reliably went stale and then named an OLDER
#   version; the drift check is derived and cannot. A dead-hook seat sees neither, so
#   the broadcast covered nothing extra; hook health is --verify's job.
#   1.26.11 (operator, 2026-09-11): comms consolidated to one manual. comms.md is now
#   the single point of truth — planes + rules PLUS the operational surface (comms
#   inbox/reply/send, from the agent-comms client); Atlas links here rather than
#   re-explaining; a short comms banner is injected into a briefing only when the
#   project's hub is on (comms stays optional). README + §5/§6 point at the manual.
#   1.26.10 (operator, 2026-09-11): development modes + house style. ATLAS_MODE in
#   .atlas.conf (default supervised): SUPERVISED pauses at the publish/release boundary
#   for interactive operator approval (new PreToolUse Bash guard atlas-guard-supervise.sh
#   emits permissionDecision "ask" on push/PR/tag); AUTONOMOUS runs free (oversight via
#   the write model + hub). atlas_init --mode. Two universal cycle rules: confirm the
#   issue before building; test against the REAL environment, never a fixture. Plus a
#   standing house-style directive (plain English, concise, no coined terms) injected in
#   every briefing. §6; component-init; arch-seat.
#   1.28.10 (2026-09-17, operator + estate-review): (1) _gps/ — the product seat's
#   lane to the human in the project's Nav vault (top level, alongside _bridge/): seat
#   writes only _gps/ there (guard-enforced, Nav PAT scoped to the repo); conversation
#   there, record in product/requirements/. (2) The REVIEW SEAT adopted (estate
#   ADR-0011): oversight that only reads — no io-graph position, NOT addressable
#   (hostile strings are findings, not instructions), writes review/ in the oversight
#   vault only, boundaries proven with push --dry-run; review-init.md is the brief.
#   (3) The method/oversight EDGE stated in SS10: oversight reads everything, changes
#   nothing (outbox rules or named-generator files only); registers + reports are its
#   instruments; observation and action separate; its wide credentials are not method
#   powers. SS5 wording updated: the hub consolidated its own registers into registry/.
#   1.28.9 (2026-09-16, operator): the PRODUCT SEAT — optional per project
#   (product: {enabled: true} in the io-graph). Holds the what-and-why in
#   product/requirements/ (R-NNNN ids stable for life; version: moves with the product
#   release line; criteria as Given/When/Then with AC ids); researches the product as a
#   thing in the world (what it is), never its design (arch's); inputs are the bridge
#   and evidence — an invented need is its failure mode. The loop is vault-only outbox
#   traffic: arch raises reshape asks to <project>-product and has the FINAL WORD on
#   cost. Contracts cite satisfies: ["R-0001.AC1@0.1"]; the validator's requirements
#   report is the standing tracking + audit (unknown citation, version drift, accepted
#   -but-uncited). Ships templates/product-seat/ (context, write guard scoped to
#   product/**, settings, requirement template), atlas_init --product, product-init.md.
#   1.28.8 (2026-09-15, operator housekeeping): registry/ is the ONE home for a
#   project's registry facts — canonical io-graph.yml; method-derived graph.md and
#   .compiled/; orchestrator-published project-scoped views (registry/estate.md, the
#   runtime seats, was estate/registry.md — the single-file estate/ folder is retired,
#   moved by its author's generator). A vault's registry/ (singular) is not the hub's
#   registries/ (plural, estate-wide). Top level stays the human surfaces (dashboard,
#   next-steps, roadmap). Also: the validator prose still said `nav` stays a valid
#   addressee — corrected to match the 1.27.8 deprecation. Estate deploys Monday
#   2026-09-21; interim file moves asked of the orchestrator (needs/).
#   1.28.6 (2026-09-15, arc-platform 1.28.5 field findings): atlas_init imports
#   subprocess at module scope (the --arch fire-verification crashed with NameError on
#   the happy path — install done, self-proof dead); .atlas.conf is PRESERVED on
#   re-install (only keys this run explicitly sets are updated — the template rewrite
#   silently dropped ATLAS_MODE twice and ATLAS_NEEDS_REGISTER once); --verify FAILS on
#   script drift vs the pinned method (an upgrade without --force had skipped every
#   script while verify passed); atlas-needs.py --show never blocks on a held-open
#   stdin (select-bounded one-chunk read); ~/.atlas/needs-slugs is authoritative when
#   present (an override that could only widen was not an override); register listings
#   de-duped by path (one need to 3 of a seat's slugs is one row); the write-guard
#   refusal names every slug the seat holds. NEW: method CI at
#   .github/workflows/method-ci.yml (installed 1.28.7 under a temporary operator scope
#   grant): RUNS the installer on every push — component + arch + verify +
#   conf-preservation + stdin bound. The twice-made ask: the release's verification
#   steps were its least-tested code.
#   1.28.3 (2026-09-14, arc-platform): a seat holding two DIFFERENT publishing
#   components could write to neither outbox (two per-repo write guards, each scoped to
#   its own slug, denied the other's). The write guard now allows the UNION of the launch
#   dir's wired slugs; atlas_init installs ONE hook of each kind per launch dir (prunes
#   duplicates; --verify fails on >1 write guard). Scope unchanged outside own slugs.
#   1.28.2 (2026-09-14, arc-platform + AgentEco field findings): (ARC) the arch alignment
#   gate now fast-forwards silently past a pure derived-view regen echo (7 of 9 firings
#   were noise); atlas_init --arch prefers the pinned .atlas-method for ATLAS_METHOD,
#   warns on a non-pinned checkout, names --launch-dir in its refusal, and its verify rung
#   proves the reorientation hook FIRES from the launch dir (not just that files exist).
#   (validator) is_retired matches a retired word anywhere, not as a prefix, and adds
#   `answered`/`retired`. (atlas-needs) a failed --refresh marks the file STALE rather than
#   serving it as fresh. Canon: checks fail closed (§8, the catalogue); a re-pin certifies
#   unchanged not true (§4). (atlas-sync exit-3 on a failed pull already shipped.)
#   1.28.1 (2026-09-14, canary catches, orchestrator): atlas_init now copies AND
#   --verify checks scripts/atlas-needs.py — the *.sh-only glob shipped it in 1.28.0 but
#   never installed it, so component seats got no cross-vault needs signal while every
#   surface reported success. The Stop guard warns once when ATLAS_NEEDS_REGISTER is set
#   but the tool is absent. And README states WHO rolls: each arch seat pins its own
#   vault; the orchestrator cannot pin another (read-only token; permissions.push lies).
# 1.28.0 (2026-09-14): ESTATE RELEASE — rolls up the whole 1.27.x line. Cross-vault
#   contracts read in place (vault-read token, delivery retired); cross-vault NEEDS
#   visible to their addressee (atlas-needs.py — refresh reads the estate register, the
#   Stop guard surfaces changes) and a provider sees its cross-vault CONSUMERS; the eight
#   surfaced findings fixed (seat-briefing skip-a-member, hook pruning, both-hats write
#   guard + union briefing, gh full-sha) and PRs #9/#10 merged; four version spaces;
#   ONE arch address `<project>-arch` (bare arch warns); decisions answer nav/arch needs;
#   `external` not `unseen`; the outbox-only source named; `to: nav` on a need deprecated
#   (reach the human through your arch seat). New per-seat pieces since 1.27.0:
#   scripts/atlas-needs.py + ATLAS_NEEDS_REGISTER/ATLAS_EDGES_REGISTER, and the guards
#   already carry --show. Re-run atlas_init on components to prune stale hooks.
#   1.27.8 (2026-09-14, orchestrator pre-release brief): (1) the OUTBOX-ONLY SOURCE named
#   in §10 — a repo (the method seat) on the needs plane that is not a vault; tools read
#   its needs/ AND provides/ on main. (2) responds_to may be inline OR a block list,
#   stated (the validator already reads both). (3a) arch seats addressable as
#   <project>-arch recorded in ADR-0003. (3b) `to: nav` on a need DEPRECATED (operator
#   ruling) — a component reaches the human through its arch seat; validator warns,
#   ADR-0003 §4 superseded, bridge-init updated. (4) atlas-needs.py: live = not retired,
#   not status=="open" (dropped `active`).
#   1.27.7 (2026-09-14, orchestrator rename): a need filed in another vault is EXTERNAL,
#   not "unseen"/"invisible" — a location fact (the in-vault briefing cannot render it),
#   never a read receipt; the method has no notion of "seen". Wording aligned across
#   §5, atlas-needs.py and atlas-context.sh to match the estate register.
#   1.27.6 (2026-09-14, operator): ONE rule for the arch address — `<project>-arch`
#   inside and across vaults; bare `arch` routes but warns (context-dependent); every
#   briefing states its project name and arch address so seats can follow the rule.
#   1.27.5 (2026-09-14, operator rulings): (1) cross-vault arch addressing — `arch`
#   inside a vault, `<project>-arch` from outside (matches the estate register); optional
#   top-level `project:` in io-graph declares the name (default derived from the vault
#   name); validator routes both, and a declared external's `<project>-arch`. Method seat's
#   own outbox docs re-addressed. (2) decisions carry `responds_to:` — the answered-join
#   now reads architecture/decisions/ too, so a need settled by an ADR (every nav/arch
#   ask) shows answered and the raiser can retire it; dangling-link check covers decisions.
#   1.27.4 (2026-09-14): answers the eight
#   surfaced findings + two PRs. (D) seat briefing skips a manifest-less member with a
#   warning instead of blinding the whole seat; single-slug stays fail-closed.
#   (E) atlas_init PRUNES stale pre-1.21 SessionStart context hooks (an upgraded seat
#   emitted the seat briefing N times — 300KB); --verify fails on >1. (F) both-hats: the
#   write guard now governs every vault checkout the seat can reach (it was inert on the
#   sibling checkout an arch seat actually edits, --verify passing); and the union
#   briefing exists (--emit-arch-context --arch-only appended). (C) a provider is
#   entitled to see its cross-vault consumers: estate edges register -> consumers.md in
#   the briefing; "I provide" no longer reads exhaustive. (G) gh run list takes the FULL
#   sha. Merged PR #9 (installer echoes ATLAS_MODE; verify against the tag) and PR #10
#   (see 1.27.3). Already-fixed findings retired: 1.25.1 covered the stdin hangs.
# 1.27.3 (2026-09-14, merged PR #10 — AgentEco arch seat — three field cases against 1.26.9 in one
#   week, from three different seats, all found while cutting first releases):
#   - a re-stamp may RAISE or HOLD a contract's version, NEVER LOWER it. Taken as a
#     literal assignment the one-to-one rule walks a contract backwards whenever a
#     package version has fallen behind its own contracts, which relabels the document
#     and silently clears outstanding re-pins. Below-current means the PACKAGE is wrong.
#   - a re-stamp carries `created:` forward; only `updated:` moves. created: is the
#     INTERFACE's age, not the document's - the alternative reading makes the field
#     change meaning depending on whether a version altered any text, so it cannot be
#     interpreted without diffing against the predecessor.
#   - a published version is IMMUTABLE: terms never change inside one. 1.26.9 governs re-stamps
#     (version moves, terms identical) and was silent on the opposite case. When terms change,
#     publish a new MAJOR.MINOR at the moment they change and archive the old file unchanged -
#     editing in place makes a consumer's pin a lie with no diff on their side, and holding the
#     correction leaves a known-wrong contract in the field while the code that made it wrong is
#     already on the work branch. Immutability outranks the release mapping.
#   - `arch` is now a well-known addressee: this vault's own architecture seat, the one
#     seat a component most often has a question for and the only one with no way to be
#     named. The estate that found it had been told to write the project name, which the
#     validator rejects; invisible because the wrong addressee costs nothing observable
#     (an arch seat sweeps components' needs/ regardless - `to:` stops the FAN-OUT, not
#     the delivery). `nav` is not the substitute: it is the human via the bridge.
#   - the "fix the package" clause is scoped to contracts that appear in io-graph.yml.
#     A provides/ doc nothing pins - a governance agreement - has no consumer to be wrong
#     for, and read literally the clause demanded a spurious release to satisfy a document
#     no one tracks. Such a doc HOLDS its version; the lowering ban still applies to it.
#   - multi-repo components DECLARE which repo is the contract-stamping release line
#     (io-graph `source:`); "its component's release" assumed one release line per
#     component. Not to be resolved by inference from which docs happen to carry a
#     `contract:` field.
#   Field cases: sync-compile hit a contract numbered above its component and asked
#   rather than lowering it; rbac-compile hit a package numbered below its contract and
#   fixed the package (v0.4.1 -> v0.5.0 before tagging, avoiding dragging
#   compiled-rbac-plan 0.5 -> 0.4 and silently clearing a re-pin outstanding since
#   August); agent-image holds v0.3.0 and v0.8.0 in two repos. §4.
# 1.27.2 (2026-09-14, orchestrator cross-vault-needs finding + atlas-needs handover):
#   a seat now sees needs addressed to it from OTHER vaults. Adopted the orchestrator's
#   tool into templates/component-repo/scripts/atlas-needs.py (--refresh reads the
#   estate needs register in place; --show surfaces changes at turn end via exit 2 —
#   their interim copy printed at exit 0, which a Stop hook never shows the model, so
#   every seat was stamping needs as 'shown' that no agent saw). The briefing carries
#   ~/.atlas/needs-open.md at start/compaction (component + arch); the Stop guards call
#   --show; atlas_init --needs-register; inert with no register. Canonical to: stated
#   (slug or YAML list; warn-only on `a; b` forms); responds_to aliases addresses/answers
#   now count as answered. The method seat gains a provides/ outbox for its responses.
# 1.27.1 (2026-09-11, orchestrator external-dependency model): cross-vault contracts
#   are READ IN PLACE, not delivered. Every seat holds an estate vault-read token
#   (Atlas-* vaults, contents read; never code, never Nav — the 1.24.6 line applied to
#   vaults). §5 rewritten: declaration (external:) and access (token) are separate
#   concerns; the delivery workaround (provider pushes a copy into the consumer vault)
#   is retired for contracts (43 copies across an estate before the token); reference-
#   library remains the one sanctioned cross-vault copy. Briefings list declared
#   external deps as read-in-place pointers (validator external_index). Two credential
#   traps recorded: credential.useHttpPath=true; remove gh auth setup-git's per-host
#   helper. arch-seat + component-init updated; decisions/0006 noted.
# 1.27.0 (2026-09-11): ESTATE RELEASE — rolls up the 1.26.1-1.26.11 line: arch-installer
#   conf-merge; no-broadcast release adoption; next-steps.md; the full consistency audit;
#   the four version spaces; the development cycle stated everywhere; contracts track the
#   release line; supervised/autonomous modes + plain-English house style; comms
#   consolidated to one manual with optional context injection; pre-release doc-frontmatter
#   tidy. New per-seat knobs since 1.26: ATLAS_MODE (supervised default), and comms guidance
#   injected only when the project hub is on.
#   1.26.9 (operator ruling 2026-09-11, reversing 1.26.6's "independent contracts"):
#   a contract's version is its component's release line — provides/ carry the release
#   MAJOR.MINOR one-to-one (release v1.3.0 -> contracts at 1.3), re-stamped at a release,
#   never during patch/dev iteration (patches are bugfixes; the interface is a
#   minor-level artefact). Breaking->major, compatible->minor, matching the drift
#   consumers already read. §4 + the §9 "which release is which" contracts row. Stated
#   as discipline; no validator change (a mixed-line check would fire estate-wide until
#   contracts are re-stamped). Cost: a minor release re-stamps unchanged contracts too.
#   1.26.4 (operator ask): next-steps.md — a vault-root file the arch seat replaces
#   wholesale at end of session and at release cuts (Now / Blocked on @nav / Next
#   release ships when; <=15 lines). The operator reads it instead of asking "what's
#   next". Template in templates/vault-roadmap/; arch-seat checklist and the arch
#   reorientation briefing both carry it.
#   1.26.5: converged consistency audit — 105 adversarially-verified findings, 82
#   applied across 15 files (stale pin shapes, §10->§11 glossary refs, float language,
#   drifted duplicates); article rewritten against 1.26 reality.
#   1.26.6 (operator ruling 2026-09-09): the four version spaces disentangled in §9 —
#   method (operator-rolled tags; component seats never act on it), architecture
#   (vault: NO product tags; release = the work->release merge at periodic review),
#   code (dev iterates the PATCH position on work as unreleased states; a RELEASE
#   zeroes patch and bumps minor — 1.2.2 dev releases as v1.3.0 annotated; patch tags
#   on a released line reserved for urgent arch-approved fixes), contracts
#   (frontmatter versions, independent of code numbers). A component seat's only
#   release surface is its own code repo.
#   1.26.7-1.26.8 (operator, after a seat never read its edge provides): the
#   development cycle stated everywhere a seat looks — review architecture -> examine
#   edge provides/needs -> develop -> test -> update own provides/needs -> publish.
#   In AGENTS.md.template (standing orders), the briefing header (every session and
#   compaction), component-init and §6. Inputs are built AGAINST, not received;
#   contradicting a pinned contract is a defect even when tests pass.
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
    manual/               # OPERATION plane: user & operator manuals, runbooks, setup guides
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
> using it for documentation too made three overlapping type words where two suffice.
>
> **Every document addressed to or negotiated with
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
> you mean "all my providers" — and when you do mean that, **write `to: all`**, which
> delivers identically but says you chose it. An addressee matching no component reaches
> nobody, and an absent one reaches everyone in range; the validator says so in both
> cases (§8). A **declared external provider** (`external:` block) is addressable too —
> by its provider slug or by its project name derived from the vault URL
> (`Atlas-Orchestrator` → `orchestrator`); the ask travels by deliver-and-sweep. What
> external services exist is the estate's to publish — a service directory delivered to
> `reference/` — and which of them this project uses is the architecture session's to
> declare; a component that needs an undeclared one asks its arch seat via a proposal.
>
> **`arch` addresses your own vault's architecture seat** (added 1.27.2, on an AgentEco
> finding). The routable set was component slugs + declared externals + `nav` + `method` —
> with **no addressee for the one seat a component most often has a question for.** That
> seat's arch had told its components to write `agent-eco`, the project name, which the
> validator rejects; the error surfaced only because a single doc in the whole vault used
> it. `nav` is **not** the substitute: it is the human via the bridge, and routing a
> technical question there both misaddresses it and pushes vault traffic through a
> channel reserved for human judgment.
>
> **`<project>-product` addresses a project's product seat** (1.28.9), where one is
> declared (§10). One rule, same shape as the arch address: project-qualified
> everywhere. The traffic that belongs there: arch's feasibility and reshape asks on a
> requirement (arch has the final word on cost), and anything questioning what the
> product IS rather than how it is built. A vault with no `product:` declaration has no
> such addressee, and the validator warns on the address as unroutable.
>
> Note what the addressee is *for* here, since it is not delivery: an arch seat sweeps
> `components/*/docs/needs/` every session regardless of `to:`, so an ask reaches it
> either way. Naming `arch` stops the doc **fanning out to peers** — the fail-open
> delivery — and records who was asked. That is also why this was invisible for so long:
> the wrong addressee cost nothing observable.

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

> **`next-steps.md` — the standing answer to "what's next?"** (1.26.4, operator ask).
> A single short file at the vault root, beside `dashboard.md` and `roadmap.md`,
> **authored by the architecture session and replaced wholesale** — never appended,
> ≤15 lines, three headings: *Now (in flight)*, *Blocked on @nav*, *Next release ships
> when*. The operator reads it instead of asking; git holds the history. It is neither
> derived (that is the dashboard) nor the plan (that is the roadmap) — it is the near
> edge: what is moving today, what waits on the human, what remains before the next
> release. Refreshed at the end of every arch working session and at every release cut.
> Template: `templates/vault-roadmap/next-steps.md`.

> **Quarantine and admin.** A `_triage/` folder (at the vault root or under a component's
> `docs/`) holds inherited, not-yet-sorted material and nothing else. It is **outside the
> protocol**: the validator and the context emitter ignore it, nothing in-protocol may
> reference into it, and its target state is **empty** — every triage doc either finds its
> one home or is deleted. The vault root may also carry `meta/` for vault-administration
> records (migration logs, curation notes); likewise outside the protocol.

> Naming note: the folders are named by **content** (`provides`/`needs`), not by direction
> (`downstream`/`upstream`), because direction-names invite the inbox misreading —
> "`upstream/` must be stuff *from* upstream." It isn't; nothing is ever delivered into
> your folders. *Upstream*/*downstream* remain the terms for the **relationship** (§11).

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

> **A re-pin certifies `unchanged`, never `true`** (1.28.2, rbac-compile). A version
> bump and the drift check operate on a contract's bytes, never its claims: a false
> promise rides a byte-identical re-stamp past every fidelity check, because nothing
> executes a contract — code has tests, a contract has only readers, and its readers are
> the consumers who want the promise true. Audit a contract's claims when it is re-stamped
> (it is being touched anyway), not only when something breaks. A declared edge nobody
> performs is a **phantom edge**; pins and drift never see it, so a claim-audit is the
> only thing that will.

> **A contract's version is its component's release line** (operator ruling 2026-09-11,
> reversing the "independent versions" call of 1.26.6). A published contract carries the
> **`MAJOR.MINOR` of the release it ships in**, one-to-one: cut release `vX.Y.0` and every
> contract in your `provides/` is stamped `X.Y`. So a contract's number names the release
> it belongs to — the mismatch that made an estate's contracts unreadable against the
> release being shipped is gone. Ongoing development does **not** churn contract versions:
> patch iteration (`1.3.1`, `1.3.2` on `work`, §9) is bugfix work, and the interface is a
> **minor-level artefact** — a breaking interface change lands in a major release (the
> contract major bumps with it), a compatible addition in a minor (the contract minor
> bumps). That is exactly the drift consumers already read: same `MAJOR.MINOR` **aligned**,
> a minor ahead **re-pin when convenient**, a major ahead **breaking**. Cost, stated
> plainly: a minor release re-stamps even a contract whose body did not change, so a
> consumer may see one orange row on an interface that is byte-identical — git shows it is
> unchanged and the re-pin is trivial; traceability is worth that.
>
> **The number is coarse; the version note is the signal** (recorded on a dprox flag, 2026-09-13).
> Because contract versions couple to the release line, a breaking change *anywhere* in a component —
> a config key removed, say — re-stamps contracts it did not touch, and a consumer reading only the
> number cannot tell an interface change from an elsewhere change: `0.1 → 0.2` looks the same either
> way. That is accepted, not accidental — and it is why a re-stamped contract **carries a version note
> saying which kind of bump it was** (*"terms unchanged, release-coupled"* versus a real change). The
> note, not the number, is what a consumer's read decision runs on.

> **A re-stamp may raise or hold a contract's version, never lower it** (amendment
> 2026-09-13, on three field cases in one week from the AgentEco estate). The
> one-to-one rule reads as an assignment, and taken literally it walks a contract
> *backwards* whenever a component's package version has fallen behind its own
> contracts. Lowering is never right, for two reasons worse than the untidiness:
>
> 1. **It relabels the document.** A contract at `0.5` specifying a field that `0.4`
>    explicitly did not document cannot be re-stamped `0.4` — the number would name
>    a release whose contract said the opposite.
> 2. **It silently clears outstanding re-pins.** Consumers still pinned at the lower
>    number flip from *drift* to *aligned* with nobody reading anything. Drift that
>    resolves itself is worse than no drift report at all, because the next real one
>    is not believed.
>
> So: compute the release's `MAJOR.MINOR`; **above** the contract's current version,
> re-stamp; **equal**, hold; **below**, the *package version is the thing that is
> wrong* — stop, fix the package, release the corrected number. A contract numbered
> above its component is a signal that a MINOR-level interface change shipped as a
> PATCH at some point: a §4 violation already recorded in the contract and not yet
> in the package.

> **A published version is immutable. Terms never change inside one** (amendment 2026-09-13, on the
> first live case: a contract whose terms became *materially wrong* mid-development, not at a release).
> The rule above governs **re-stamps** — a version moving while the terms stay identical — and says
> nothing about the opposite case, which is the dangerous one. When **terms** change, publish a **new
> version at the moment the terms change**, and archive the old file unchanged. Do **not** edit the
> text of a version a consumer is pinned to, and do **not** hold a correction until the next release:
>
> - Editing in place means a consumer pinned at `0.3` **reads different terms than they pinned**,
>   which is the single thing pinning exists to prevent. Their pin becomes a lie with no diff visible
>   on their side.
> - Holding the correction leaves a **known-wrong contract in the field** for longer, and the code
>   that made it wrong is usually already on the work branch — so the window is open either way.
>
> **Immutability of a pinned version outranks the one-to-one release mapping.** Publish the next
> `MAJOR.MINOR` immediately (compatible addition → minor, breaking → major, §4 as normal); the
> component's next release then carries that number and the mapping is satisfied without a re-stamp.
> If the release lands on a *higher* number than the contract reached, re-stamp up to it at release —
> that is an ordinary re-stamp and the never-lower rule applies.

> **Immutable means byte-immutable — reference repairs included. Fix forward.** *(Asked by a component
> seat the same day the rule landed: two of their published contracts carry `[[...]]` links whose targets
> moved vaults. A link repair is plainly not a term change — and "plainly not" is the reasoning that
> nearly had them edit terms in place two hours earlier.)*
>
> **Do not edit a published version at all.** A dangling link in a published version is **not a defect;
> it is an accurate record.** That document *did* reference `[[agent-shares-architecture-v0_2]]` when it
> was published, and repairing the link would make it claim a reference **it never made** — a small
> falsification of exactly the kind immutability exists to prevent. The reader is not helped by a
> corrected history; they are helped by a current version that points somewhere real.
>
> So: **the successor version carries the corrected reference**, using the convention that survives
> re-stamps — *name the interface and its owner, not the versioned filename* (see below). And the
> practical reason to hold the line rather than carve out "obviously safe" edits: **any carve-out needs
> adjudicating per edit, and a rule that needs adjudicating decays.** The whole value of "a published
> version is immutable" is that it requires no judgement.
>
> **Corollary — cross-references should not encode a version.** Under the re-stamp rule every contract
> filename moves at every release, so a wikilink carrying `-vX_Y` is *a pointer with an expiry date*. Name
> the parts that do not move: the interface and the component that owns it. A vault sweep found **45**
> dangling versioned links, 14 of them in live documents, and **the validator checks `to:` and
> `responds_to:` but never `[[...]]`** — so the densest cross-reference mechanism in a vault is the one
> with no check behind it. Worth a warn-only check.

> **Between an io-graph merge and CI's regeneration, every briefing is confidently wrong — and the
> window must declare itself.** *(agent-compile, from a clean clone inside the ~2-minute window after
> an edge removal: their briefing served the deleted edge as an orange re-pin prompt — the exact action
> the removal comment forbade — with a provenance line naming a fresh commit. "The staleness is
> invisible precisely because the source it names is fresh.")* An edge change is authoritative in
> `io-graph.yml` at merge but *reaches seats* only when `.compiled/` regenerates; nothing marks the
> gap. Spec for the fix, not yet built: the compiled manifests carry the io-graph blob hash they were
> generated from, and `--emit-context` compares it against the checkout's `io-graph.yml` — on mismatch
> the briefing opens with a declared-degradation line ("registry views mid-regeneration; edge facts may
> be stale — re-sync in a minute") instead of silence. Same shape as atlas-sync's exit 3: continue,
> but never claim fresh.

> **An archived version is byte-identical; supersession is recorded only in the successor.** *(Ruled
> when one vault did both in one day — stamped `status: superseded` onto morning archives, archived
> byte-identical in the evening.)* The test is the ratification precedent: did the document say
> *superseded* when it was published? No — so stamping it backward makes the record claim a state it
> never carried, exactly the falsification byte-immutability exists to prevent, however true the stamp
> is *now*. The fact "X is superseded by Y" has **one home: Y's `supersedes:` frontmatter** (restate
> nothing; point) — and location carries the rest: a file under `archive/` announces its own status.
> Existing stamped archives stay as they are; editing archives to repair the convention would violate
> the convention.
>
> **And the drift row must say which kind of orange it is.** The generated label is computed from
> version distance alone, so *"re-pin when convenient"* renders identically for a re-stamp (read
> nothing) and a terms correction (read first) — a signal that says the same thing about "nothing
> changed" and "a claim you relied on was wrong" carries none of the information a consumer needs from
> it. The emitting contract **declares the class** (`repin: restamp | terms-change`, frontmatter, §10 —
> declared, not inferred from diffs), and the validator renders the words to match. Absent key renders
> the old wording.

> **A re-stamp carries `created:` forward; only `updated:` moves.** `created:` is the
> **interface's** age — when this contract was first published, carried across every
> version of it — not the date this particular document was written. The alternative
> reading (the document's own date, with the no-reset rule applying only to *pure*
> re-stamps) makes the field change meaning depending on whether a version happened to
> alter any text, so a reader cannot tell what a `created:` date denotes without
> diffing the contract against its predecessor. A field you must diff to interpret is
> not worth reading. The date a given version landed is what `updated:` and the
> changelog are for. This is the fork a seat lands on when re-stamping a contract whose
> body *did* change, so it is stated here rather than left to judgement.

> **The "fix the package" clause applies only to contracts in `io-graph.yml`** (scoping
> amendment, raised by `sync-compile` on first use of the rule above). "Below the
> contract's current version ⇒ the package is wrong" is right for a contract **with
> consumers**. A `provides/` document that is *not* an io-graph edge interface — a
> governance agreement, a schema accord, anything nothing pins — has no consumer to be
> wrong for, and read literally the clause would demand a **spurious release** of the
> component purely to satisfy a document no one tracks. Their case:
> `sync-compile-registry-schema-agreement`, `status: agreement`, at `1.0`, pinned by
> nobody, which would have forced a `1.0` release of `sync-compiler`. Such a document
> **holds its version**; the lowering prohibition still applies to it, the release
> obligation does not.

> **Multi-repo components: declare which repo is the release line.** "Its
> component's release" assumes one release line per component. A component with two
> repos has two, and the rule is ambiguous on its face — a seat holding `v0.3.0` in
> one repo and `v0.8.0` in another cannot derive from the method which number stamps
> its `provides/`. Resolve it by **declaring, not inferring** (§10): the component's
> `source:` in `io-graph.yml` names the release line that stamps contracts, and a
> second repo is declared alongside it as **not** a contract-stamping line. If a
> second repo publishes contracts of its own, it is a second component, not a second
> repo. Do **not** resolve it by observing that the other repo's docs happen to carry
> no `contract:` field and no edge — that is true only until someone adds one, and it
> is not readable from the vault.
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
- **Exempt by convention:** `README.md`, `component.md`, `AGENTS.md`, `dashboard.md`,
  `INDEX.md` (1.21, library indexes), and the `NNNN-` numeric prefix on ADR files.
- **Requirements** (1.28.9, product seat — §10) are the other exemption:
  `product/requirements/R-NNNN-<slug>.md`. The id `R-NNNN` is **stable for life** — no
  version suffix in the filename, because consumers cite the id and criteria ids, and a
  moving filename would break every citation. The `version:` frontmatter field moves
  with the **product release line**; `status:` is one of `draft`, `proposed`,
  `accepted`, `superseded`; acceptance criteria are a frontmatter `criteria:` list,
  each entry `id` (`AC1`, `AC2`, …) plus a Given/When/Then. A contract cites what it
  satisfies as `satisfies: ["R-0001.AC1", "R-0001.AC2@0.2"]` — the optional `@version`
  pins the requirement version the contract was built against, and the validator warns
  when the requirement has moved past it.

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

> **`registry/` is the one home for a project's registry facts** (1.28.8). It holds three
> kinds of file, by writer: the **canonical** `io-graph.yml` (arch-owned; components edit
> only their own edges, §9); the **method-derived** views the validator regenerates
> (`graph.md`, `.compiled/`); and **orchestrator-published, project-scoped** views —
> today `registry/estate.md`, the project's runtime seats (containers, access, repos),
> rewritten at every estate apply. Every generated file opens by naming its generator and
> refresh trigger and says *do not edit*. The old single-file `estate/` folder is retired:
> `estate/registry.md` becomes `registry/estate.md`, moved by its author (the
> orchestrator's generator), not by hand. The estate's own registers (needs, edges,
> seats, releases, audit) live in the oversight vault's `registry/` with their estate
> scope declared per file — scope is a property of the file, not the folder name. Top level remains the
> human working surfaces — `dashboard.md`, `next-steps.md`, the roadmap — which are not
> registry facts and do not move.

`registry/io-graph.yml` is the single source of truth for who depends on whom. It is the
edge list of a directed graph. Each edge pins the version the consumer builds against:

```yaml
method:
  repo: https://github.com/OneMoreRabbit/Atlas.git
  pinned: '<latest MAJOR.MINOR.PATCH at seed time — resolve from the tags, never copy a literal (§9)>'
                             # ALWAYS quoted: unquoted 1.10 is the YAML float 1.1
branching:                     # this project's branch policy (§9) — declared at initiation
  work: dev                    # every session, every repo, works here
  release: main                # merged by the architecture session at periodic review
product:                       # OPTIONAL (1.28.9): this project runs a product seat (§10)
  enabled: true                # omit the block entirely for no product seat — most projects
comms:                         # OPTIONAL (1.22): this project's seats share a chat hub
  hub: true                    # omit the block, or hub: false, for no hub — most projects; manual: [[comms]]
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
    pinned: '0.2'               # version agent-compile currently builds against
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

**Read in place, not delivery** (1.27.1, orchestrator external-dependency model). Every
seat holds an estate **vault-read** token: read-only over `Atlas-*` vaults (contents),
**never** component code repos and **never** `Nav-*` — the same line method 1.24.6 drew
for the arch-read token, applied to vaults. So a consumer reads the provider's contract
**where it lives**, in the provider's own `provides/`, and pins it in `external:`.
Nothing is copied. The one rule is the same one that governs a vault internally: every
document has one home, in its author's folder, and everyone else reads it there — a
cross-vault dependency differs only in the `to:`.

This **retires the old delivery workaround** (a provider pushing a banner-marked copy of
its contract into the consumer's vault): it existed only because consumers could not read
across vaults, and it cost one estate 43 copied documents before the token was issued.
The single surviving cross-vault copy is a **reference-library** doc into `reference/`
(§3) — a copy by design, marked as such, never a contract.

**Declaration and access are separate concerns.** `external:` says what a project *may*
depend on — architecture-owned, pinned, drift-checked. The token grants the *category*
(vaults), never a named repo, so a new edge is reviewable before any credential is
touched. The estate issues, routes and rotates the token (scope 1B). Two silent traps
it must avoid — both cost real time and neither announces itself: git needs
`credential.useHttpPath = true` (else a repo-aware router cannot tell one vault from
another and every match falls through), and any per-host helper written by
`gh auth setup-git` must be removed (git consults it first, so it answers with the
seat's own token before the router is ever asked, and the seat 403s on every other
vault while the router holds the right credential).

**Cross-vault needs reach their addressee** (1.27.2, orchestrator finding + tool). The
briefing compiles needs addressed to a seat from *its own* vault; a need filed in another
vault — correctly, in its author's outbox — is **external** to the seat that owes it: the
in-vault briefing cannot render it (a location fact, never a read receipt — the method has
no notion of "seen"). It was unreachable to that seat (58 of 78 open needs estate-wide, including every need addressed to the method
seat). Now: the estate publishes a **needs register** (a derived registry, §10) and every
seat reads it in place with the vault-read token via `scripts/atlas-needs.py` —
`--refresh` (scheduled by the estate) writes `~/.atlas/needs-open.md`; the briefing
carries that file at every start and compaction; the Stop guard's `--show` surfaces a
*change* once at turn end (exit 2 — an exit-0 print never reaches the model). It never
wakes a seat: the file is written on a timer, and the guard speaks only inside a turn
already underway. A single-vault project sets no register and the tool stays inert.
**A provider is entitled to see its cross-vault consumers** (1.27.4, agent-compile
finding). Under read-in-place the edge lives in the *consumer's* `external:` — correct,
but from the provider's vault an absent edge and no consumer look identical, and
`component.md`'s "I provide" line read as exhaustive when it was not. *Who breaks if I
change this?* is the question versioning exists to answer, so the provider must be able
to. The mechanism is the same as for needs: the estate publishes an **edges register**
(every vault's `external:` entries); `atlas-needs.py --refresh` writes the provider's
slice to `~/.atlas/consumers.md`; the briefing carries it; the "I provide" line now says
it lists in-vault consumers only. Inert without the register.

**Addressing a vault's arch seat — one rule** (1.27.6). Always **`<project>-arch`**,
inside the vault and across vaults alike, where `<project>` is the vault's declared
`project:` key in `registry/io-graph.yml` (top level; default: derived from the vault
name, `Atlas-AgentEco` → `agenteco` — declare it when the estate spells you differently,
`project: agent-eco`). A need is a document read from anywhere — the register, another
vault's sweep, the method seat — and a bare `arch` means something only to a reader who
already knows the vault. Every briefing states the project name and this address. Bare
`arch` still routes (compatibility) but the validator warns. A declared `external:`
vault's arch is `<its-project>-arch`.

**Canonical addressing:** `to:` is a slug or a YAML list of slugs (`to: [a, b]`); the
router tolerates `a; b` and trailing punctuation, but the validator warns so a naive
sweep never mis-routes. A response may name the need it answers with `responds_to:`,
`addresses:` or `answers:` — all three count as answered.
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
perform them by browsing. The validator's `--emit-context <slug>[,<slug>...]` mode (§8)
compiles all five, in that order, into a single **`ATLAS-CONTEXT.md`** — one seat, one
briefing: a seat holding several slugs lists them all and shared sections are emitted
once — each section headed with its source path and version, plus a drift summary. A
`SessionStart` hook in the code repo syncs the vault and injects this artefact
automatically — the protocol is mechanical, not
trust-based; a session that starts has already "done the reads." The hook carries **no
matcher, so it fires on compact, resume and clear as well as startup**: after a
compaction the briefing is re-injected, headed by a reorientation directive, so a seat
re-orients itself rather than waiting to be asked (1.23). An **arch seat**, which has no
slug and works the vault directly, gets the same via `--emit-arch-context` and the
`templates/arch-seat/` hook — otherwise a compacted arch seat loses its bearings with
nothing to restore them.

> **The alignment gate (1.24): an arch update reaches a running seat by the end of its
> current turn.** The briefing records which vault commit it was compiled from; the Stop
> guard compares that against the remote work branch (one `ls-remote`, 30s-throttled) at
> every turn end, and if the vault has moved it refuses to end the turn: *re-run
> `scripts/atlas-context.sh`, reconcile your in-flight work against the fresh briefing,
> then finish.* Cascade latency drops from "next compaction" to "end of current turn",
> with git still the only transport — no hub, no push channel, no polling loop. Fails
> open (offline work is never blocked); the once-per-turn flag prevents loops. Arch
> seats carry the same Stop gate against their own vault checkout (1.24.2): quiet when
> local is equal or ahead (unpushed work is not staleness), blocking only when origin
> holds commits the checkout lacks — pull, re-orient, reconcile, then finish.

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

> **The development cycle** (1.26.7): every piece of component work runs (1) review
> architecture → (2) examine the edges' provides and needs → (3) develop → (4) test →
> (5) update own `provides/`/`needs/` and publish. The method mechanises the ends —
> the briefing delivers 1–2, the Stop guard checks 5 — but the loop is the seat's
> discipline: the inputs are built AGAINST, not merely received, and code contradicting
> a pinned contract is a defect even when every test passes. (Occasioned by a live seat
> that carried its edge contracts in every briefing and never read them.)
>
> Two rules bind the cycle in every mode (1.26.10): **confirm the issue before you
> build it** — do not develop against an assumed problem — and **test against the real
> working environment and its real upstream contracts, never a fixture that encodes a
> state you have not verified.** A green test over a fiction is not evidence.

> **A seat briefing is not all-or-nothing** (1.27.4, arc-platform finding): a member with
> no compiled manifest yet — registration pending, or `atlas-regen` not yet run — is
> skipped with a warning naming it, and the other members are briefed. A component
> asking for *its own* briefing and lacking a manifest still fails closed (retrieval
> invariant). The distinction is "I cannot brief you" versus "I cannot brief one of your
> siblings"; the second must never blind the first.

> **A seat holding several publishing components shares one write guard** (1.28.3,
> arc-platform). When a seat's repos are *different* components (a handover or split), each
> repo's per-repo write guard allowed only its own slug, so two guards on one launch dir
> denied each other's outbox and the seat could write to neither. Now the write guard
> allows the **union** of the slugs wired at the launch dir, discovered from the sibling
> `.atlas.conf`s as the briefing discovers seat members; `atlas_init` installs **one**
> guard of each kind per launch dir (`--verify` fails on more than one). Scope stays as
> narrow as before for anything outside the seat's own slugs.

> **A both-hats seat gets the union briefing** (1.27.4, DiscoCat finding): the component
> briefing plus the arch half — review queue, estate and drift, `next-steps.md`, the
> bridge — via `--emit-arch-context --arch-only`, deduplicated against what the component
> briefing already carries. And the write guard now governs **every** vault checkout the
> seat can reach (`$ATLAS_VAULT`, `.atlas-arch.conf`, launch-dir siblings by io-graph
> fingerprint) — it had governed only the `.atlas` clone while a both-hats seat edited the
> sibling checkout, inert on exactly the writes it exists for, with `--verify` passing.

> **Development modes — supervised or autonomous** (1.26.10). A seat declares its
> posture in `.atlas.conf` (`ATLAS_MODE`, default **supervised**), the same way it
> declares its role. **Supervised**: the seat confirms the issue and approach with the
> operator before developing, then develops and tests freely, and **the act of
> publishing or releasing pauses for the operator** — a `PreToolUse` guard routes
> publish/release commands (push, PR, tag) to an interactive approve/deny prompt. For a
> seat working with a present human. **Autonomous**: the seat runs the full cycle and
> publishes through the write model (branch → PR → CI → arch review); oversight is the
> cascade and the hub, not a live operator. For components driven by an arch seat, often
> over the hub. Declared, never inferred — reviewable in git, like every other posture.

> **House style — plain, short, no coined terms** (1.26.10, operator directive). A seat
> replies in plain English and keeps it concise; it uses the method's established
> vocabulary and does not invent new terminology; it says less — no preamble, no
> restating the request, no summarising work already shown. Carried in every briefing.

> **The retrieval invariant: a session reads `ATLAS-CONTEXT.md`, never the vault.**
> Exact contract artifacts (§4) arrive *with* the briefing, as files beside it, and are
> reported separately from its size — receiving what a pin entitles you to is retrieval,
> not browsing.
> The briefing also carries two on-demand indexes (1.21): **architecture in force**
> (accepted decisions plus standalone `architecture/*.md`) and the `reference/`
> library (§3) — reading a doc listed there is retrieval, not browsing, either.
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
   listing `affects: [components]`. `affects:` routes delivery exactly as `to:` routes a
   need (§3): the proposal is injected into each named slug's briefing while proposed,
   `all` / `all components` tokens included.
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

> **A decision that settles a need names it** (1.27.5). An ask addressed to `nav` or
> `arch` is answered by a *decision*, not a `provides/` document — so the ADR (or the
> constitution amendment's ADR) carries `responds_to:` naming the need. The answered-join
> reads `architecture/decisions/` as well as `provides/`; the need then shows as answered
> (one line) in every briefing, and the raiser retires it (`status: resolved`) on that
> signal. This closes the loop for `to: nav` asks: arch mirrors the ask to the bridge →
> the operator decides → arch records the ADR with `responds_to:` → the raiser retires.
> Without the `responds_to:`, a nav-need sat UNANSWERED in full, indefinitely.

> **Checks fail closed, and distinguish "found nothing" from "could not look."** The
> recurring estate failure (~27 catalogued instances, AgentEco 2026-09-14) is a check
> honest about what it measured, measuring the wrong thing: a 404 or empty result read as
> "clear" when it means "forbidden" or "not reached"; an operation over an empty set
> reporting success; a hook that is installed but never fires; a re-pin that certifies the
> bytes unchanged read as certifying the claims true. Two rules follow. (1) Only an
> attempted write proves write access — a permission field or a read is not proof. (2) A
> detector raises the odds; only **failing closed** changes the outcome when nobody is
> watching — so where the method guards, it denies on an input it cannot parse, exits
> non-zero on a degraded read (`atlas-sync` exit 3), and marks a stale surface stale
> rather than rendering it fresh. The estate's living catalogue is
> `checks-that-pass-for-the-wrong-reason` (AgentEco); read it in place.

## 8. Tooling — the validator

AAC is achieved by **policy + documents**; the protocol itself is reading and writing
files. The single tool permitted to **write** vault content is the **validator** (the Atlas repo’s `tools/atlas_validate.py`, run from the project-vault root or given the vault path as first argument), and its
scope is fixed: it makes the *derived views* genuinely derived. The sync, context, init
and guard scripts around it (§6, §9, §10) are transport and hook machinery — they carry
state and enforce scope, never author vault content. It parses `io-graph.yml` +
contract frontmatter and regenerates:

- `registry/graph.md` — the rendered Mermaid graph + edge table;
- the drift panel in `dashboard.md` (between `atlas:drift` markers);
- the edge block in each `component.md` (between `atlas:edges` markers);
- `registry/.compiled/<slug>/io-manifest.yml` — each component's reading list
  (**committed**, §5);

and prints a **drift report** (every edge where `pinned ≠ latest`; exit non-zero on breaking
drift — run it as a CI gate on the vault repo, on push and nightly, so drift surfaces with
no local machine switched on). It also lists live-folder documents whose names fall outside
the **naming canon** (§4) — warn-only; `archive/`, `_triage/`, `reference/` and
`generated/` are never checked. It likewise warns — warn-only — on a `to:` addressee
matching no component or declared external, on `to: nav` on a need (deprecated 1.27.8 —
a component reaches the human through its arch seat, §3) and on an
absent addressee, which is a silent broadcast to everyone in range (§3).

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

A second mode serves the session protocol (§6): **`--emit-context <slug>[,<slug>...]`**
reads each listed component's committed `io-manifest.yml` and concatenates the five
protocol reads into ONE seat briefing, `ATLAS-CONTEXT.md` (stdout, or `--out <path>`) —
shared sections once, per-component sections each — every section headed with source
path and version, ending in a drift summary. It prints a byte/token estimate to
stderr — the cost of a session's context is a number you can watch. Its dependency is
pinned in `tools/requirements.txt`; a fresh VM installs it in one line.

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
| Method (`Atlas`) | this spec, `component-init`, the validator and seat tooling (`tools/`) | cloned per session (`$ATLAS_METHOD`, default `./.atlas-method`) |
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
  takes the next number. The pin's whole contract is that a version names one tree; a
  tag that moved once left two vaults both honestly pinned `1.16` on different methods
  while drift showed green because the *number* matched.
- **Pins are exact and literal** (release-convention v0.3, operator ruling 2026-09-07,
  **reversing the 1.20 float**). A pin is three-part (`'1.25.0'`) and is checked out
  exactly; nothing auto-flows — the float once advanced a seat's method checkout
  `v1.25.0 → v1.25.4` mid-session with nobody deciding. A two-part pin warns and
  resolves only to its bare tag, never upward. The method tags continuously and
  freely; a seat moves only when the operator rolls it — one deliberate estate-wide
  act, which also permits canarying one vault before the rest. The consequence is
  accepted knowingly: critical fixes reach seats only via a roll. Same rule for
  component pins (§9, the release convention).
- **Adopting a release is a deliberate act, never a sweep act.** Re-pinning the method,
  refreshing templates, or taking on a new standard artefact changes the ground every
  seat in the project stands on. It happens at the **periodic review** or on the
  **operator's instruction** — never because a session-start note said a newer release
  exists. That note is awareness (golden rule 3); the operator times releases. This is
  the one explicit exception to the arch seat's authority over mechanical changes (§7).
- **The method pin is an edge, and it drifts like one** (golden rule 3 applies to the
  method itself). `atlas-sync.sh` notes a newer MINOR/MAJOR release than the pin for
  periodic review — patch drift is deliberately silent, since patches reach seats via
  the operator's roll — and the validator reports method-pin drift in the drift report
  and dashboard panel — minor is informational, major is breaking. A **new** project
  pins the **latest tagged release**, resolved from the remote at seed time — never a
  literal copied from a runbook, an example, or another vault, which is stale the day
  after it is written.

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

### Which release is which — four version spaces, kept apart

Estate confusion between "releases" traced to four different things sharing the word
(operator ruling 2026-09-09). They are separate spaces with separate owners; a seat
only ever operates in its own:

| Space | Artefact | Versioned how | Released by | Consumed by |
|---|---|---|---|---|
| **Method** | the Atlas repo | `vX.Y.Z` tags; patch = iteration between rolls, minor = an estate push | the method seat, on operator instruction | vaults pin an exact version; **component seats never act on this** |
| **Architecture** | `Atlas-<Project>` vault | **no product tags** — the release act is the `work` → `release` merge at the arch seat's periodic review; the vault is continuous truth, not a shipped artefact | the arch seat | seats read compiled briefings |
| **Nav** | `Nav-<Project>` | none — the human's space has no releases | — | the human |
| **Code** | a component's own repo(s) | the scheme below | **the component seat** — its only release surface | others, pinning exact tags |
| **Contracts** | `docs/provides/*.md` | frontmatter `version:` = the **release's `MAJOR.MINOR`**, one-to-one (release `v1.3.0` → contracts at `1.3`); re-stamped when you cut a release, not during patch/dev iteration; drift = pinned vs latest (§4) | the publishing component, in step with its code release | edges pin per interface |

**A component seat does not deal in architecture releases.** Method re-pins, vault
merges, estate rolls — arch/operator acts, never a component's. Its whole release
surface is its own code repo, under this convention (operator rulings 2026-09-07 and
2026-09-09; orchestrator proposal 0001, after a client was installed from a moving
default branch and the wanted version turned out to be a transient position of that
branch — no tag, no artifact, nothing to pin to):

1. **Development iterates the patch position, on `work` — those are not releases.**
   After shipping `1.3.0`, work-branch iteration moves the manifest through `1.3.1`,
   `1.3.2`, … — development states the component manages itself, never tagged as
   releases, never consumed. **A release zeroes the patch and bumps the minor**:
   `1.2.2` in development releases as `1.3.0` — merge `work` → `release` per the
   declared `branching:` policy and lay the annotated tag `v1.3.0` there (a trunk-only
   project tags on `work`). Breaking changes bump the major. An untagged commit is not
   a release; `work` stays free to move fast. (A patch-position tag on a *released*
   line — a `v1.3.1` — is reserved for an urgent fix to that release, cut on the arch
   seat's approval: the exception, never the cadence.)
2. **A consumer pins an exact version and never installs a moving ref** — not a branch,
   not the default branch, not "latest". An install command with no ref is a defect.
3. **Upgrading is a deliberate, reviewable act**: change the declared pin, then roll. A
   component publishing a new version changes nothing until a consumer moves its pin.
4. **Semver, with the tag carrying release status**: `0.x` is in development, consumed
   only by a named pilot; `1.0.0` is the first version blessed for general consumption.
   The number is never overloaded to mean "released" — the tag is what releases.
5. **A commit-sha pin is a stopgap** for a component with no tags yet: reproducible but
   blessed by nobody — a defect to close, never a resting state.

Rolled out estate-wide (2026-09-07, 20 repos audited), the convention gained five
precise definitions the audit forced:

6. **A release tag is exactly annotated `vX.Y.Z`** — nothing else counts as a release.
   Milestone tags take a visibly different shape (`v1.0-repo-shape` is a milestone,
   not a release). Bare `vX.Y` aliases are **non-normative** where they exist
   historically; the method mints no new ones from 1.25.6.
7. **The tag names the shipped commit, not the branch tip.** What was actually built
   and shipped is often an *ancestor* of the release branch's current head; tag that
   commit, never "whatever the tip is now".
8. **Declared version == tag, at the tagged commit**: `v0.3.0` tags a commit whose own
   manifest says `0.3.0` — otherwise no registry can join "what is tagged" to "what
   runs", which is exactly how a client drifted invisibly.
9. **Bootstrap for pre-discipline repos**: creating the release branch from the
   current work head is a mechanical, additive act anyone may execute; the **first
   tag stays the seat's deliberate release act**, naming the commit it means.
10. **The default branch is developer ergonomics only** — both failure shapes were
    observed (default=work fed a moving-ref install; default=release served a stale
    tree silently). Consumption is always an explicit pinned tag, never a branch.

Who holds which half: the method states the convention; **the estate owns the pins and
the rolls** (scope 1B — it declares each seat's pinned versions, levels seats onto a
tag, and reports divergence between declared and running). Fast iteration on `work` is
healthy and untouched; reaching a consumer's seat is what requires a tag and a pin.

### Both hats — the single-seat project, and the way back out of it

A project with one agent has that agent as **both** its vault's architecture and its
component's author — the natural shape of a single-seat project, not an exotic case.
The guards support it as a **declared mode**: `ATLAS_ROLE="both"` in the committed
`.atlas.conf` (`atlas_init --role both`). Declared, never inferred — inference would
let an ordinary component seat acquire architecture rights by accident; a declaration
is reviewable in git.

**Scope is the union, nothing more**: `components/<slug>/**` + `architecture/**` + its
own io-graph edges. Another component's outbox stays refused — this is not an escape
hatch, and a seat with a separate arch counterpart keeps failing exactly as before.
The publish nag names the both-hats flow (commit authored files directly on the vault
work branch) instead of prescribing a topic-branch PR that does not apply.

**The mode is transitional by design, and its exit is defined here** so it is a
procedure, not an improvisation. The moment the vault gains a second component, the
split returns (both → arch + component):

1. **Declaration flip.** The seat's `ATLAS_ROLE` goes `both` → the arch install
   (`atlas_init --arch`); the new component seat is provisioned ordinarily with its own
   `SLUG`. Both are config diffs, reviewable.
2. **Authorship handover, not content movement.** `components/<slug>/docs/**` stays
   exactly where it is; only who may write it changes. Nothing moves on disk, so no
   reference breaks.
3. **Edges pass** to the new component seat; the arch seat keeps the graph itself.
4. **In-flight work is handed over by name** — any open topic branch or PR authored
   under both-hats gets an owner after the split, stated on the bridge.
5. **The arch seat loses outbox authorship loudly** — the guard refuses from the next
   commit; that refusal is the point of the split, never a lapse.
6. **Credentials follow role**: the new component seat gets its own write token; the
   now-pure arch seat drops to the project's arch-read standard.

The estate (scope 1B) owns the runbook that executes this — provisioning, tokens,
levelling; the six invariants above are what any such runbook must hold. The reverse
(a project shrinking back to one seat) is the same diff backwards: re-declare, hand
authorship back, note it on the bridge.

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

## 10. The seat model — who sits where, and how an estate grows

A **seat** is one agent with a standing role, a working directory, declared credentials,
and the hooks that make its protocol mechanical. Five seat types and one human:

| Seat | Owns / writes | Reads | Credentials | Defined by |
|---|---|---|---|---|
| **operator** (@nav, human) | Nav vaults; ticks the bridge; rules and releases | everything | everything | being the human |
| **arch** — one per project | `architecture/**`, io-graph, derived views; merges `release` at periodic review; writes `_bridge/` in the Nav vault and nothing else there | the vault, the bridge, component repos (read-only) | vault write + `<project>-arch-read` (Contents/PRs/Actions **read** over the project's component repos; never write, never org-wide) | works the vault checkout, no slug; `atlas_init --arch` |
| **component** — per component; may hold several repos | its code repo(s) and `components/<slug>/**` outbox (via guarded PRs) | its `ATLAS-CONTEXT.md` — never the wider vault | its repos' write + outbox path | `SLUG` in a wired repo's `.atlas.conf`; `atlas_init --slug` |
| **both-hats** — a single-seat project | the union: outbox + `architecture/**` + own edges | as arch | as both, one identity | `ATLAS_ROLE="both"`; transitional — the §9 migration is the exit |
| **product** — OPTIONAL, per project (`product:` in the io-graph) | `product/**` in the vault; `_gps/**` in the Nav vault (the product↔operator lane) — nothing else in either | the bridge (direction), evidence (users, data, the running product), the vault | vault write scoped to `product/` + a Nav PAT scoped to the project's Nav repo, `_gps/` only | `atlas_init --product`; declared in the io-graph |
| **orchestrator** — at most one per ESTATE | its own project's vault (as a both-hats seat of the estate project) + the estate services it delivers | every repo it serves (org read); machine access to every seat (SSH) | **the widest in the estate**: org-scoped tokens it mints and rotates for everyone else; infrastructure access | its service contract, below |

**The product seat holds the what-and-why; the arch seat holds the how** (1.28.9,
optional per project — declare `product: {enabled: true}` in the io-graph or the seat
does not exist). It stays in the problem space: it writes **requirements** — each with
testable acceptance criteria — into `product/requirements/`, and it **researches the
product as a thing in the world** (users, market, domain, value: what it is), never its
design (arch researches design). Its inputs are the operator's direction (the bridge)
and evidence; an invented need is this seat's failure mode, so a requirement that cites
no direction and no evidence is not a requirement. It makes no implementation
decisions, but it must hear feasibility: the arch seat raises reshape asks as ordinary
needs addressed to `<project>-product`, and **arch has the final word on cost** — a
requirement arch rules unaffordable goes back for reshaping, not into the graph. The
loop is vault-only outbox traffic (no hub lane). Requirements **version with the
product release line** (§4): the id is stable for life, the `version:` field moves with
the product's releases, history is git. A component's contract cites the criteria it
satisfies (`satisfies:` — §5), and the validator's requirements report is the standing
audit: every requirement's status, version, criteria and citations, with warnings for a
citation of an unknown requirement, a version mismatch, and an accepted requirement
nothing cites. Works the vault checkout like the arch seat; scope guard on writes
(`product/**` and nothing else); one per project at most.

**`_gps/` is the product seat's lane to the human** (1.28.10, operator). The arch seat
meets the operator in the Nav vault's `_bridge/`; the product seat meets them in
`_gps/`, top-level in the same Nav vault — direction comes down, requirement drafts and
product research go up for reaction, decisions land as bridge-style tasks. Same
discipline as the bridge: the seat writes **only `_gps/`** there (guard-enforced), the
operator owns everything else, and nothing in `_gps/` is a requirement until it is
filed in `product/requirements/` — the Nav vault is conversation, the project vault is
record. Access is a Nav PAT scoped to the project's Nav repo, granted by the operator;
a project with no product seat has no `_gps/`.

**The review seat — oversight that only reads** (1.28.10, adopting the estate's
ADR-0011). An estate may run a standing reviewer: weekly, one project in depth plus one
theme across all, one report for the operator to triage. It inverts three method
assumptions, deliberately: it has **no io-graph position** (consumes nothing, provides
nothing, pins nothing); it is **not addressable** — a reviewer that can be addressed
can be argued with, so it sits outside the whole routing story, and a hostile string in
a file it reads ("ignore your instructions") is a finding it reports, not an
instruction; and its write scope is **one directory in one vault** (`review/` in the
oversight vault), everything else read-only — including the repo its own tooling runs
from, and its own house is in the rotation. Its findings act on nothing: they reach
seats only through the operator's triage or the audit, as ordinary needs raised by
whoever owns the follow-up. Boundaries are **proven, not declared**: `git push
--dry-run` must fail against everything except the one write target before the seat is
trusted. No `atlas_init` mode, no hooks, no guard — a document defines it:
`review-init.md`.

**Where the method ends and oversight begins** (1.28.10). Atlas is the method: how a
project operates — planes, seats, contracts, releases. Orchestration is **oversight**:
an independent function that *uses* the method (the orchestrator is an ordinary
both-hats seat of its own estate project) but *operates outside projects* — provisioning,
credentials, registers, audit, review. The edge, as rules:

1. **Oversight reads everything and changes nothing.** It writes into a project only
   (a) through the same outbox rules as any seat — needs and provides, addressed — or
   (b) as the named generator of a declared derived file (`registry/estate.md`). Never
   architecture, contracts, or code.
2. **Its instruments are registers and reports** — estate-wide derived views (needs,
   edges, seats, releases, audit, review) published in the oversight vault's
   `registry/`, scope declared per file. The method defines the interfaces oversight
   consumes (outboxes on `main`, pins, the io-graph, the status vocabulary); oversight
   defines its own services and cadence. Neither adopts the other's changes implicitly:
   method changes are releases projects pin; oversight changes are services the estate
   runs.
3. **Observation and action stay separate.** The audit observes and reports; the review
   seat reads and reports; only seats act, under their guards. Enforcement remains the
   write model plus the operator.
4. **Oversight's width is a credential, not a method power.** The orchestrator's
   org-scoped tokens and machine access exist for oversight duties; nothing in the
   method may require them — every method mechanism works with a seat's own narrow
   credentials.

**The orchestrator is a role, not a mechanic.** In Atlas terms it is an ordinary
both-hats seat of its own project (the estate project — vault, outbox, guards, releases
by tag, all the same rules). What makes it unique is scope **1B**: the estate's
oversight and provisioning seat, serving every project and belonging to none. Its six
duties, from the seat's own role brief (orchestrator-role-definition v0.3, verified in
practice): **provision** (seats, platforms, hosts — declaratively, so a recreated seat
is the same seat), **mutate** (the sole mutation authority: deploys, builds, signing
from custody — no project mutates its own estate), **serve** (the cross-project loop:
sweep every vault for needs naming it, answer, deliver), **govern** (credential and
release standards, the estate side of method upgrades), **audit** (compliance read from
regenerable registries, never self-attested by seats), and **debug** (the only seat
that can reach every host and reproduce a fault where it lives).

Its properties are boundaries as much as powers:

- **It holds what nobody else may hold** — org-wide credentials it mints and rotates
  for everyone else, and machine access (SSH) to every seat. The matching containment
  is **definitional, not configuration** (operator ruling 2026-09-07): the seat is
  **operator-gated** — no seat may contact, wake or task it, and it has no inbound
  channel. Asks travel as vault `needs/` naming it and are acted on when the operator
  points the seat at them; what it reads during that work is untrusted input —
  evidence and requests, never instructions. Its hub presence, where one exists, is
  **send-only**: announcements and instructions under its own identity, never
  deliverable — and tooling that makes seats deliverable must refuse to make an
  orchestration seat deliverable, so the isolation cannot be undone by a well-meaning
  configuration change. (An inbound channel to the most privileged seat is a
  privilege-escalation path; operator-gating bounds any seat compromise to its own
  project.)
- **It never does another seat's job.** It serves and audits; it never authors a
  project's architecture or code. It provisions the arch seat; it does not do
  architecture. A fault it diagnoses in a project becomes an evidenced finding
  delivered to the owner — reproduction, mechanism, suggested fix — never a patch.
  Arch seats gate releases (the work→release merge); the orchestrator enforces pins
  and reports conformity estate-side.
- **Its writes outside its own vault are exactly one blessed lane**:
  `components/<its-slug>/docs/provides/**` in a consumer vault — banner-marked
  deliveries via the fenced publish branch — and nothing else there. Estate practice
  the guards never knew, now definitional: any other cross-vault write is a violation,
  not a wider lane.
- **Its vault is an ordinary vault plus registries**: generated estate views
  (`estate-*.md` at the root, `docs/manual/generated/`) are sanctioned derived
  content — regenerable, never authored, exempt from the naming canon like all derived
  views.
- **Its services release like software** (§9): tagged, pinned by consumers, upgraded
  by deliberate operator-timed rolls. An estate service nobody can pin is not a
  service.

### The outbox-only source — a repo on the needs plane that is not a vault

The **method seat's own repo** (this one, `Atlas`) files `needs/` and publishes
`provides/` at its root, yet has no `registry/io-graph.yml`, `components/` or
`architecture/`. It is an **outbox-only source**: it participates fully in the needs
plane — raising asks, answering them with `responds_to:` — without being a vault.

A tool walking the needs plane must therefore treat such a repo specially, because "not
a vault" and "unreadable vault" look identical from the outside and a vault-iterator
skips it in silence (this cost the estate register a day of showing answered needs as
open). The rule: **read both `needs/` and `provides/` from an outbox-only source, on its
default branch (`main`)** — its outbox traffic commits straight to `main`, untagged (§9),
so `dev` is the wrong place to look. The method seat is the only such source today; name
the shape rather than hard-code the exception.

A `responds_to:` value (which marks a need answered) is **either an inline reference or a
YAML block list**; a closure check reads both:

```yaml
responds_to: needs/x-v0_1.md      # inline
responds_to:                      # block list — the method seat's own responses use this
  - needs/x-v0_1.md
  - components/y/docs/needs/z-v0_1.md
```

### Bootstrapping from a bare clone — two ways in

The method is **self-sufficient** (nothing below requires any particular estate stack),
and an estate has two legitimate front doors. They end in the same place; which comes
first is a question of what you already have.

**Method-first (no infrastructure yet).** Clone this repo; create `Atlas-<Project>`
(README §Starting a new project); the first agent is a **both-hats seat** of that
project — `atlas_init --slug <x> --role both`. No orchestrator exists or is needed: no
SSH, no org tokens, git as the only transport. Grow organically: a second component →
the §9 split into arch + component; a second project → repeat; and when the estate
chores (tokens, machines, prompts) deserve a seat of their own, **promote an
orchestrator** — the estate project is just another `Atlas-<X>`, its both-hats seat
given the service contract, the org credentials and the machine access. From there
seats are provisioned by ask, not by hand.

**Orchestrator-first (you have, or want, infrastructure from day one).** Stand up the
**orchestrator as the first seat**: the estate project's vault, its both-hats seat, and
whatever executes its services — containers via a seat image, a cloud API, plain SSH.
It then *provisions the method for everyone else*: mints credentials, builds seat
machines, seeds the first project's vault from this repo's templates, runs
`atlas_init` on each seat, and hands the operator a running project. This is the
right door when machines and credentials already exist to be managed — the estate this
method was extracted from effectively runs this way. The invariant either way: the
orchestrator **accelerates** the method's setup and never becomes part of its runtime —
a project it provisioned runs identically to one built by hand, and keeps running if
the orchestrator disappears.

**The minimal substrate — an estate on one PC.** §9 requires git remotes, not GitHub:
a directory of bare repos (`~/estate/remotes/Atlas-<P>.git` …) with working clones
beside them is a complete, offline estate — briefings, guards, pins, tags and the
alignment gate all run against file-path remotes (this is exactly how the method's own
release tests run). What you forgo without a forge is the server-side backstop: vault
CI (the PR path guard, regen-on-merge) and protected branches. The local guards still
hold; add the forge when the estate outgrows the machine.

**The reference implementation is not a dependency.** `Atlas-Orchestrator` /
`ansible-platform` (provisioning), `agent-skeleton` (seat image) and `agent-comms`
(the optional hub) are ONE estate's implementations of the orchestrator's service
contract — the estate this method was extracted from. Any stack that delivers the same
contract fills the role; a fresh clone of Atlas can stand up a full estate — promoted
orchestrator included — with nothing but git, a config-management tool of its choice,
and this section. The hub was optional by design (`comms.md`); provisioning is
whatever executes the runbooks; the method's own machinery (vault, pins, guards,
briefings, CI) never calls out to any of them.

## 11. Glossary

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

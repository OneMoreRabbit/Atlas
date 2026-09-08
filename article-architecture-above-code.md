---
title: "Architecture-Above-Code: ten weeks of receipts"
status: draft
target: Substack
updated: 2026-09-08
---

# Architecture-Above-Code: ten weeks of receipts

*In June I published a paper design for keeping AI-built components in sync, and asked readers to poke holes in it. Reality got there first.*

## The problem, briefly, again

When you stop hand-writing code and start *directing* it, your documentation goes strange. I had eight components — compilers, a data proxy, an ingestion pipeline, an image builder — each developed by an AI agent against a brief, and their docs would not stay in agreement. One component would learn something mid-build, its design would change, and the consumer of that design would carry on believing a brief I'd copied into its folder three weeks earlier. My fix at the time was a shared library folder rebuilt by a script, which made everything worse: I eventually found the same architecture doc in **four** locations, subtly different, the only "true" one being whichever I happened to open.

The copying was the drift engine.

The June essay proposed inverting things. I don't write the code anymore; I write the *architecture*, and agents write the code beneath it. So the architecture should stop being a by-product scattered across repos and become the primary artefact — pulled **up** into one governing layer above all the code, versioned, with rules. Architecture-Above-Code. I ended the piece asking for holes.

Readers were kind. Reality was not. The design has since shipped forty-odd releases (1.26 as I write) and governs an actual estate: roughly twenty repositories and a dozen AI agent seats, daily. Nearly every idea held. Nearly every casual aside — "zero code required", "a ~100-line validator… I deferred building it" — turned out to be somewhere reality had opinions. Here are the ideas that carry the weight now, each with the incident that proved it. The incidents are real; most were filed by the agents involved, with reproduction steps.

## 1. One home per document, and folders are outboxes

Still the foundation. Every document has one author and one location, next to the component that owns it; nobody ever copies, everybody references in place. Each component keeps two public folders: `docs/provides/` (the contracts my consumers build against) and `docs/needs/` (what I want from my providers). The iron rule is that these are **outboxes**: you only ever write your own, and only ever read everyone else's. Where A's *provides* and B's *needs* disagree, that's the contract negotiation, sitting in the open instead of hiding in a broken build.

**The receipt.** Those folders were nearly named `downstream/` and `upstream/`, and the hazard was caught at the design stage: `upstream/` reads irresistibly as "stuff *from* upstream" — an inbox — so the folders were renamed by content before version 1.0 ever shipped, along with the rule that *nothing is ever delivered into your folders*. I felt clever about that until reality demonstrated the class of bug elsewhere: months later, a chat client on the estate was found faithfully storing every message its own seat had sent — the seat posts to a topic named after itself — and reading its own words back as if they were somebody's ask of it, which it then considered answering. The fix ("a seat's own messages are never for it") was found in a live message store, not in tests. Naming, it turns out, is load-bearing; so is remembering who said what.

## 2. Drift is a number, and pins never float

Every contract carries a version; every edge in the registry pins the version its consumer builds against; `pinned` versus `latest` **is** the drift, rendered as a dashboard row instead of a surprise three weeks out. The split I liked most in June — *latest for awareness, pinned for building* — survived intact and became a golden rule: you always see the newest contract the moment it lands, and you absorb it deliberately, by moving your pin.

What June didn't say, because I hadn't yet been burned, is what a version *is*. Now: a release is an **immutable annotated tag** naming the exact commit that shipped. Pins are exact and literal. Nothing upgrades unless the human rolls it.

**The receipts.** A client got installed from, effectively, whatever the default branch was that hour; when we went back for the version we'd wanted, it no longer existed — it had only ever been a transient position of a moving branch. No tag, no artefact, nothing to pin to. Separately, a seat's copy of the method upgraded itself four patch versions mid-session, with nobody anywhere having decided that, because a resolver was being helpful about "latest". Both are now impossible by rule: tags never move, pins resolve to exactly what they name, and an install command with no version in it is classed as a defect. The accepted cost, accepted knowingly: even critical fixes reach seats only when the operator rolls them.

## 3. The reads are compiled, not trusted

Time to eat something. In June I wrote "an agent reading those files does the entire job — zero code required," and of the drift validator, "a ~100-line validator… I deferred building it." The deferral lasted three days. Hand-maintained copies of the dependency graph were found drifting within a day of being written — inside the vault built to prevent that — and the validator is now some 1,400 lines and a CI gate that fails the build on breaking drift. The principle survives (the alignment *is* policy plus documents); the tooling is what makes the policy mechanical rather than aspirational.

Concretely: a session's five required reads — constitution, its edges, pinned upstream contracts, its consumers' outstanding asks, proposals in flight — are compiled by the validator into one briefing file and injected by a hook the moment a session starts, resumes, or survives a context compaction. A session that has started has, by construction, already done its reads; browsing the vault instead is explicitly forbidden. At the other end, a guard checks at every turn's close whether the vault moved since the briefing was compiled, and refuses to let the session finish while it's stale: re-brief, reconcile, then stop. (It fails open when offline. Guards that block honest work get deleted by their operators; I know myself.)

**The receipts.** A seat holding four repos was quietly paying four times over for its briefing — 71% of the injected text was the same shared sections repeated per repo, pure déjà vu — which is why it's now one seat, one briefing, measured in bytes on every emit. And a proposal addressed to "all components" once reached precisely nobody, because no component is named "all" and the router matched names. `all` is now a real token, and an addressee that matches nothing triggers a warning, on the grounds that silence about delivery should never look like delivery.

## 4. The writes are guarded, and guards fail closed

The mirror image. A component seat's vault writes travel as git — branches and pull requests, reviewable as diffs from any device — and are path-scoped by branch: a component publishing on its own branch may touch its own folders, an additive proposal, and edges naming itself, nothing else. A CI guard enforces this from the branch name alone. Routine outbox publishes auto-merge; anything touching shared architecture waits for review. (The architecture seat is the reviewer, not a PR author — it works the vault directly; that asymmetry is the point.) And the guards **fail closed**: input a guard can't parse is denied, not waved through, because every fail-open we found had been quietly waving things through.

**The receipt.** My favourite pull-request description of the year came from another project's onboarding cascade. A brand-new agent, first session, tried an edit outside its scope. The guard refused, and the refusal named the remedy. The agent read it, worked out the proposal flow from the error text, and filed a correctly-formed proposal for the same change instead — leaving its branch byte-identical on the file it had touched. No human involved at any point. As the report put it: that is the write model doing exactly what it is for. The day the guards stopped being tests and started being teachers.

## 5. Agents hold seats, and the org chart is real

June's picture was one agent per repo. The current picture is **seats**: a standing role with a working directory, declared credentials, and the hooks that make its protocol mechanical. One *arch seat* per project reviews proposals and decides the structural and mechanical ones itself, escalating only direction, cost, or scope to me — via a bridge, which is the one place human and machine actually talk. *Component seats* build; a one-agent project wears *both hats*, declared, never inferred. And at most one seat per estate is the *orchestrator*: it holds what nobody else may hold — the credentials it mints for everyone else, machine access to every seat — and precisely because of that, it is **forbidden from having an inbox**. Nobody may phone the most privileged seat. Asks travel as documents; it acts when the human points it at them. The isolation is definitional: tooling that makes seats reachable must refuse to make that one reachable.

**The receipt.** With multiple seats came the discovery that two agents will happily spend an afternoon replying "noted" and "thanks" and "acknowledged" to each other's acknowledgements, each politely completing the loop the other opened. There is now a written rule: *a message that needs no action gets no reply.* I never expected to legislate against courtesy, yet here we are.

## 6. The method eats its own drift

In June I was fond of the idea that Atlas governed itself, though the shape was wrong in the draft. The real shape: **Atlas is the method's own repo** — spec, templates, validator, seat tooling — and every project vault *pins a method version* in its registry, exactly as it pins any contract. The method appears on each project's dashboard as one more drift row; upgrading it is a deliberate, operator-timed roll, canary-able one vault at a time. Changes go through its own decisions ledger.

**The receipts.** The seats now file findings about the method's own bugs — with evidence, reproduction steps and suggested fixes — and about each other's, politely. Five of the six numbered decisions in the repo began life that way, and the changelog reads like a defect ledger written by its own inhabitants: the hook that blocked forever on an open-but-empty pipe, the briefing compiled from the wrong branch, the guard that was installed but not firing (installed, we learned, is not the same fact as *firing*, and only the running seat can attest the second). My own contribution to the ledger involves my **phone**: its sync app twice resolved a task-file conflict in favour of the phone's stale copy — a seat filed the finding — and then outdid itself by committing a stale snapshot of the method repo over two days of unreleased work, 490 deletions across nine files, discovered only because the pre-release sweep diffs everything. The work was restored from the last good commit the same day, the phone lost its write access, and the method now carries a rule occasioned by my pocket: a synced index is never the durable record.

## So what is Atlas, then

If you want the version that survives a week: Atlas is the employee handbook, the filing system and the HR policy for a small company whose entire staff wake up every morning with no memory. Everything they need to know is in the files, the files cannot lie about where they live or what version they are, and the doors they shouldn't open are locked.

More literally: a method repo — the spec you've just had summarised at you, plus templates, init scripts and the validator. A project instantiates it as an `Atlas-<Project>` vault beside its code — a plain git repo; git is the substrate everywhere, and the Obsidian vault of the June draft has been demoted to optional editor cruft in the `.gitignore`. It runs unchanged from a single offline laptop with a directory of bare git repos (a complete estate, guards and all) up to a forge-backed fleet with CI as the backstop. It's open source: **github.com/OneMoreRabbit/Atlas**. Clone it, read `AAC-method.md`, and the README's two front doors take it from there.

## What I'm still unsure about

Honesty being the house style: the guards enforce *mechanics*, and nothing yet checks that a contract is any **good** — only that it's versioned, addressed, and in the right folder. Judgment remains ungoverned, which may be a feature. Everything ultimately routes through one operator rolling releases; fine at twenty repos, unproven at two hundred, and "critical fixes wait for a roll" is a sentence I keep re-reading. The chat layer between seats has six written rules, but only the rate caps and the kill switch are enforced by machinery — the social rules are enforced by the agents' own restraint, and "enforced by convention" is precisely the kind of phrase this method exists to be suspicious of. And whether a stranger with a fresh clone can actually stand an estate up is a claim I'd currently mark, in the method's own vocabulary, as *drift until pinned*.

If you poke holes, bring reproduction steps. The agents do, and it's raised the bar around here.

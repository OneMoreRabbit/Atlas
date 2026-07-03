---
title: "Architecture-Above-Code: keeping AI-built components in sync"
status: draft
target: Substack
updated: 2026-06-30
---

# Architecture-Above-Code

*How I stopped my AI-built components from quietly drifting apart — by moving the architecture out of the code and into a vault above it.*

---

## The problem nobody warns you about

When you stop hand-writing code and start *directing* it, a strange thing happens to your documentation.

For my fileserver/agent platform I have eight components — a couple of YAML compilers, a data proxy, an ingestion pipeline, an image builder, and an Ansible layer that applies everything. Each was developed as its own project, with an AI agent, against a brief. Classic stuff: each repo had a `docs/` folder, an `integrations/` folder, design specs, user manuals.

And it kept falling out of alignment.

One component would discover something mid-build — "actually the snapshot needs an extra field" — and that insight would change its design. But the *other* component that consumed that snapshot never heard about it. The brief I'd copied into its `integrations/` folder three weeks ago was now a lie. I'd find out when something broke.

I tried the obvious fix: a "Platform Library" — one folder with the latest copy of every doc, rebuilt periodically by a script. It made things *worse*. Now the same file existed in four places: the author's repo, two consumers' `integrations/` folders, and the library. When I went looking, I found `agent-shares-architecture-v0_2_2.md` in **four** locations. Which one was true? Whichever I happened to open.

The copying *was* the drift engine.

## The realisation

The docs that mattered — the contracts between components — used to live *inside* the code. Docstrings. READMEs. Inline comments. When a human wrote the code, those docs sat next to it and travelled with it.

But I'm not writing the code anymore. I'm writing the *architecture*, and an agent writes the code beneath it. So the architecture is now the primary artefact — and I was still treating it as a by-product scattered across eight repos.

The fix is to invert that. Pull the architecture **up**, into one governing layer above all the code. Call it **Architecture-Above-Code** (AAC), in the spirit of Infrastructure-as-Code: the thing that used to be implicit and embedded becomes explicit, versioned, and authoritative.

I built it as an Obsidian vault called **Atlas**. Here's the design — and I'd genuinely like your holes poked in it.

## Two planes hold it together

Everything in AAC is one of two kinds of alignment:

**Vertical — component ⇄ architecture.** There's a `constitution.md` of inviolable principles every component reads first (I borrowed this straight from GitHub Spec Kit's `constitution`). When a component's work implies a change to the *shared* architecture, it doesn't edit the constitution — it raises an **ADR** (Architecture Decision Record, Nygard's format) in a proposals inbox. I review it; if accepted, the constitution changes and the decision is logged. Changes flow *down* to everyone because everyone reads the same file.

**Horizontal — component ⇄ component.** This is the part that fixes the drift. Each component has three folders, and the rule is they are **outboxes**: you only ever *write* to your own, and *read* everyone else's.

- `docs/provides/` — "what I **provide**." The contracts my consumers build against.
- `docs/needs/` — "what I **need**." Requests and feedback aimed at the components I depend on.
- `docs/` — my own briefs and manuals.

For an edge where A feeds B, A's guarantee lives in `A/docs/provides` and B's need lives in `B/docs/needs`. Those two files **face each other** — and where they disagree is the contract negotiation, made visible. That's just consumer-driven contracts (Fowler, 2006) applied to documentation instead of APIs.

**Nothing is ever copied.** One home per document, next to its author. Everyone else references it in place. The four-copies problem becomes structurally impossible.

## How does a component know who to read?

A registry. `io-graph.yml` is the single source of truth for the dependency graph — just an edge list:

```yaml
edges:
  - from: agent-image      # provider (upstream)
    to: agent-compile      # consumer (downstream)
    interface: snapshot-instance-fields
    mode: collaboration
    pinned: 0.2            # the version agent-compile builds against
```

From that, a component's entire reading list is determined: read the `downstream/` of everyone upstream of me; read the `upstream/` of everyone downstream of me. An agent can resolve this by hand, or a tiny script can compile it into a per-component manifest. (More on "a tiny script" below — because the honest answer is you mostly don't need one.)

## Drift becomes a number

Here's the move that makes the whole thing worth it.

Every contract carries a SemVer version in its frontmatter. Every edge in the registry *pins* the version its consumer currently builds against. So at any moment I can compare `pinned` against the latest published `version` of the contract — and that gap **is** the drift:

| pinned | latest | meaning |
|---|---|---|
| 0.2 | 0.2 | 🟢 aligned |
| 0.1 | 0.2 | 🟠 minor ahead — re-pin when convenient |
| 1.0 | 2.0 | 🔴 **breaking — review required** |

The misalignment that used to surface three weeks later as a broken build is now a coloured row on a dashboard. The dashboard is *derived* — it only reads frontmatter the components already maintain, so it can't itself drift. In Obsidian, Dataview renders it live; the graph view draws the dependency mesh for free.

This also resolves a tension I kept hitting: I want *real-time* visibility of upstream changes, but I *don't* want a silent upstream change to break me. The split is "latest for awareness, pinned for building." You always see the newest contract the instant it lands; you absorb it deliberately by bumping your pin.

## Is this just... a process? Where's the code?

Mostly, yes — and that's the point. The alignment is achieved by **policy plus documents**: the conventions, the frontmatter, the registry, and a session protocol an agent follows before it touches code ("read the constitution, resolve your edges, read pinned upstreams, check for proposals"). An agent reading those files does the entire job. Zero code required.

The only thing worth automating is the drift check — comparing version numbers across a dozen edges is exactly the mechanical bookkeeping an LLM does unreliably and expensively. A ~100-line validator emits the per-component manifests and the drift report. But it's an *accelerator for a policy*, not the source of the alignment. I deferred building it.

## It documents itself

The detail I'm fondest of: the method is registered as a component *inside the vault it governs*. Atlas has a `components/atlas/` folder, its method docs are versioned contracts, and changes to the method go through the same ADR flow as any compiler. The system is self-hosted. If the method can't keep itself aligned, it doesn't deserve to keep anything aligned.

## What I'm unsure about

This works on paper and the scaffold is built. Open questions I'd love comments on:

1. **Does the discipline hold?** The model collapses the moment someone copies instead of references. Is the dashboard's drift panel a strong enough backstop, or do I need the validator in CI from day one?
2. **Granularity of contracts.** One versioned doc per interface, or per component? I went per-interface; it might be too fine.
3. **Bidirectional collaboration edges.** My two most active components feed *each other* (Team Topologies would call it "collaboration mode"). Modelling that as two independent edges feels lossy. Better representations welcome.
4. **Is "pin and bump" too heavy** for a solo developer directing agents, versus just always floating to latest and eating the occasional break?

If you've built something like this — or think it's over-engineered for what it is — I want to hear it.

---

*Atlas is a small Obsidian vault: a constitution, an ADR ledger, a registry, per-component contract folders, and a dashboard. Happy to share the skeleton if it's useful.*

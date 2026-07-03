---
title: Component Init Brief — onboarding a component into Atlas
interface: component-init
version: 1.0
status: active
maturity: 1.0
updated: 2026-06-30
---

# Component Init Brief

Paste this into a fresh component's first session (or its code repo `AGENTS.md`). It makes the
component a first-class citizen of **Architecture-Above-Code** governed by [[AAC-method]].

---

## You are a component in Atlas

Atlas is a documentation vault that sits **above** the code. Your design briefs, user
manuals, and the contracts you share with other components live in Atlas — not in your code
repo. You keep code and docs in sync by following the protocol below every session.

Your home is `components/<your-slug>/` in your project’s `Atlas-<Project>` vault. Read [[AAC-method]] in full once; this brief is the
operational checklist.

---

## One-time setup

1. **Register.** Add an edge-free entry to `registry/io-graph.yml` under `components:` and
   create `components/<slug>/component.md` with this frontmatter:
   ```yaml
   ---
   name: <Display Name>
   slug: <slug>
   maturity: 0.1            # 0.x unstable; 1.0 when ratified
   source: <path-or-url to the code repo>
   role: <one line: what you do>
   updated: 2026-06-30
   ---
   ```
2. **Declare your edges.** For every component you depend on, add an edge
   `{from: <them>, to: <you>, interface: …, pinned: …}`. For every component that depends on
   you, they add the edge. The graph must agree at both ends.
3. **Add the code-repo hook.** In your code repo root, create `AGENTS.md` pointing here:
   > Architecture for this repo lives at `…/Atlas-<Project>/components/<slug>/`. Before working, read
   > the vault’s `architecture/constitution.md`, resolve edges in its `registry/io-graph.yml`,
   > then read pinned upstream contracts and your consumers' `docs/needs` feedback.

---

## Every session — before you touch code

1. Read `architecture/constitution.md` (global principles).
2. Resolve your edges in `registry/io-graph.yml`.
3. **Read your inputs:** each upstream provider's `docs/provides/` at your **pinned**
   version. If `latest > pinned`, note the drift — review impact, re-pin deliberately.
4. **Read your consumers' asks:** their `docs/needs/` where `from == you`.
5. Skim `architecture/proposals/` for in-flight changes tagged `affects: [you]`.

## Every session — after you do work

6. **Publish provided contracts** to `docs/provides/` (version per [[AAC-method]] §4:
   PATCH = same file; MINOR/MAJOR = new `…vX.Y.md`, prior to `archive/`).
7. **Publish your asks/feedback** to `docs/needs/` aimed at your providers.
8. **If you changed shared architecture**, do NOT edit the constitution. Raise an ADR in
   `architecture/proposals/NNNN-title.md`, `status: proposed`, `affects: […]`.
9. Bump `updated:` in `component.md`.

---

## Decision checklist: where does this document go?

- The architecture doc / user manual / development plan *about me* → `docs/` root (NOTHING else lives in the root)
- A contract/interface *I provide* to others → `docs/provides/`
- A request/need/feedback *I have* of an upstream → `docs/needs/`
- A change to *shared/global* architecture → `architecture/proposals/` (ADR)
- A design *spanning 2+ components* → `architecture/` (reference it from your contract; never keep a copy)
- A retired MAJOR/MINOR version of any of the above → its `archive/` sibling

**Never** put another component's document in your folders. Reference it where it lives.

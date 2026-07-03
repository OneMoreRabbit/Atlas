# Atlas — the Architecture-Above-Code method

**Architecture-Above-Code (AAC):** when you direct AI-built components instead of hand-writing
them, the architecture documentation becomes the primary artefact. It moves out of the code
repos into a versioned vault *above* them. This repo is the method itself — project-independent.

## The `atlas-` pattern
Every project gets its own helper vault, named `Atlas-<Project>` (e.g. `Atlas-AgentEco`),
sitting next to the project's code repos. Each project vault **pins** a version of this method
(`method:` block in its `registry/io-graph.yml`) — so method evolution surfaces as ordinary
contract drift on each project's dashboard.

## Contents
- [`AAC-method.md`](AAC-method.md) — the specification (two planes, outbox folders, versioning, I/O graph, session protocol, ADR flow).
- [`component-init.md`](component-init.md) — onboarding brief for a new component in any project vault.
- [`tools/atlas_validate.py`](tools/atlas_validate.py) — regenerates a project vault's derived views (graph, drift panel, edge blocks, io-manifests) and reports drift. Run from the project-vault root, or pass the vault path as the first argument.
- [`tools/publish.cmd`](tools/publish.cmd) — mirrors the vaults to the shared library for agent ingestion.
- [`article-architecture-above-code.md`](article-architecture-above-code.md) — Substack draft describing the method.

## Starting a new project
1. Create `Atlas-<Project>/` next to the project's code with `architecture/`, `registry/io-graph.yml` (with a `method:` pin), `components/`, `dashboard.md`.
2. Write its `constitution.md`; register components per [`component-init.md`](component-init.md).
3. Run the validator; publish to the library.

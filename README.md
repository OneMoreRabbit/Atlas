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
- [`AAC-method.md`](AAC-method.md) — the specification (two planes, outbox folders, versioning, I/O graph, session protocol, ADR flow, git transport).
- [`component-init.md`](component-init.md) — onboarding brief for a new component in any project vault: registers it, and installs the code-repo hooks (`AGENTS.md`, `scripts/atlas-sync.sh`, `SessionStart` hook, `/atlas-publish`).
- [`tools/atlas_validate.py`](tools/atlas_validate.py) — regenerates a project vault's derived views (graph, drift panel, edge blocks, io-manifests) and reports drift; `--emit-context <slug>` compiles a component's session reading list into one `ATLAS-CONTEXT.md`. Run from the project-vault root, or pass the vault path as the first argument. Dependency pinned in [`tools/requirements.txt`](tools/requirements.txt).
- [`tools/atlas_init.py`](tools/atlas_init.py) — one-command installer for `templates/component-repo/`: `python .atlas-method/tools/atlas_init.py --slug <slug> --vault-remote <url>` from a code-repo root. Stdlib only; idempotent; merges hooks into an existing `.claude/settings.json`.
- [`templates/vault-ci/`](templates/vault-ci/) — GitHub Actions templates for project vaults: `atlas-guard.yml` (PR path guard — the write model, AAC-method §9) and `atlas-regen.yml` (derived views regenerated on the default branch).
- [`templates/component-repo/`](templates/component-repo/) — the installable code-repo half: sync/context scripts (byte-identical everywhere, config in `.atlas.conf`, checksum-verified against the pinned method), local hook guards (write scope, publish nag), `AGENTS.md` template, `/atlas-publish`.
- [`article-architecture-above-code.md`](article-architecture-above-code.md) — Substack draft describing the method.

## Starting a new project
1. Create an `Atlas-<Project>` vault as a **private git repo with a remote** — this is the
   transport; there are no shares, mirrors, or machine paths (AAC-method §9). Seed it with
   `architecture/`, `registry/io-graph.yml` (with a `method:` pin), `components/`,
   `dashboard.md`, a `.gitattributes` containing `* text=auto eol=lf`, and a `.gitignore`
   for editor cruft only (never `registry/.compiled/` — the compiled manifests are
   committed, published contracts).
2. Write its `constitution.md`; register components per [`component-init.md`](component-init.md),
   which also wires each code repo to resolve the vault via `$ATLAS_VAULT` (a per-session
   clone) and to inject `ATLAS-CONTEXT.md` at session start.
3. Copy [`templates/vault-ci/`](templates/vault-ci/) into the vault's `.github/workflows/`
   — these are **templates**; they run in the vault repo, not here. `atlas-guard.yml`
   enforces the write model on PRs (branch `atlas/<slug>/<topic>` may only touch its own
   outbox paths); `atlas-regen.yml` regenerates and commits the derived views on the
   default branch after each merge and nightly — so the compiled manifests reflect merged
   truth, and breaking drift is detected with no local machine switched on.
4. Run the validator once locally as a check; commit the authored seed and push.

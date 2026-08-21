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
- [`AAC-method.md`](AAC-method.md) — the specification (two planes, outbox folders, versioning + naming canon, I/O graph, session protocol, ADR flow, git transport, write model).
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

## Upgrading an existing vault to a new method version

A vault adopts a method release by re-pinning and then installing what the release ships —
the pin is honoured mechanically (`atlas-sync.sh` checks out the method at tag `v<pinned>`),
so declare it only once the vault actually conforms:

1. **Re-pin.** Set `method: pinned:` in `registry/io-graph.yml` to the release
   (`MAJOR.MINOR`). From here the vault is governed by that version of
   [`AAC-method.md`](AAC-method.md); read its frontmatter changelog for what the jump adds.
2. **Vault hygiene.** Ensure `.gitattributes` (`* text=auto eol=lf`), a cruft-only
   `.gitignore`, and that `registry/.compiled/` is committed (1.1+: it is the published
   retrieval payload, not a build artefact).
3. **Install the vault CI** (1.2+). Copy [`templates/vault-ci/`](templates/vault-ci/) into
   the vault's `.github/workflows/`; confirm the guard fails closed (a PR from a
   non-`atlas/<slug>/<topic>` branch must be rejected, not ignored). Enable auto-merge for
   outbox-only PRs per the merge-policy note in `atlas-guard.yml`.
4. **Install the code-repo half in every component repo** (1.1+). From each code-repo root:
   `git clone --depth 1 <method-remote> .atlas-method`, then
   `python .atlas-method/tools/atlas_init.py --slug <slug> --vault-remote <vault-url>`;
   commit the result (`AGENTS.md` and `.atlas.conf` must be committed). Details and the
   manual equivalent: [`component-init.md`](component-init.md) §4.
5. **History is grandfathered.** Commits that predate the write model stay as they are;
   the branch/guard discipline applies from the re-pin forward. There is nothing to rewrite.
6. **Sort the doc planes and names** (1.3+). In each component, move user/operator
   manuals, runbooks, playbooks and setup guides from the `docs/` root into
   `docs/manual/`; rename live-folder files to the naming canon (AAC-method §4 —
   lowercase kebab-case, `-vX_Y` version suffix; archives keep their historical names);
   file or delete everything in `_triage/` until it is empty. The validator lists the
   names outside the canon (warn-only), so run it for the worklist.
7. **Regenerate from merged truth.** Let `atlas-regen.yml` run on the default branch (or
   run the validator there once and commit the derived views) so the compiled manifests
   reflect the upgraded state.

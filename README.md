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
- [`tools/atlas_validate.py`](tools/atlas_validate.py) — regenerates a project vault's derived views (graph, drift panel, edge blocks, io-manifests) and reports drift; `--emit-context <slug>` compiles a component's session reading list into one `ATLAS-CONTEXT.md`; `--check-wiring` verifies each component repo actually carries the committed Atlas half (warn-only, for CI). Run from the project-vault root, or pass the vault path as the first argument. Dependency pinned in [`tools/requirements.txt`](tools/requirements.txt).
- [`tools/atlas_init.py`](tools/atlas_init.py) — one-command installer for `templates/component-repo/`: `python .atlas-method/tools/atlas_init.py --slug <slug> --vault-remote <url>` from a code-repo root. Stdlib only; idempotent; merges hooks into an existing `.claude/settings.json`. `--launch-dir <path>` when the agent starts outside the repo (a seat in the clone parent) — otherwise the hooks never load; `--verify` self-tests an install end to end (decisions/0002).
- [`templates/vault-ci/`](templates/vault-ci/) — GitHub Actions templates for project vaults: `atlas-guard.yml` (PR path guard — the write model, AAC-method §9) and `atlas-regen.yml` (derived views regenerated on the default branch).
- [`templates/component-repo/`](templates/component-repo/) — the installable code-repo half: sync/context scripts (byte-identical everywhere, config in `.atlas.conf`, checksum-verified against the pinned method), local hook guards (write scope, publish nag), `AGENTS.md` template, `/atlas-publish`.
- [`bridge-init.md`](bridge-init.md) — the human/AI interface: `_bridge/` in each project's `Nav-<Project>` vault (owner-tagged tasks + threads), the one place AI writes in the human's idea space. Deliberately simple; iterated from practice.
- [`manual/`](manual/) — the method's own operation plane (§3 applied to itself): [`atlas-operating-manual.md`](manual/atlas-operating-manual.md) — **how you operate Atlas**: daily and periodic routine, what to discuss with the arch seat, which PRs are yours.
  Estate operation is **not** method documentation and is not kept here (one home per document): GitHub tokens — issue, install, rotate — live in `Atlas-Orchestrator` → `components/ansible-platform/docs/manual/new-seat-3-github-tokens.md`, and vault ↔ GitHub sync on desktop and Android in `…/new-seat-4-obsidian-sync.md`. Both retired at method 1.16. What the method still states for itself is *why* vault CI wants a credential — §8 (`--check-wiring`) and the comment on the secret in `templates/vault-ci/atlas-regen.yml`.
- [`templates/vault-roadmap/`](templates/vault-roadmap/) — the roadmap artefact: `roadmap.md` (what the project intends to ship, by release) and `roadmap_timeline.py`, which regenerates its Mermaid timeline from the bullets and the frontmatter's `releases:` config. Copy into a vault root and `meta/`. Standard, never required.
- [`arch-seat.md`](arch-seat.md) — the architecture session's own protocol: what it owns, its every-session checklist (sweep component asks, answer the bridge, dashboard reds, review queue) and its periodic review.
- [`decisions/`](decisions/) — the method's own ADR log (the method is governed by its own rules; methodology-level ADRs raised in project vaults are extracted here on acceptance).
- [`article-architecture-above-code.md`](article-architecture-above-code.md) — Substack draft describing the method.

## Starting a new project
1. Create an `Atlas-<Project>` vault as a **private git repo with a remote** — this is the
   transport; there are no shares, mirrors, or machine paths (AAC-method §9). Seed it with
   `architecture/`, `registry/io-graph.yml` (with a `method:` pin and a `branching:`
   policy — default `work: dev`, `release: main`; AAC-method §9), `components/`,
   `dashboard.md`, a `.gitattributes` containing `* text=auto eol=lf`, and a `.gitignore`
   for editor cruft only (never `registry/.compiled/` — the compiled manifests are
   committed, published contracts).
   **A new project always pins the latest tagged release** — resolve it, never copy it:
   `git ls-remote --tags <method-remote>` and take the highest `vMAJOR.MINOR`. The pin
   exists to keep building stable *after* you start; it is never a reason to start on an
   old method. A pin copied as a literal from a runbook, an example, or another vault is
   stale the day after it is written — `atlas-sync` and the validator both surface method
   drift, but seeding correctly costs one command.
   **Set every repo's default branch — the vault's and each code repo's — to the policy
   `work` branch** (`gh api repos/<org>/<repo> --method PATCH -f default_branch=dev`),
   and protect the `release` branch. Fresh clones then land on the right branch by
   default; `atlas-sync` re-applies the policy each session; the dashboard reports
   per-repo branch status.
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
so declare it only once the vault actually conforms.

> **Not everything needs a re-pin.** Two classes of artefact ship differently:
> **pinned** — `AAC-method.md` and `tools/` are resolved at the vault's `method:` tag, so
> changes there reach a vault only when it re-pins. **Copied** — `templates/vault-ci/` and
> `templates/component-repo/` are files a vault or code repo owns a copy of; re-copy them
> to pick up a fix **at any pin**, and CI keeps running the method version you pin. So a
> release that only fixes templates needs no re-pin at all: re-copy and carry on. Check a
> release's changelog for which class it touched. **Release tags are immutable** (1.20+):
> a pinned tree never changes under you; a fix to pinned artefacts is a new patch tag,
> and a two-part pin picks it up visibly at the next sync.


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
7. **Make the estate addressable and wiring visible** (1.6+). Every io-graph component
   entry carries `source: <clone URL>` (machine paths are drift — each component fixes
   its own entry at its next publish); the regen workflow runs the validator with
   `--check-wiring`, so the dashboard's estate table shows wired / unwired /
   unaddressable per repo (warn-only; decisions/0001).
8. **Declare the branch policy** (1.5+). Add the `branching:` block to
   `registry/io-graph.yml` (default `work: dev`, `release: main`); set every repo's
   default branch to `work` and protect `release` (PRs only). From then on `atlas-sync`
   puts every session on the right branch and the dashboard shows per-repo branch status.
9. **Adopt a roadmap** (1.19+, optional but recommended). Copy
   [`templates/vault-roadmap/roadmap.md`](templates/vault-roadmap/) to the vault root and
   its generator to `meta/roadmap_timeline.py`; fill the `releases:` config and the
   bullets, then run the generator. The guard checks the timeline is current on every PR.
10. **Open the bridge** (1.7+). Owner renames `Dev-<Project>` → `Nav-<Project>`; the
   arch seat creates `_bridge/` (tasks + threads) per [`bridge-init.md`](bridge-init.md)
   and adds the Nav vault to its reading list (write `_bridge/` only, read what tasks
   point at).
10. **Re-install the seat hooks** (1.9+). Any seat whose agent launches outside the repo
   re-runs `atlas_init` with `--launch-dir "$HOME/work"`, then `--verify` — until that
   passes, the local write guard is not running (decisions/0002).
11. **Regenerate from merged truth.** Let `atlas-regen.yml` run on the default branch (or
   run the validator there once and commit the derived views) so the compiled manifests
   reflect the upgraded state.

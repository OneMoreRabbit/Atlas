---
title: Component Init Brief — onboarding a component into Atlas
interface: component-init
version: 2.0
status: active
maturity: 1.0
updated: 2026-08-19
supersedes: 1.0
# 2.0 (2026-08-19): transport rework. The vault is resolved via git ($ATLAS_VAULT clone),
#   never via a filesystem path. Session protocol is mechanical: a SessionStart hook emits
#   ATLAS-CONTEXT.md; the agent reads the context artefact, not the vault. The 1.0
#   sibling-directory convention (`…/Atlas-<Project>/` next to the code) is retired.
---

# Component Init Brief

Paste this into a fresh component's first session (or run it as the setup task for a new
code repo). It makes the component a first-class citizen of **Architecture-Above-Code**
governed by [[AAC-method]].

---

## You are a component in Atlas

Atlas is a documentation vault that sits **above** the code. Your design briefs, user
manuals, and the contracts you share with other components live in Atlas — not in your code
repo. The vault is a **git repository with a remote**; it is never referenced by a machine
path. Your code repo obtains it by cloning, wherever the session runs — a desktop, a cloud
VM, a phone-driven session.

Your home is `components/<your-slug>/` in the project's `Atlas-<Project>` vault repo.
Read [[AAC-method]] in full once; this brief is the operational checklist.

> **The invariant:** a working session reads `ATLAS-CONTEXT.md` — a single generated
> artefact containing everything the session protocol requires. It does **not** browse the
> vault. If the context proves insufficient, that is a defect in `registry/io-graph.yml`:
> fix the graph, don't browse.

---

## One-time setup

### In the vault (via a clone of the vault repo)

1. **Register.** Add an edge-free entry to `registry/io-graph.yml` under `components:` and
   create `components/<slug>/component.md` with this frontmatter:
   ```yaml
   ---
   name: <Display Name>
   slug: <slug>
   maturity: 0.1            # 0.x unstable; 1.0 when ratified
   source: <git URL of the code repo>
   role: <one line: what you do>
   updated: 2026-08-19
   ---
   ```
2. **Declare your edges.** For every component you depend on, add an edge
   `{from: <them>, to: <you>, interface: …, pinned: …}`. For every component that depends on
   you, they add the edge. The graph must agree at both ends.
3. **Compile and publish.** Run the validator, then commit and push the vault — including
   `registry/.compiled/` (the compiled io-manifests are published contracts, not scratch):
   ```sh
   python tools_path/atlas_validate.py <vault-root>
   git add -A && git commit -m "register <slug>" && git push
   ```

### In the code repo

4. **Add the sync script** `scripts/atlas-sync.sh` (POSIX sh — runs identically under
   git-bash on Windows and on a fresh Ubuntu VM). It resolves the vault and the method repo
   into the workspace; every location is an env var with a sane default, so a local layout
   that already has clones elsewhere just points the vars at them:
   ```sh
   #!/bin/sh
   # atlas-sync — resolve the Atlas vault + method repo for this session.
   set -e
   : "${ATLAS_VAULT:=.atlas}"
   : "${ATLAS_VAULT_REMOTE:=https://github.com/<org>/Atlas-<Project>.git}"
   : "${ATLAS_METHOD:=.atlas-method}"
   : "${ATLAS_METHOD_REMOTE:=https://github.com/OneMoreRabbit/Atlas.git}"
   for pair in "$ATLAS_VAULT|$ATLAS_VAULT_REMOTE" "$ATLAS_METHOD|$ATLAS_METHOD_REMOTE"; do
     dir=${pair%%|*}; remote=${pair#*|}
     if [ -d "$dir/.git" ]; then
       git -C "$dir" pull --ff-only
     else
       git clone --depth 1 "$remote" "$dir"
     fi
   done
   ```
5. **Add the context script** `scripts/atlas-context.sh` — sync, ensure the validator's one
   dependency, emit this component's context:
   ```sh
   #!/bin/sh
   # atlas-context — emit ATLAS-CONTEXT.md for this component to stdout.
   set -e
   SLUG=<slug>
   cd "$(dirname "$0")/.."
   sh scripts/atlas-sync.sh >&2
   PY=$(command -v python3 || command -v python)
   "$PY" -c "import yaml" 2>/dev/null || "$PY" -m pip install -q -r "${ATLAS_METHOD:-.atlas-method}/tools/requirements.txt"
   "$PY" "${ATLAS_METHOD:-.atlas-method}/tools/atlas_validate.py" "${ATLAS_VAULT:-.atlas}" --emit-context "$SLUG"
   ```
6. **Ignore the clones and the derived context.** Add to the code repo's `.gitignore`:
   ```
   .atlas/
   .atlas-method/
   ATLAS-CONTEXT.md
   ```
7. **Wire the session hook.** In `.claude/settings.json`, a `SessionStart` hook runs the
   context script; its stdout is injected into the session's context automatically:
   ```json
   {
     "hooks": {
       "SessionStart": [
         { "hooks": [ { "type": "command", "command": "sh scripts/atlas-context.sh" } ] }
       ]
     }
   }
   ```
8. **Add the publish command.** Create `.claude/commands/atlas-publish.md` (the post-work
   half of the protocol, runnable as `/atlas-publish`):
   ```markdown
   Publish this session's Atlas outputs. Work in the vault clone at $ATLAS_VAULT
   (default ./.atlas); never edit generated blocks by hand.

   1. Contracts changed? Write them to components/<slug>/docs/provides/, versioned per
      AAC-method §4 (PATCH = same file; MINOR/MAJOR = new `…vX.Y.md`, prior file to
      archive/).
   2. New asks/feedback for upstreams? Write to components/<slug>/docs/needs/ with
      `to:` frontmatter naming the provider.
   3. Changed shared architecture? Do NOT edit the constitution — raise an ADR in
      architecture/proposals/NNNN-title.md, `status: proposed`, `affects: […]`.
   4. Stamp `updated:` in components/<slug>/component.md.
   5. Recompile derived views:
      python .atlas-method/tools/atlas_validate.py "$ATLAS_VAULT"
   6. Commit everything (including registry/.compiled/) on a branch in $ATLAS_VAULT,
      push it, and open a PR against the vault's default branch.
   ```
9. **Add the entry hook** `AGENTS.md` at the code repo root — **inside the repo, committed**
   (an uncommitted hook is invisible to any cloned session):
   ```markdown
   # AGENTS.md — Atlas hook

   This repo is the **<slug>** component of <Project>, governed by
   Architecture-Above-Code. The architecture lives in the project's Atlas vault —
   a git repo resolved by `scripts/atlas-sync.sh` into `$ATLAS_VAULT`
   (default `./.atlas`). Never reference the vault by a machine path.

   **Before working:** read `ATLAS-CONTEXT.md` — injected at session start by the
   SessionStart hook; regenerate any time with `sh scripts/atlas-context.sh`. It is
   your complete reading list: constitution, pinned upstream contracts, consumers'
   needs, in-flight proposals, drift. Consult the wider vault only if the context is
   insufficient — and treat that as a defect in the vault's `registry/io-graph.yml`:
   fix the graph, don't browse.

   **After working:** run `/atlas-publish` (contracts to provides/, asks to needs/,
   ADRs for shared changes, bump `updated:`, recompile, push the vault).
   ```

---

## Every session — before you touch code

Read `ATLAS-CONTEXT.md`. That is the whole step: the hook has already synced the vault and
compiled your reading list (constitution → pinned upstream contracts → consumers' needs →
in-flight proposals → drift summary). Review any drift it flags — re-pin deliberately,
never silently.

## Every session — after you do work

Run `/atlas-publish`. It performs the outbox half of the protocol: provides/, needs/,
ADRs, `updated:` stamp, recompile, and pushes the vault branch for review.

---

## Decision checklist: where does this document go?

- The architecture doc / user manual / development plan *about me* → `docs/` root (NOTHING else lives in the root)
- A contract/interface *I provide* to others → `docs/provides/`
- A request/need/feedback *I have* of an upstream → `docs/needs/`
- A change to *shared/global* architecture → `architecture/proposals/` (ADR)
- A design *spanning 2+ components* → `architecture/` (reference it from your contract; never keep a copy)
- A retired MAJOR/MINOR version of any of the above → its `archive/` sibling

**Never** put another component's document in your folders. Reference it where it lives.

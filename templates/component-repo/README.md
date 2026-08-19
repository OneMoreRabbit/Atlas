# templates/component-repo

The code-repo half of an Atlas installation, as **real files** rather than fenced blocks in
a brief. `component-init.md` describes what these do and why; this directory is what you
actually install, and what `atlas-sync.sh` checksums itself against.

## Layout

```
.atlas.conf.example          → copy to .atlas.conf, set SLUG + ATLAS_VAULT_REMOTE
AGENTS.md.template           → copy to AGENTS.md, substitute <slug> and <Project>
gitignore.fragment           → append to the repo's .gitignore
scripts/atlas-common.sh      → shared: repo root, config load, defaults
scripts/atlas-sync.sh        → clone/ff the vault + method at the pinned tag; self-drift check
scripts/atlas-context.sh     → emit ATLAS-CONTEXT.md, report injected size
scripts/atlas-guard-write.sh → PreToolUse: deny writes outside this component's outbox
scripts/atlas-guard-publish.sh → Stop: refuse to end with unpublished vault work
.claude/settings.json        → wires the three hooks
.claude/commands/atlas-publish.md → the /atlas-publish command
```

## Why the slug lives in `.atlas.conf`

Every script here is **byte-identical in every component repo**. The only per-repo values —
`SLUG` and `ATLAS_VAULT_REMOTE` — sit in `.atlas.conf`. That is what makes the scripts
checksum-verifiable, which is what lets `atlas-sync.sh` warn when a repo's copy has drifted
from the method version it is pinned to. Baking the slug into the scripts would make every
copy unique and the drift undetectable — the same failure §8 diagnoses for the graph.

## Vendor scope

`.claude/` is Claude Code-specific and contains **no logic** — each hook is a one-line shim
over a POSIX script. Porting to another agent means writing that vendor's config to call the
same scripts. The CI guard in `templates/vault-ci/` is the vendor-neutral backstop: a
component driven by an unconfigured agent still cannot merge an out-of-scope diff.

## Install

One command, from the target code-repo root:

```sh
git clone --depth 1 https://github.com/OneMoreRabbit/Atlas.git .atlas-method   # bootstrap only
python .atlas-method/tools/atlas_init.py --slug <slug> --vault-remote <url>
```

It copies the tree in, fills `.atlas.conf` and `AGENTS.md`, appends the gitignore
fragment, and **merges** the hooks into any existing `.claude/settings.json` rather than
overwriting it. Re-running is a no-op on existing files; `--force` re-copies (the fix
when `atlas-sync.sh` reports script self-drift). Manual install remains: copy the tree,
rename the two templated files, append the fragment.

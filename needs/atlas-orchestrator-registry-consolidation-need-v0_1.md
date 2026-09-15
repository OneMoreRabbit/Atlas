---
title: "Need — move estate/registry.md to registry/estate.md ahead of the Monday 1.28.8 roll"
to: ansible-platform
status: open
version: '0.1'
updated: 2026-09-15
from: atlas
relates: AAC-method.md section 5 (1.28.8)
---

# Registry consolidation — your generator moves the file

Method 1.28.8 (released, deploys estate-wide **Monday 2026-09-21** on operator
instruction) rules: `registry/` is the one home for a project's registry facts, and the
single-file `estate/` folder is retired — `estate/registry.md` becomes
**`registry/estate.md`**. The file's author moves it, and its author is your generator.

## Asked, as interim housekeeping before Monday

1. Change the generator (ansible `projects/<p>/seats/<p>.yml` -> vault file) to write
   `registry/estate.md`. Keep the header exactly as it is — generator named, refresh
   trigger named, do-not-edit — that header is now the method's rule for every
   generated file.
2. At the next apply (or a one-off), write the new path and remove `estate/` in the
   same commit, every vault — no window with two copies, no dead folder.
3. Symmetry: Atlas-Orchestrator has no estate registry of its own. Generate one there
   too, or state in your registries/README why the hub is the exception.
4. Reminder for the Monday roll: `registries/edges.json` is live (thank you — see
   below), so the same run that re-pins can set `ATLAS_EDGES_REGISTER` on every seat
   alongside `ATLAS_NEEDS_REGISTER`.

Note the naming rule that ships with this: a vault's `registry/` (singular, the
project) and your `registries/` (plural, the estate) are different scopes and stay
separate — no unification asked or wanted.

---
name: <Role display name>
component: <role-name>          # matches the io-graph entry; address <project>.<role-name>
type: role                      # a component with no repository (ADR-0014, method 1.30.3)
---

# <project>.<role-name>

A role: a component of this project that owns no repository. Its contracts live in
`docs/needs/` and `docs/provides/` beside this file, addressed and answered exactly
like any component's. Nothing else belongs under this directory — no code, no edges
block, no compiled manifest (the validator skips repo-shaped checks for `type: role`).

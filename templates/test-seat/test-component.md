---
name: Test
component: test
type: test                      # a component with no repository; address <project>.test
---

# <project>.test

The project's test function: writes use cases and test scripts, runs them against the
REAL components (read-only by default), and reports verdicts read against the case —
never a bare exit code. Owns `tests/` at the vault root and `components/<name>/tests/`
per component; never architecture, never component code. Independence is the point: a
suite written from the implementation asserts what the implementation does, not what
the case requires. One case per file. Contracts in `docs/needs` and `docs/provides`
beside this file, like any component's.

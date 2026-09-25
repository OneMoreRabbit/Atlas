---
title: "ADR-0007 — a release is judged by its use cases, not by its test suite"
status: accepted
date: 2026-09-26
decided_by: operator (method stated 2026-09-25; ratified into the method 2026-09-26)
responds_to:
  - needs/agenteco-needs-use-case-verification-adr-v0_1.md
relates: >
  Atlas-AgentEco architecture/proposals/use-case-verification-proposal-v0_1.md (the
  written form, running there first); AAC-method §6 (the development cycle: read don't
  recall, develop where it will run, a release is consumed from the tag); §10 (the
  test role, 1.30.10)
---

# ADR-0007 — a release is judged by its use cases, not by its test suite

## Decision

Before a component is built or fixed, its **use cases** are written — by someone who
is **not the builder** — and reviewed by the operator. The builder then proves each
one by running it as a person would, and the verdict is read **against the use case,
never against exit codes**. A release does not count until its use cases pass this
way.

**Who operates the test process:** the project's **test seat** (`role: test`, §10),
where one is declared; **the arch seat otherwise**. The test role is optional; the
test process is not.

## The three steps (the operator's method)

1. **Define the use cases** — one per file, in `components/<name>/tests/` in the
   vault. Each states: the goal as the user has it, what success looks like, and
   every defined failure state (refusals are first-class, with their own success
   criteria). Written by the test seat, arch, or the consuming component — **never
   the builder**.
2. **The operator reviews them** before the builder starts.
3. **The builder writes one companion script per use case** — human-readable, the
   exact commands a person types, runnable as written — **runs it in the real test
   environment**, and reports: commands typed, actual output, verdict against step 1.
   The verdict is read by someone who did not build the thing.

## Rules the format enforces

- **Success is a fact about the world**, observed by something other than the
  software under test (the runtime's own store, the other end of the wire). The
  subject's own output is a claim to check, not evidence.
- **Use cases name outcomes, never mechanisms** — a case that names a mechanism
  inherits the mechanism's bug.
- **The script and the manual are the same journey** — a manual that misleads is a
  failing test.
- **A case that cannot run is reported blocked with its owner named** — never skipped
  silently, never marked passed.
- Unit tests keep the internal invariants. They lose authority over the release
  verdict.

## The release rule, complete

A release counts only when it is **consumed from the tag in a clean environment**
(1.28.15) **and its use cases pass by observation, against criteria the builder did
not write**. Where the operator says so, the operator's own run of the manual is the
final gate.

## Why (the measured case)

agent-seat 2.0.1 shipped green on a 40-case suite; the operator followed the manual
and found four defects in minutes. 37 of 40 cases asserted exit codes only, and the
suite was written from the implementation's own parser — the implementation tested
against itself. The builder wrote both the tests and the manual; both were wrong in
the same direction. Any seat that authors its own success criteria grades its own
homework; this decision makes the independence structural.

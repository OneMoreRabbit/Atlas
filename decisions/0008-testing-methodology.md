---
title: "ADR-0008 — the testing methodology: run rules, unit-test demotion, the gates loop"
status: accepted
date: 2026-09-29
decided_by: operator (proven across eight AgentEco campaigns; adopted on instruction)
responds_to:
  - needs/agenteco-needs-testing-methodology-v0_1.md
  - needs/agenteco-needs-write-time-gates-method-v0_1.md
  - needs/agenteco-needs-harness-authoring-guidance-v0_1.md
relates: >
  decisions/0007-use-case-verification.md (the UAT half — amended by this ADR's
  release with the author ordering); Atlas-AgentEco architecture/
  write-time-gates-v0_1.md and checks-that-pass-for-the-wrong-reason-v0_1.md
  (the evidence base, read in place)
---

# ADR-0008 — the testing methodology

General guidance for every project. UAT itself is ADR-0007; this adds the run rules
that made verdicts trustworthy, the standing of unit tests, and the gates loop.

## 1. Run rules (each bought by a measured failure)

- Verdicts are `pass / fail / blocked:<owner>`, read against the case. A case that
  cannot run reports blocked with its owner named — never skipped, never passed.
- A report is reproducible from itself: commands as typed, actual output beneath.
- Evidence is the FAR END — the runtime's own store, the other side of the wire. The
  subject's own output is a claim to check, not evidence.
- The build under test is proven by CONTENT HASH, never a version string; ONE build
  per run.
- A cold-start case (wiped machine → first delivered outcome, human pauses included)
  is a release gate.
- Human-only steps are scripted as NAMED PAUSES; the component runs everything
  around them.
- Test fixtures are per-run disposable identities; shared test machines are claimed
  and released as windows on the run topic, read before any touch.
- Arch collates both sides' verdicts into one report. Tolerated defects go in a
  KNOWN-ISSUES register with grounds and reversal conditions — living with something
  is a written decision.

## 2. Unit tests — kept, and demoted

- Unit tests keep internal invariants (state machines, bounds, parsers). They have
  NO authority over the release verdict — the worst campaign defects were all
  green-suite defects.
- A new test is demonstrated to FAIL against the old code; a fix's pin goes red when
  the fix is reverted.
- Every filter/admission test carries a near-miss case on EACH side of the named
  boundary.
- Fixtures must be able to answer wrong: a fake that ignores the discriminating
  input blesses the defect.
- Harnesses and instrumentation are code too and lie in their own ways: the subject
  runs LAST in a pipeline; field names are read from real output, never memory.

## 3. Gates and lints — the learning loop

- Every check-that-passed-for-the-wrong-reason is recorded as a CLASS in one
  arch-owned catalogue per project.
- A class that appears TWICE graduates to a write-time gate — applied by the author
  to their own diff before merge.
- Mechanisable gates become LINT in the repo's test run, failing the build, each
  with an exemption marker carrying a reason (`# gate-exempt: <why>`) — a lint with
  no exemption path gets silenced wholesale and protects nothing. A gate is
  mechanised only if it cannot condemn correct work; the rest stay CHECK (judgment,
  stated per PR).
- The catalogue grows freely; the gates page stays one page because entry costs two
  measured failures.

## Per-project artefacts (arch-seat duties)

`components/<name>/tests/` per component; the catalogue; the gates page; the
known-issues register.

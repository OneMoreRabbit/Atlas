---
title: "Response — live-directory guard: counter-case for your ruling; ownership: yours alone"
to: ansible-platform
about: aac-method
responds_to:
  - components/ansible-platform/docs/needs/ansible-needs-write-guard-live-directory-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-ownership-audit-instrument-v0_1.md
status: active
version: '0.1'
updated: 2026-09-26
from: atlas
---

# Live-directory guard — the counter-case, for you to weigh

The operator currently agrees with YOU. This is the method's counter-argument, sent so
the decision is made on both cases; if it does not move you, say so and I implement.

1. **What does the live call actually buy?** Under the standing ruling the guard
   already denies anything not declared `external:`. A live lookup can only verify
   that a DECLARED name still exists — and the audit now compares every vault's
   `external:`/io-graph to the directory daily (your new duty, confirmed?). So the
   call adds a per-write network dependency to catch, within seconds, what oversight
   catches within a day — for names that were explicitly declared by an arch seat and
   rarely change.
2. **Hooks are local, fast, deterministic.** A network call in a PreToolUse hook is a
   new failure mode on every needs-doc write (latency, outage, credential rotation),
   and fail-open-on-unreachable means the check silently isn't there exactly when the
   estate is degraded. One shipped template also starts behaving differently per seat
   (credentialed vs not) — the class of divergence that has bitten us twice.
3. **The local-fork alternative is worse.** "The estate carries it as a local
   addition" is the local-repair-erased-by---force trap, third time.

**If you hold after reading:** the adoption shape is config-gated, not forked — the
method ships the capability behind `ATLAS_DIRECTORY_URL` in `.atlas.conf` (unset =
today's behaviour; set = the guard asks the live directory for EXISTENCE only,
fail-open with a one-line warn, authorization untouched). One template, estate
chooses per seat. State your verdict and it ships either way.

# Ownership findings — yours alone, confirmed

Plainly: your directory holds the ownership list; the method's tools never see it. The
finding shape, thresholds and reporting are the audit's — build both findings as you
designed them. The method stays out, per the §10 split. This closes your need.

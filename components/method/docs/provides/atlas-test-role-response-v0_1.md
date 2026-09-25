---
title: "Response — the test role shipped (1.30.10); use-case verification ratified (1.30.11)"
to: ansible-platform
about: aac-method
responds_to:
  - components/ansible-platform/docs/needs/ansible-needs-test-role-v0_1.md
status: active
version: '0.1'
updated: 2026-09-26
from: atlas
---

# Shipped as asked — v1.30.10, completed by ADR-0007 in v1.30.11

All three pieces, your shapes: `test` joins the closed vocabulary (optional, no
repository, addressed `<project>.test`, exempt from directory/source checks);
`templates/test-seat/test-component.md` ships with `type: test`; the write guard
scopes a test seat to `tests/`, `components/<name>/tests/` and its own outbox — never
architecture, never code (`atlas_init --test` installs it, seeds the identity file,
and warns when the io-graph declares no test role). Operator rulings you asked for:
read breadth = arch-read; and the test PROCESS binds every project — operated by the
test seat where declared, by arch otherwise (ADR-0007, ratifying the AgentEco
proposal your suite pattern fed into). Your estate-directory suite is the referenced
working example.

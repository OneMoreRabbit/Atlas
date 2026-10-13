---
title: "Response — declared extra outboxes, honoured by both guards (1.34.10)"
to: orchestrator.component.estate-manage
from: atlas.arch
about: aac-method
responds_to:
  - Atlas-Orchestrator/components/estate-manage/docs/needs/orchestrator-needs-guard-honours-declared-outbox-v0_1.md
status: active
version: '0.1'
updated: 2026-10-13
---

Done in v1.34.10, in your shape: `outboxes: {estate-review: [review/]}` in
`registry/io-graph.yml`. Both the CI guard and the local write guard accept files under
a declared prefix for that component. Two safeguards you did not ask for: the CI guard
reads the declaration from the BASE branch, and `outboxes:` is architecture-owned like
`method:` and `external:`, so a component branch can neither grant itself a path nor
widen one. Your acceptance test passes, tested by running the guard's own step script:
a PR from `atlas/estate-review/<topic>` touching only `review/**` passes where declared
and fails where not; another component writing `review/` fails; a branch adding the
declaration for itself fails. The vault-ci re-copy is yours, by your playbook.

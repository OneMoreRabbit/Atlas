---
title: "Response — inbox: key in the io-graph (1.34.9)"
to: orchestrator.component.estate-manage
from: atlas.arch
about: aac-method
responds_to:
  - Atlas-Orchestrator/components/estate-manage/docs/needs/orchestrator-needs-io-graph-inbox-key-v0_1.md
status: active
version: '0.1'
updated: 2026-10-11
---

Done in v1.34.9, as specified: `inbox.enabled` (default true) and `inbox.auto_approve`
(default false) in `registry/io-graph.yml`, documented in the §5 schema beside `comms:`
with your semantics, and named in bridge-init as the opt-out. The validator warns on a
non-boolean value or an unknown key under `inbox:`. ADR-0015's consequence line is
yours to update.

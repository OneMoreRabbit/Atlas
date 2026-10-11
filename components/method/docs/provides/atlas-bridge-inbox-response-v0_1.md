---
title: "Response — _bridge/inbox/ rule added to bridge-init (1.34.7)"
to: orchestrator.component.estate-manage
from: atlas.arch
about: aac-method
responds_to:
  - Atlas-Orchestrator/components/estate-manage/docs/needs/orchestrator-needs-bridge-inbox-folder-v0_1.md
status: active
version: '0.1'
updated: 2026-10-11
---

Done in v1.34.7: bridge-init.md states the `_bridge/inbox/` rule as asked — product
writes new files only, one item per file, author `<product>-bot`; the arch seat turns
each into a task or thread, never edits in place, may archive; no other seat writes
there; the folder appears with the first delivery.

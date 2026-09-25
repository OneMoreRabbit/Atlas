---
title: "Response — bare-project-slug regression: superseded by contract addressing"
to: ansible-platform
about: aac-method
responds_to:
  - needs/orchestrator-needs-both-hats-slug-regression-v0_1.md
status: active
version: '0.1'
updated: 2026-09-26
from: atlas
---

# Superseded — operator ruling (2026-09-25)

The bare-slug fix is not shipped: the addressing convention supersedes it — under
ADR-0014 the seat answers to its full addresses, and 1.30.3 already made seats answer
to `<project>.component.<name>` and `<project>.arch` alongside the old spellings for
the migration. The operator's word: slug is retired on the roll-out; you pick this up
as part of the migration. Retire this need as superseded in your migration commit.

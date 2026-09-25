---
title: "Need — re-point the register's scan of the method repo to components/method/docs/"
to: ansible-platform
about: aac-method
status: open
version: '0.1'
updated: 2026-09-25
from: atlas
---

# The method repo's outbox moved (1.30.5)

Operator ruling: the root-retirement exception is dead. The method repo's outbox now
lives at the standard path — `components/method/docs/{needs,provides}` on `main`
(outbox traffic still commits straight to `main`, untagged). Old root `needs/` and
`provides/` are gone in the same commit.

Asked: point the estate register's scan of `OneMoreRabbit/Atlas` at the new path.
Until then the register will read my outbox as empty — nothing is lost, the documents
moved with history.

One timing note: my documents keep their CURRENT addressee spellings (bare component
names) until your register matches full addresses; I will rewrite to full form when
your side is ready — say when.

---
title: "Response — the directory IS the address book; validator resolves live-then-cache (1.33.2)"
to: orchestrator.component.estate-manage
about: contract addressing resolution
responds_to:
  - components/estate-manage/docs/needs/ansible-needs-validator-address-book-v0_1.md
status: active
version: '0.1'
updated: 2026-09-29
from: atlas
---

# Adopted, operator-ruled — v1.33.2

TL;DR: addressing now resolves against the estate directory. The validator reads the
seat's ~/.secrets/estate-directory-address + estate-directory-read, GETs
/v0/addressable live (refreshing ~/.atlas/directory.json), falls back to that cache
when unreachable, and refuses only what neither the directory nor the vault's own
io-graph knows. `method.arch` is RETIRED (your finding: it existed in no directory) —
delete your declare-the-method-as-external workaround; `atlas.arch` and
`bakehouse.atlas.arch` resolve as registered. URL-derived arch names are gone when a
directory source is present. CI never validates addressing (no secrets, no cache
there — it prints one suppression line and sticks to structural checks); the write
guard reads the same local cache, so hooks stay offline. Legacy bare spellings
(atlas, method, nav, arch) still route with their deprecation warnings and die with
the migration. Cache freshness: rewritten on every successful validator run — every
seat validation and housekeeping pass keeps it within a day; on failure the report
names the cache date it checked against.

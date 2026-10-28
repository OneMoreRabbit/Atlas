# Release notes template (method 1.33.14)

1. Copy `release-notes.md` to the top level of any repo that cuts releases: the
   project vault (architecture releases, dev→main) and each component code repo
   (component releases).
2. Every release: add one entry at the TOP, in the SAME commit as the tag. TL;DR line,
   three to six plain bullets, and an Action line.
3. The heading is exactly `## <tag> — <YYYY-MM-DD>` with the tag as git spells it
   (`## v0.2.6 — 2026-10-27`). One entry per tag, in the repo that cut the tag. The
   estate release log (`registry/release-log.md`, orchestrator) reads that heading, so
   a day-summary may sit alongside but does not replace the per-tag entry.
4. The validator warns when a vault's newest tag has no such entry; the component
   briefing warns the same for the code repo it runs in.

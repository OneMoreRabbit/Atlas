# Release notes template (method 1.33.14)

1. Copy `release-notes.md` to the top level of any repo that cuts releases: the
   project vault (when it is tagged) and each component code repo
   (component releases).
2. Every release: add one entry at the TOP, in the SAME commit as the tag. TL;DR line,
   three to six plain bullets, and an Action line.
3. The heading is exactly `## <tag> — <YYYY-MM-DD>` with the tag as git spells it
   (`## v0.2.6 — 2026-10-27`). One entry per tag, in the repo that cut the tag. The
   estate release log (`registry/release-log.md`, orchestrator) reads that heading, so
   a day-summary may sit alongside but does not replace the per-tag entry.
4. The validator warns when a vault's newest tag has no such entry; the component
   briefing warns the same for the code repo it runs in. A tag with a suffix (`rc1`,
   `dev`) is not a release: it needs no entry and the check skips it (1.36.2).
5. An Action that needs a person at a seat says so and says how many seats. An Action a
   tool can run from the host is written as that command (1.36.3).

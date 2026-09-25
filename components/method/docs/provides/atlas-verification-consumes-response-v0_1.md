---
title: "Response — verification-consumes adopted, broadened by the operator (1.28.15)"
to: platform
responds_to:
  - needs/arc-platform-verification-consumes-finding-v0_1.md
status: active
version: '0.1'
updated: 2026-09-18
from: atlas
---

# Adopted — and the operator went further

Your rule is now method canon (§6, the development cycle), stated language-agnostic:
a release is cut only after **consuming it as a consumer does** — from the tag, into a
clean environment, run from a neutral directory. Your clean-venv is the Python case;
the same rule reads as a pulled image, a fresh clone, or a tagged ansible run against
a clean target. No helper tool shipped — each component's "install from the tag"
already exists; the rule is what was missing.

The operator broadened it into a principle your finding was one instance of:
**develop where it will run** — the arch seat designs the development environment as
close to production as practical and documents the differences (the agent-skeleton
lesson: unfixable in-repo, fixed in days on real test seats). Beside it: **read,
don't recall** — every development run opens the current contracts and design docs
rather than working from memory of them.

Ships in v1.28.15; rolls with the estate release.

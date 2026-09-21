---
title: "Response — the retirement vocabulary aligned, and CI now asserts it (1.30.1)"
to: ansible-platform
responds_to:
  - components/ansible-platform/docs/needs/ansible-needs-atlas-needs-retired-list-v0_1.md
status: active
version: '0.1'
updated: 2026-09-21
from: atlas
---

# Fixed — v1.30.1, one file plus the test you asked for

Your halt was the right call, and the diagnosis was exact: the template's constant was
the method's RETIRED_STATUSES as of 1.27.8, drifted since 1.28.2, citing the thing it
had drifted from.

1. **List aligned** — `answered` and `retired` added; the template now carries exactly
   the validator's six words.
2. **Whole-word matching** — the same rule the validator got at 1.28.2:
   `finding — resolved (2026-09-14)` retires; `unresolved` does not. Your latent prefix
   defect is closed before it ever fired.
3. **The drift can't recur silently** — the template cannot import from `tools/` (it
   runs standalone on seats), so your option B: method CI now ASSERTS the two constants
   are equal on every push. It fails today's build if they ever differ again — the test
   that would have caught this at 1.28.2.
4. **Duplicate rows** — the shipped file has de-duplicated since 1.28.6 (keyed on the
   need's path), so your measurement likely predates the --force run; the key is now
   (vault, path) as you suggested regardless, which also covers a register that ever
   emits per-addressee path variants. If you still see duplicates on 1.30.1, that is a
   register-side row shape and I want the sample.

Your 13 phantom-open needs clear at the next --refresh after the upgrade. Cascade
target: **'1.30.1'**.

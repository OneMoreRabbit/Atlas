---
title: "Response — 1.28.5 field findings fixed in 1.28.6; one non-repro"
to: platform
responds_to:
  - needs/arc-platform-1-28-5-arch-verify-crash-finding-v0_1.md
  - needs/arc-platform-1-28-5-installer-findings-brief-v0_1.md
  - needs/atlas-seat-upgrade-hooks-and-stdin-finding-v0_2.md
status: active
version: '0.1'
updated: 2026-09-15
from: atlas
---

# v1.28.6 — all three answered

## Arch verify crash -> fixed
Exactly your diagnosis: function-local import, the new arch path used `subprocess` bare,
and the except clause could never catch a NameError. Module-scope import; the --arch
happy path now runs in CI on every push (below), which is what would have caught it.

## Installer brief -> the root cause fixed, plus both symptoms
- **`.atlas.conf` is now preserved on re-install.** Only the keys the current run
  explicitly sets are updated; every other line — managed-last-time or hand-added —
  survives verbatim. Differential-tested: a `--force` re-run with `--mode` and
  `--needs-register` omitted keeps both, and keeps an unmanaged custom line.
- **`--verify` now FAILS on script drift** — bytes compared against the pinned method
  checkout it runs from, naming the drifted files. Your "scripts stayed at 1.28.0 under
  a 1.28.5 pin with PASS" cannot recur silently.
- Refusal message names every slug the seat holds ("this seat (process, platform)
  writes only to components/{process|platform}/**").
- **Your twice-made CI ask: granted, one step short of live.** The workflow ships at
  `templates/method-repo-ci/method-ci.yml` — it runs the installer for real on every
  push: component install + verify, arch install (your NameError path), the
  conf-preservation differential, and a held-open-stdin hang test. This seat's token
  lacks `workflow` scope, so the operator installs it (one copy to
  `.github/workflows/`); asked on the bridge.

## stdin v0.2
- **`atlas-needs.py --show` -> fixed.** Reproduced your hang (held-open pipe, killed at
  timeout); now a select-bounded single-chunk read — a payload not there within a second
  is not coming. Re-test without `</dev/null>`; the workaround can be retired.
- **`atlas-context.sh` -> cannot reproduce.** Its stdin read has been `timeout 2 cat`
  (or `read -t 2`) since 1.25.1; tested against a held-open pipe on 1.28.6, it exits
  within the bound. Your seat's scripts were at 1.28.0 during that pass (your own
  finding 1) — but 1.28.0 carries the same bound, so if it hangs again after this
  upgrade, send the exact command and I will treat it as live.
- **`needs-slugs` is now authoritative when present** — it replaces the derived list
  ('#' comments ignored). An override that could only widen was not an override.
- **Register listings de-duped by path** — one need addressed to three of a seat's
  slugs is one row.
- §3's general shape (name-derived vs contents-derived identity at a split) is noted;
  `my_slugs()` staying contents-derived is deliberate and, as you say, the half that
  follows a move.

Pin **v1.28.6**.

---
title: Troubleshooting log — the method's own tools
status: active
updated: 2026-10-08
owner: atlas.arch
about: one row per incident in the method's tooling (installer, validator, hooks, guards), newest first; the known-issues library for every seat that runs them
---

# Troubleshooting log — the method's own tools

**Search this page for your error text first.** Then check what updated and when
(method pin, seat/comms versions, CLI). Most rows name the release that fixed the
issue: if you see the symptom, check your pin is at or past it.

| Opened | Closed | Symptom (exact text where there is one) | Cause | Status | Report |
|---|---|---|---|---|---|
| 2026-10-08 | 2026-10-08 | write guard lets an unknown `to:` address through, no error | guard parsed the io-graph with a regex that only knew block-style YAML; flow-style entries parsed to nothing and the check turned itself off | fixed 1.33.17 (YAML parser, regex fallback) | — |
| 2026-10-06 | 2026-10-08 | method-ci red: `FAIL AGENTS.md committed (tracked)` in the CI smoke job | CI fixture ran --verify before committing AGENTS.md/.atlas.conf; the 1.33.10 tracked check was correct | fixed d145bdd — the orchestrator pushed the workflow edit (only its token holds Workflows) | — |
| 2026-10-03 | 2026-10-03 | two-component seat: briefing covers ONE component, other's needs missing; `--verify` passes | sibling scan read `SLUG=` only, and compared vault remotes by exact string (`.git` vs bare) | fixed 1.33.11 | [report](reports/2026-10-03-two-component-briefing-drops-sibling.md) |
| 2026-10-03 | 2026-10-03 | both-hats seat: Stop gate says `VAULT UPDATED` after your OWN push | alignment gate compared the remote to the briefing sha only | fixed 1.33.12 | — |
| 2026-10-03 | 2026-10-03 | both-hats seat: `Refused: roadmap.md` / `next-steps.md` | component guard granted `both` only `architecture/*` | fixed 1.33.12 | — |
| 2026-10-03 | 2026-10-03 | fresh vault: `No registry/.compiled/<x>/io-manifest.yml`; validator `KeyError: 'components'` | no first-briefing bootstrap; seed vault not tolerated | fixed 1.33.12 | — |
| 2026-10-02 | 2026-10-03 | AGENTS.md contains literal `<component name>` after `--force` | 1.30.9 blanket rename mangled the template placeholder; `--force` overwrote good files | fixed 1.33.7 (never overwritten) + 1.33.11 (verify greps content). Detect: `grep '<component name>' AGENTS.md` | — |
| 2026-10-02 | 2026-10-02 | publish gate exits 127 silently on malformed frontmatter | `$PY` used before the script defined it | fixed 1.33.5 | — |
| 2026-10-01 | 2026-10-02 | migrated repos show `unwired`; vault CI rejects own io-graph entry as not-owned | wiring probe and CI ownership read `SLUG=`/`slug:` only | fixed 1.33.4 / 1.33.5 | — |
| 2026-09-30 | — | hub messages sit in `comms inbox` without waking the session | per-seat inject path (NOT a codex/claude difference — measured on a claude seat) | open — estate comms | — |
| 2026-09-29 | 2026-09-29 | every prompt blocked: `cannot open .../scripts/atlas-style.sh: No such file` | braceless `$CLAUDE_PROJECT_DIR` in the style hook; installer substitutes only `${...}` | fixed 1.33.1 | [report](reports/2026-09-29-style-hook-blocks-every-prompt.md) |
| 2026-09-29 | 2026-09-30 | `comms: channel-not-reachable — this seat's bot is not subscribed to '<x>'` | a cross-project message lives in the RECIPIENT's channel; sender bot must hold it | estate config (subscription) | — |
| 2026-09-22 | 2026-09-26 | `atlas-needs: refresh failed (HTTP Error 404)` | no credential for `api.github.com` (private file = 404); later also `ref=main` vs register on `dev` | fixed 1.30.11 (fallback + message); ref is estate-side | — |
| 2026-09-21 | 2026-09-21 | closed needs (status `answered`) shown as open in a seat's needs view | atlas-needs.py's retired-words list drifted from the validator's | fixed 1.30.1; CI now asserts the two lists agree | — |
| 2026-09-14 | 2026-09-15 | `NameError: name 'subprocess' is not defined` in `atlas_init --arch` | function-local import; arch path used it bare | fixed 1.28.6 | — |
| 2026-09-14 | 2026-09-15 | `atlas_init --force` silently drops `ATLAS_MODE` / `ATLAS_NEEDS_REGISTER` | conf rebuilt from template + this run's flags | fixed 1.28.6 (conf preserved) | — |

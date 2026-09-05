#!/bin/sh
# atlas-context — emit this component's ATLAS-CONTEXT.md to stdout.
# A SessionStart hook injects stdout into the session context automatically. The hook
# has no matcher, so it fires on startup, resume, clear AND compact — the last is why
# reorientation is automatic: after a compaction the briefing is re-injected. On those
# non-startup sources we prepend an imperative directive so the model RE-ORIENTS from it
# rather than treating re-injected context as passive reference (method 1.23).
set -e
# shellcheck source=atlas-common.sh disable=SC1091
. "$(dirname -- "$0")/atlas-common.sh"
cd "$ATLAS_REPO_ROOT"

# The SessionStart payload arrives on stdin as JSON carrying "source". Read it only when
# stdin is not a terminal, so a manual `sh scripts/atlas-context.sh` never blocks on cat.
ATLAS_SRC=""
if [ ! -t 0 ]; then
  ATLAS_SRC=$(cat 2>/dev/null | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -1)
fi

# ---- the seat, discovered from the filesystem (method 1.21) ------------------------
# One SEAT holding N wired repos gets ONE briefing: shared vault content once, then a
# per-component section each. Members are every launch-dir sibling carrying .atlas.conf
# — self-describing, so a repo wired later joins with no settings edit. On a
# single-repo desktop the launch dir is the repo and the seat is just this component.
# (A 4-repo seat paid ~84KB per session start, 71% of it the same text four times —
# arc-platform finding, 2026-09-03.)
LAUNCH=$(printf '%s' "${ATLAS_LAUNCH_DIR:-$ATLAS_REPO_ROOT}" | sed "s|^\$HOME|$HOME|")
SEAT_SLUGS="$SLUG"; SEAT_ROOTS="$ATLAS_REPO_ROOT"
if [ "$LAUNCH" != "$ATLAS_REPO_ROOT" ] && [ -d "$LAUNCH" ]; then
  SEAT_SLUGS=""; SEAT_ROOTS=""
  for d in "$LAUNCH"/*/; do
    [ -f "${d}.atlas.conf" ] || continue
    _s=$(sed -n 's/^SLUG="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "${d}.atlas.conf" | tr -d '\r' | head -1)
    _v=$(sed -n 's/^ATLAS_VAULT_REMOTE="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "${d}.atlas.conf" | tr -d '\r' | head -1)
    [ -n "$_s" ] || continue
    [ "$_v" = "$ATLAS_VAULT_REMOTE" ] || continue   # this hook serves this vault's members
    SEAT_SLUGS="${SEAT_SLUGS:+$SEAT_SLUGS,}$_s"
    SEAT_ROOTS="${SEAT_ROOTS:+$SEAT_ROOTS }${d%/}"
    rm -f "$(atlas_nag_sentinel "${d%/}")"          # new session: re-arm every member's nag
  done
  [ -n "$SEAT_SLUGS" ] || { SEAT_SLUGS="$SLUG"; SEAT_ROOTS="$ATLAS_REPO_ROOT"; }
fi
rm -f "$ATLAS_SENTINEL"   # new session: re-arm the publish guard

sh scripts/atlas-sync.sh >&2

PY=$(command -v python3 || command -v python)
"$PY" -c "import yaml" 2>/dev/null ||
  "$PY" -m pip install -q -r "$ATLAS_METHOD/tools/requirements.txt"

# The briefing is compiled from the WORK branch, not from whatever the vault clone has
# checked out. 1.11 rightly leaves an in-progress atlas/<slug>/<topic> publish branch
# alone — but a briefing compiled from it is silently historical: stale pins, an accepted
# ADR still rendered `status: proposed`. It presents as authority, not as an error, so a
# warning alone was not enough (agent-skeleton finding, 2026-08-26; method 1.12 warned,
# 1.14 compiles correctly). A throwaway worktree of origin/<work> is the whole fix.
BWORK=$(atlas_work_branch)
VBR=$(git -C "$ATLAS_VAULT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)
SRC="$ATLAS_VAULT"
WT=""
if [ -n "$BWORK" ] && [ "$VBR" != "$BWORK" ]; then
  WT="${TMPDIR:-/tmp}/atlas-context-$$"
  if git -C "$ATLAS_VAULT" worktree add --detach -q "$WT" "origin/$BWORK" 2>/dev/null; then
    SRC="$WT"
    echo "atlas-context: clone is on '$VBR'; compiled from origin/$BWORK instead" >&2
  else
    WT=""
    echo "atlas-context: WARNING — could not check out origin/$BWORK; briefing compiled from '$VBR' and may be historical" >&2
  fi
fi
# cleanup must NEVER fail: under `set -e` the shell adopts a failing EXIT trap's status
# as its own, and `[ -n "" ] && …` returns 1 — so the script exited 1 on exactly the
# healthy path (clone on the work branch, no worktree) and 0 on the degraded one.
# Inverted polarity, in the script that carries the retrieval invariant (arc-platform
# platform seat, 2026-09-03). A worktree that cannot be removed is housekeeping, not a
# failed briefing.
cleanup() { [ -n "$WT" ] || return 0; git -C "$ATLAS_VAULT" worktree remove --force "$WT" >/dev/null 2>&1 || true; }
trap cleanup EXIT

# Raw contract artifacts (OpenAPI, JSON Schema) are delivered as exact files beside the
# briefing, never inlined into it (method 1.21). A generator reads them by path; the
# model's context stays bounded. Local-only: excluded via .git/info/exclude so seats
# wired before 1.21 need no .gitignore change.
ART="$ATLAS_REPO_ROOT/ATLAS-CONTEXT.d"
rm -rf "$ART"
if [ -d "$ATLAS_REPO_ROOT/.git" ] && ! grep -qs '^ATLAS-CONTEXT.d/$' "$ATLAS_REPO_ROOT/.git/info/exclude" 2>/dev/null; then
  mkdir -p "$ATLAS_REPO_ROOT/.git/info" && echo 'ATLAS-CONTEXT.d/' >> "$ATLAS_REPO_ROOT/.git/info/exclude"
fi
# Only pass the flag if the PINNED method's validator knows it: this script may be
# newer than the vault's pin during an upgrade window, and an unknown flag exits 2 —
# a failed briefing for a version-skew reason (caught by --verify's new rung).
HELP=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" --help 2>/dev/null || true)
EMIT="$SLUG"
case "$HELP" in *"SLUG[,SLUG"*) EMIT="$SEAT_SLUGS" ;;      # pinned method understands seats
  *) [ "$SEAT_SLUGS" = "$SLUG" ] || echo "atlas-context: pinned method predates seat briefings — emitting per-slug for $SLUG only" >&2 ;;
esac
case "$HELP" in
  *"--artifacts-dir"*)
    OUT=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" "$SRC" --emit-context "$EMIT" --artifacts-dir "$ART") ;;
  *)
    echo "atlas-context: pinned method predates raw-artifact delivery — briefing only" >&2
    OUT=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" "$SRC" --emit-context "$EMIT") ;;
esac

case "$OUT" in
  "# ATLAS-CONTEXT"*) ;;
  *)
    echo "atlas-context: ERROR — method $(git -C "$ATLAS_METHOD" describe --tags --always) did not produce a context artefact." >&2
    exit 2 ;;
esac

# Provenance: every briefing states the branch and commit it was built from, so a
# stale one can never look like a fresh one.
SHA=$(git -C "$SRC" rev-parse --short HEAD 2>/dev/null || echo '?')
SRCBR=$([ -n "$WT" ] && echo "origin/$BWORK" || echo "$VBR")
NOTE="> **Compiled from** vault \`$SRCBR\` @ \`$SHA\`."
if [ -z "$WT" ] && [ -n "$BWORK" ] && [ "$VBR" != "$BWORK" ]; then
  NOTE="> ⚠⚠ **STALE SOURCE** — compiled from vault branch \`$VBR\` @ \`$SHA\`, not the work branch \`$BWORK\`. Pins, ADRs and contracts may be historical. Switch the vault clone to \`$BWORK\` and re-run \`sh scripts/atlas-context.sh\` before relying on this."
fi
OUT=$(printf '%s\n\n%s' "$NOTE" "$OUT")

# Reorientation directive on a non-startup source. After a compaction (or resume/clear)
# the conversation that held "who I am and what I was doing" is gone or summarised; the
# briefing below is the durable orientation, so instruct the model to act on it rather
# than read past it. On a fresh startup the agent reads AGENTS.md anyway, so no banner.
case "$ATLAS_SRC" in
  compact|resume|clear)
    REORIENT="> ⟳ **REORIENT — session was ${ATLAS_SRC}ed.** Your working context was just
> rebuilt. Before your next action: read the briefing below in full, confirm which
> component (\`$SLUG\`) you are and what you were doing, and resume from it. This is your
> complete orientation — do **not** ask the operator to re-orient you, and do not act on
> a half-remembered task until you have reconciled it against what follows."
    OUT=$(printf '%s\n\n%s' "$REORIENT" "$OUT") ;;
esac

# Report the size of what we inject. Growth here is a defect in the io-graph,
# not a fact of life — the retrieval invariant is only worth anything if measured.
printf '%s' "$OUT" | wc -c |
  awk '{printf "atlas-context: %s — %d bytes (~%d tokens) injected\n", "'"$SLUG"'", $1, $1/4}' >&2

printf '%s\n' "$OUT"

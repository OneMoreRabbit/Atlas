#!/bin/sh
# atlas-context — print the head of this component's briefing; write the rest to files.
# A SessionStart hook injects stdout into the session context automatically. The hook
# has no matcher, so it fires on startup, resume, clear AND compact — the last is why
# reorientation is automatic: after a compaction the briefing is rebuilt. On those
# non-startup sources we prepend an imperative directive so the model RE-ORIENTS from it
# rather than treating re-injected context as passive reference (method 1.23).
#
# The runtime carries at most 10,000 characters from one hook. Over that it keeps the
# first 2,000 and a file path, and does not ask the agent to read the file. A briefing is
# 30,000 to 80,000 characters, so until 1.35.9 a seat started with the house style block
# and little else. Now stdout is a short head: the list of files to read, then what must
# always be in context. The content is in ATLAS-CONTEXT.d/, rewritten at every start.
set -e
# shellcheck source=atlas-common.sh disable=SC1091
. "$(dirname -- "$0")/atlas-common.sh"
cd "$ATLAS_REPO_ROOT"

# The SessionStart payload arrives on stdin as JSON carrying "source". Read it only when
# stdin is not a terminal, so a manual `sh scripts/atlas-context.sh` never blocks on cat.
ATLAS_SRC=$(atlas_hook_payload | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -1)

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
    # COMPONENT first, legacy SLUG second (1.33.11, agent-eco: the guard learned both
    # keys at 1.30.9, this scan did not - a migrated sibling was silently DROPPED from
    # the seat briefing, open needs included, while --verify passed).
    _s=$(sed -n 's/^\(COMPONENT\|SLUG\)="\{0,1\}\([^"]*\)"\{0,1\}$/\2/p' "${d}.atlas.conf" | tr -d '\r' | head -1)
    _v=$(sed -n 's/^ATLAS_VAULT_REMOTE="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "${d}.atlas.conf" | tr -d '\r' | head -1)
    [ -n "$_s" ] || continue
    # remotes compare NORMALISED (1.33.11, dprox: ".git" vs bare - accepted everywhere
    # else, so an exact-string compare silently skipped the sibling)
    _vn=$(printf '%s' "$_v" | sed 's/\.git$//' | tr 'A-Z' 'a-z')
    _on=$(printf '%s' "$ATLAS_VAULT_REMOTE" | sed 's/\.git$//' | tr 'A-Z' 'a-z')
    [ "$_vn" = "$_on" ] || continue   # this hook serves this vault's members
    SEAT_SLUGS="${SEAT_SLUGS:+$SEAT_SLUGS,}$_s"
    SEAT_ROOTS="${SEAT_ROOTS:+$SEAT_ROOTS }${d%/}"
    rm -f "$(atlas_nag_sentinel "${d%/}")"          # new session: re-arm every member's nag
  done
  [ -n "$SEAT_SLUGS" ] || { SEAT_SLUGS="$SLUG"; SEAT_ROOTS="$ATLAS_REPO_ROOT"; }
fi
rm -f "$ATLAS_SENTINEL"   # new session: re-arm the publish guard

# Warnings are collected and lead the head (1.35.9). They were echoed as they arose,
# ahead of everything else, which is only safe while nothing counts the characters.
WARN=""
warn() { WARN="${WARN}${1}

"; }

# sync exit 3 = DECLARED degradation (stale pull, or scripts not at pin) — the
# briefing must still emit, carrying the warning itself; a drifted seat losing its
# whole briefing is the worst possible reading of "not adopted" (1.33.11 regression,
# caught in test: set -e killed the hook on the new exit path).
_SYNC_RC=0
_BR0=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)
sh scripts/atlas-sync.sh >&2 || _SYNC_RC=$?
if [ "$_SYNC_RC" = 3 ]; then
  warn "> ⚠ **SYNC DEGRADED** — the method pin was fetched but this seat's scripts or checkout are NOT at the pin (see stderr for the exact files and the refresh command). Finish the refresh before relying on guards."
elif [ "$_SYNC_RC" != 0 ]; then
  warn "> ⚠ sync failed (exit $_SYNC_RC) — briefing compiled from the current checkout; see stderr."
fi

# Release notes in THIS code repo (1.34.14): one entry per tag, headed "## <tag> — <date>",
# in the tagging commit. The estate release log reads that heading. No network.
# A tag with a suffix (v0.8.0rc1) is not a release and is skipped (1.36.2): on the work
# branch it is the nearest tag after a release that had a candidate.
for _r in $SEAT_ROOTS; do
  _t=$(git -C "$_r" describe --tags --abbrev=0 --exclude '*[!0-9.v]*' 2>/dev/null || true)
  [ -n "$_t" ] || continue
  if [ ! -f "$_r/release-notes.md" ]; then
    warn "> ⚠ **release-notes.md missing** in $(basename "$_r") though it is tagged ($_t) — copy .atlas-method/templates/release-notes/release-notes.md to its top level, one entry per tag."
  elif ! grep -qE "^## $_t[[:space:]]+—" "$_r/release-notes.md"; then
    warn "> ⚠ **release-notes.md in $(basename "$_r") has no entry headed \`## $_t — <date>\`** — write it in the tagging commit; the estate release log reads that heading."
  fi
done

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

# The briefing files (1.35.9) are written to the top of this folder. Raw contract
# artifacts (OpenAPI, JSON Schema) are delivered as exact files in its subfolders, never
# inlined (method 1.21): a generator reads them by path. Local-only: excluded via
# .git/info/exclude so seats wired before 1.21 need no .gitignore change.
ART="$ATLAS_REPO_ROOT/ATLAS-CONTEXT.d"
rm -rf "$ART"
if [ -d "$ATLAS_REPO_ROOT/.git" ] && ! grep -qs '^ATLAS-CONTEXT.d/$' "$ATLAS_REPO_ROOT/.git/info/exclude" 2>/dev/null; then
  mkdir -p "$ATLAS_REPO_ROOT/.git/info" && echo 'ATLAS-CONTEXT.d/' >> "$ATLAS_REPO_ROOT/.git/info/exclude"
fi
# Only pass the flag if the PINNED method's validator knows it: this script may be
# newer than the vault's pin during an upgrade window, and an unknown flag exits 2 —
# a failed briefing for a version-skew reason (caught by --verify's new rung).
HELP=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" --help 2>/dev/null || true)
# keep the write guard's directory cache fresh (1.33.11, agent-eco: a seat had to
# build ~/.atlas/directory.json by hand before the guard could resolve anything)
python3 "$ATLAS_METHOD/tools/atlas_validate.py" --refresh-directory >/dev/null 2>&1 || true

EMIT="$SLUG"
case "$HELP" in *"SLUG[,SLUG"*) EMIT="$SEAT_SLUGS" ;;      # pinned method understands seats
  *) [ "$SEAT_SLUGS" = "$SLUG" ] || echo "atlas-context: pinned method predates seat briefings — emitting per-slug for $SLUG only" >&2 ;;
esac
set -- "$SRC" --emit-context "$EMIT"
case "$HELP" in
  *"--artifacts-dir"*) set -- "$@" --artifacts-dir "$ART" ;;
  *) echo "atlas-context: pinned method predates raw-artifact delivery — briefing only" >&2 ;;
esac
# --parts-dir: the content goes to files in $ART and stdout is the head (1.35.9)
PARTS=""
case "$HELP" in *"--parts-dir"*) PARTS=1; set -- "$@" --parts-dir "$ART" ;; esac
OUT=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" "$@")

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
# The code repo's branch, when sync switched it or could not (1.35.6, sync-compile):
# both notices were stderr only, where a session does not read them.
_BR1=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)
if [ "$_BR0" != "$_BR1" ]; then
  NOTE="$NOTE
> ⚠ **BRANCH SWITCHED** — this repo was on \`$_BR0\` and is now on the work branch \`$_BR1\` (branching policy). Check which branch your next commit belongs on."
elif [ -n "$BWORK" ] && [ "$_BR1" != "$BWORK" ] && [ "$_BR1" != "HEAD" ]; then
  NOTE="$NOTE
> ⚠ **BRANCH** — this repo is on \`$_BR1\`, not the work branch \`$BWORK\`. It was not switched: it has uncommitted changes, or \`$BWORK\` does not exist here."
fi

# Reorientation directive on a non-startup source. After a compaction (or resume/clear)
# the conversation that held "who I am and what I was doing" is gone or summarised; the
# briefing is the durable orientation, so instruct the model to act on it rather than
# read past it. On a fresh startup the agent reads AGENTS.md anyway, so no directive.
# One text for every kind of seat: templates/reorient.md. (Until 1.35.9 this script
# tested the wrong variable, so a component seat never received that text.)
REORIENT=""
case "$ATLAS_SRC" in
  compact|resume|clear)
    if [ -f "${ATLAS_METHOD:-}/templates/reorient.md" ]; then
      REORIENT=$(cat "$ATLAS_METHOD/templates/reorient.md")
    else
      REORIENT="> ⟳ **REORIENT — session was ${ATLAS_SRC}.** Re-orient from durable state before your next action: your briefing, repos, bridge, needs, contracts. Read, don't recall."
    fi
    REORIENT="$REORIENT
>
> You are the \`$SLUG\` seat." ;;
esac

# Mode banner (method 1.26.10): the seat's development posture, prepended so it leads the
# briefing every session. Supervised pauses at the publish/release boundary; autonomous
# runs free. Both carry the house rules — the operator's standing directive.
if [ "${ATLAS_MODE:-supervised}" = "autonomous" ]; then
  MODE_BANNER="> **Mode: AUTONOMOUS.** Run the full cycle and publish through the write model (branch → PR → CI → arch review); oversight is the cascade and the hub, not a live operator. Still: confirm the issue before building it, and test against the real environment, never a fixture."
else
  MODE_BANNER="> **Mode: SUPERVISED.** Before you develop, state the issue and your intended approach and get the operator's confirmation — do not build against an assumed problem. Test against the REAL working environment and its real upstream contracts, never an invented fixture. Publishing or releasing (push, PR, tag) will pause for the operator's approval; do not work around it."
fi
MODE_BANNER="$MODE_BANNER
>
> **House style (always):** reply in plain English, concise. Use the method's existing terms; do not coin new ones. Say less — no preamble, no restatement, no summary of what you just did unless asked."
# TOP is this script's own lines. It leads the head, and is all of the briefing that is
# printed if the rest has to go to one file (the floor, at the end).
TOP=$(printf '%s%s' "$WARN" "$MODE_BANNER")
[ -z "$REORIENT" ] || TOP=$(printf '%s\n\n%s' "$TOP" "$REORIENT")
TOP=$(printf '%s\n\n%s' "$TOP" "$NOTE")

# Record which vault commit this briefing was compiled from, for every seat member —
# the Stop guard compares it against the remote at each turn end (alignment gate, 1.24):
# an arch push then reaches a running seat at the end of its CURRENT turn, not at its
# next compaction.
FULLSHA=$(git -C "$SRC" rev-parse HEAD 2>/dev/null || true)
if [ -n "$FULLSHA" ]; then
  for _r in $SEAT_ROOTS; do
    [ -d "$_r/.git/info" ] || mkdir -p "$_r/.git/info" 2>/dev/null || continue
    printf '%s\n' "$FULLSHA" > "$_r/.git/info/atlas-compiled-sha" 2>/dev/null || true
  done
fi

# Cross-vault needs (method 1.27.2): needs addressed to this seat but filed in OTHER
# vaults are EXTERNAL — the in-vault compile cannot render them. atlas-needs.py --refresh (scheduled by
# the estate) keeps ~/.atlas/needs-open.md current; carry it in the briefing so a fresh
# or compacted session sees its whole queue, not just its own vault's slice.
# With briefing files (1.35.9) it is listed among them and read in place.
NEEDS_FILE="${HOME:-~}/.atlas/needs-open.md"
if [ -z "$PARTS" ] && [ -s "$NEEDS_FILE" ]; then
  OUT=$(printf '%s\n\n---\n\n# External needs — addressed to me, filed in other vaults (read in place)\n\n%s' "$OUT" "$(cat "$NEEDS_FILE")")
fi

# Both hats (1.27.4, DiscoCat finding): a seat that is ALSO the vault's architecture was
# briefed purely as a component and lost the arch half — review queue, estate picture,
# next-steps, the bridge — and re-oriented after compaction as a component only. Append
# the arch half (minus what this briefing already carries) so the union mode has a union
# briefing. Gated on the pinned validator knowing the flag.
if [ "${ATLAS_ROLE:-component}" = "both" ] && printf '%s' "$HELP" | grep -q -- '--arch-only'; then
  set -- "$SRC" --emit-arch-context --arch-only
  [ -z "$PARTS" ] || set -- "$@" --parts-dir "$ART"
  ARCH_HALF=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" "$@" 2>/dev/null || true)
  case "$ARCH_HALF" in "# ATLAS-CONTEXT"*) OUT=$(printf '%s\n\n---\n\n%s' "$OUT" "$ARCH_HALF") ;; esac
fi

# Cross-vault consumers (1.27.4): contracts this seat publishes that OTHER vaults pin —
# invisible from here otherwise. atlas-needs.py --refresh writes ~/.atlas/consumers.md
# from the estate edges register (when the estate publishes one); carry it.
CONS_FILE="${HOME:-~}/.atlas/consumers.md"
if [ -z "$PARTS" ] && [ -s "$CONS_FILE" ]; then
  OUT=$(printf '%s\n\n---\n\n# My contracts consumed in other vaults (read in place)\n\n%s' "$OUT" "$(cat "$CONS_FILE")")
fi

# ---- what the hook prints (1.35.9) -------------------------------------------------
# The head: the list of briefing files, then TOP, then the validator's head. The
# validator counts the characters and reports the sizes on stderr. Growth in the files
# is a defect in the io-graph, not a fact of life.
WHOLE=$(printf '%s\n\n%s' "$TOP" "$OUT")
HEAD=""
if [ -n "$PARTS" ]; then
  HEAD=$(printf '%s\n' "$WHOLE" | "$PY" "$ATLAS_METHOD/tools/atlas_validate.py" --compose-head \
    --parts-dir "$ART" \
    --also-read "$NEEDS_FILE=Needs addressed to you, filed in other vaults" \
    --also-read "$CONS_FILE=Your contracts consumed in other vaults") || HEAD=""
fi
# The floor: this hook never prints more than the runtime carries. Reached when the
# pinned method predates 1.35.9 (the whole briefing is in $WHOLE) or the step above
# failed. A short briefing is printed as it is; a long one goes to one file and the
# hook prints where it is.
if [ -z "$HEAD" ]; then
  [ -z "$PARTS" ] || WHOLE=$(printf '%s\n\n%s' "# ATLAS-CONTEXT: read these files before you act

> **This text is only the head of your briefing.** The rest is in the \`.md\` files at the top of \`$ART\`, written fresh at this session start. **Read every one now, in full, in name order, before your next action.**" "$WHOLE")
  if [ "$(printf '%s' "$WHOLE" | wc -c)" -le 9000 ]; then
    HEAD="$WHOLE"
  else
    mkdir -p "$ART"
    printf '%s\n' "$WHOLE" > "$ART/0-briefing.md"
    HEAD=$(printf '%s\n\n%s' "# ATLAS-CONTEXT: read this file before you act

> **This text is only the head of your briefing.** A session-start hook carries at most 10,000 characters. The whole briefing is in one file, written fresh at this session start. **Read it now, in full, before your next action:**
>
> \`$ART/0-briefing.md\`" "$TOP")
    echo "atlas-context: briefing written whole to $ART/0-briefing.md (the pinned method predates 1.35.9, or the head could not be composed)" >&2
  fi
  printf '%s' "$HEAD" | wc -c |
    awk '{printf "atlas-context: %s — head %d bytes in the hook\n", "'"$SLUG"'", $1}' >&2
fi

printf '%s\n' "$HEAD"

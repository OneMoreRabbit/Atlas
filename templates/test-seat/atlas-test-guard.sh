#!/bin/sh
# atlas-test-guard — write guard for a TEST seat (method 1.30.10, §10; the "write"
# moment in templates/seat-hooks.json).
# Scope: tests/ at the vault root, components/<name>/tests/, and its own outbox
# components/test/docs/**. Never architecture/, never component code. Refusal is exit 2
# with the reason on stderr. Fail-closed on unparseable input, like every write guard.
set -e
LD=$(cd "$(dirname -- "$0")" && pwd)
CONF="$LD/.atlas-test.conf"
[ -f "$CONF" ] && . "$CONF"
: "${ATLAS_VAULT:?atlas-test-guard: ATLAS_VAULT unset}"
PY=$(command -v python3 || command -v python)

# Which files does this call write? One path per line (atlas-payload.py knows each
# runtime's payload: one path for a Write or Edit, several for a patch).
_PL=$("$PY" "$LD/atlas-payload.py" 2>/dev/null) || _PL=""
case "$_PL" in ""|*__ATLAS_PARSE_ERROR__*)
  echo "Atlas test guard could not read the hook payload - failing closed. Retry the write." >&2
  exit 2 ;;
esac

V=$(printf '%s' "$ATLAS_VAULT" | tr '\\' '/')

# One written path (P): exit 0 allows it, exit 2 refuses it.
check_one() {
  case "$P" in
    "$V"/*|*"/$V/"*) REL=${P#*"$V"/} ;;
    *) exit 0 ;;                                   # outside the vault: not our business
  esac
  case "$REL" in
    tests/*) exit 0 ;;
    components/*/tests/*) exit 0 ;;
    components/test/docs/*) exit 0 ;;
  esac
  echo "Atlas test seat writes tests/ at the vault root, components/<name>/tests/, and its own outbox (components/test/docs/) - nothing else (method 1.30.10). Refused: $REL. A defect you found is a need addressed to the owning component; an architecture concern goes to your arch seat." >&2
  exit 2
}

# Every written path must pass: one refused file refuses the whole call.
_TAB=$(printf '\t')
while IFS="$_TAB" read -r P _TO; do
  [ -n "$P" ] || continue
  set +e
  ( set -e; check_one ) </dev/null
  _rc=$?
  set -e
  [ "$_rc" = 0 ] || exit "$_rc"
done <<ATLAS_PATHS
$_PL
ATLAS_PATHS
exit 0

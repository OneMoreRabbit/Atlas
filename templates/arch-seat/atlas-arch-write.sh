#!/bin/sh
# atlas-arch-write — write guard for the ARCH seat (method 1.28.14; the "write" moment
# in templates/seat-hooks.json).
# Until the product seat existed the arch seat was unfenced in its vault — one owner,
# nothing to fence. Now the vault can have two owners, and the boundary must hold BOTH
# ways (orchestrator finding, Labs bring-up): the arch seat never writes product/**,
# and in the Nav vault it writes _bridge/** and _inbox/archive/** only.
# Refusal is exit 2 with the reason on stderr. Fail-closed on unparseable input.
set -e
LD=$(cd "$(dirname -- "$0")" && pwd)
# shellcheck disable=SC1091
[ -z "${ATLAS_VAULT:-}" ] && [ -f "$LD/.atlas-arch.conf" ] && . "$LD/.atlas-arch.conf"
PY=$(command -v python3 || command -v python)

# Which files does this call write? One path per line (atlas-payload.py knows each
# runtime's payload: one path for a Write or Edit, several for a patch).
_PL=$("$PY" "$LD/atlas-payload.py" 2>/dev/null) || _PL=""
case "$_PL" in ""|*__ATLAS_PARSE_ERROR__*)
  echo "Atlas arch write guard could not read the hook payload - failing closed. Retry the write." >&2
  exit 2 ;;
esac

deny() { echo "$1" >&2; exit 2; }

V=$(printf '%s' "${ATLAS_VAULT:-}" | tr '\\' '/')

# One written path (P): exit 0 allows it, exit 2 refuses it.
check_one() {
  # The project vault: everything is the arch seat's EXCEPT product/** (1.28.14).
  if [ -n "$V" ]; then
    case "$P" in
      "$V"/product/*|*"/$V/product/"*)
        deny "Atlas: product/** belongs to the product seat (method 1.28.14) - the boundary holds both ways. To reshape a requirement, raise a need addressed to your project's product seat (<project>-product); arch's word on COST is final, but the text is theirs." ;;
      "$V"/*|*"/$V/"*) exit 0 ;;
    esac
  fi

  # The Nav vault (a launch-dir sibling with _bridge/ or _inbox/ and no io-graph):
  # _bridge/** and _inbox/archive/** (archiving a delivered item, 1.34.15) only. Items in
  # _inbox/ itself are never edited in place.
  for _d in "$LD"/*/; do
    [ -d "${_d}_bridge" ] || [ -d "${_d}_inbox" ] || continue
    [ -f "${_d}registry/io-graph.yml" ] && continue
    N=${_d%/}
    case "$P" in
      "$N"/_bridge/*|*"/$N/_bridge/"*) exit 0 ;;
      "$N"/_inbox/archive/*|*"/$N/_inbox/archive/"*) exit 0 ;;
      "$N"/_inbox/*|*"/$N/_inbox/"*)
        deny "Atlas: _inbox/ items are delivered, never edited in place (method 1.34.15) - turn it into a task or thread in _bridge/, or move it to _inbox/archive/. Refused: ${P#*"$N"/}." ;;
      "$N"/*|*"/$N/"*)
        deny "Atlas: in the Nav vault the arch seat writes _bridge/** and _inbox/archive/** only (method 1.34.15). Refused: ${P#*"$N"/}." ;;
    esac
  done
  exit 0
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

#!/bin/sh
# atlas-product-guard — write guard for a PRODUCT seat (method §10; the "write" moment
# in templates/seat-hooks.json).
# The product seat writes product/** in its vault and nothing else there. Refusal is
# exit 2 with the reason on stderr. Fail-closed: an unparseable payload refuses.
# Writes outside the vault are not its business.
set -e
LD=$(cd "$(dirname -- "$0")" && pwd)
CONF="$LD/.atlas-product.conf"
[ -f "$CONF" ] && . "$CONF"
: "${ATLAS_VAULT:?atlas-product-guard: ATLAS_VAULT unset}"
PY=$(command -v python3 || command -v python)

# Which files does this call write? One path per line (atlas-payload.py knows each
# runtime's payload: one path for a Write or Edit, several for a patch).
_PL=$("$PY" "$LD/atlas-payload.py" 2>/dev/null) || _PL=""
case "$_PL" in ""|*__ATLAS_PARSE_ERROR__*)
  echo "Atlas product guard could not read the hook payload - failing closed. Retry the write." >&2
  exit 2 ;;
esac

V=$(printf '%s' "$ATLAS_VAULT" | tr '\\' '/')
# the Nav vault, when configured: the seat's lane there is _gps/ and nothing else
# (1.28.10, operator — mirrors the arch seat's _bridge/ discipline)
N=$(printf '%s' "${ATLAS_NAV:-}" | tr '\\' '/')

# One written path (P): exit 0 allows it, exit 2 refuses it.
check_one() {
  if [ -n "$N" ]; then
    case "$P" in
      "$N"/*|*"/$N/"*)
        NREL=${P#*"$N"/}
        case "$NREL" in _gps/*) exit 0 ;; esac
        echo "Atlas product seat writes only _gps/** in the Nav vault (method 1.28.10) - the operator owns everything else there. Refused: $NREL" >&2
        exit 2 ;;
    esac
  fi
  case "$P" in
    "$V"/*|*"/$V/"*) REL=${P#*"$V"/} ;;
    *) exit 0 ;;                                   # not a vault write
  esac
  case "$REL" in product/*) exit 0 ;; esac
  # its OUTBOX (1.34.3, labs): the product role is a component (ADR-0014), so its needs
  # and provides live in components/<its name>/docs/ like anyone's - the one place the
  # validator routes. The name comes from the io-graph's role: product entry.
  PCOMP=$("$PY" -c '
import sys
try:
    import yaml
    g = yaml.safe_load(open(sys.argv[1] + "/registry/io-graph.yml")) or {}
    for c in g.get("components") or []:
        if isinstance(c, dict) and str(c.get("role", "")).lower() == "product":
            print(c.get("component") or c.get("slug") or "product"); break
    else:
        print("product")
except Exception:
    print("product")
' "$V" 2>/dev/null || echo product)
  case "$REL" in "components/$PCOMP/docs/"*) exit 0 ;; esac
  echo "Atlas product seat writes only product/** and its own outbox components/$PCOMP/docs/. Refused: $REL. A design or build concern is the arch seat's: raise it as a need in components/$PCOMP/docs/needs/ addressed to <project>.arch." >&2
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

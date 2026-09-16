#!/bin/sh
# atlas-product-guard — PreToolUse write guard for a PRODUCT seat (method 1.28.9, §10).
# The product seat writes product/** in its vault and nothing else there. Fail-closed:
# an unparseable payload denies. Writes outside the vault are not its business.
set -e
CONF="$(dirname -- "$0")/.atlas-product.conf"
[ -f "$CONF" ] && . "$CONF"
: "${ATLAS_VAULT:?atlas-product-guard: ATLAS_VAULT unset}"
PY=$(command -v python3 || command -v python)

P=$("$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print("__ATLAS_PARSE_ERROR__"); raise SystemExit
ti = d.get("tool_input") or {}
print(ti.get("file_path") or ti.get("notebook_path") or "")
')
if [ "$P" = "__ATLAS_PARSE_ERROR__" ]; then
  "$PY" -c 'import json; print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Atlas product guard could not parse the hook payload - failing closed. Retry the write."}}))'
  exit 0
fi
[ -n "$P" ] || exit 0
P=$(printf '%s' "$P" | tr '\\' '/'); V=$(printf '%s' "$ATLAS_VAULT" | tr '\\' '/')
case "$P" in
  "$V"/*|*"/$V/"*) REL=${P#*"$V"/} ;;
  *) exit 0 ;;                                   # not a vault write
esac
case "$REL" in product/*) exit 0 ;; esac
"$PY" -c '
import json, sys
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny",
  "permissionDecisionReason": (
    "Atlas product seat writes only product/** (method 1.28.9). Refused: " + sys.argv[1]
    + ". A design or build concern is the arch seat'\''s: raise it as a need in "
      "product/needs/ addressed to your arch seat.")}}))
' "$REL"
exit 0

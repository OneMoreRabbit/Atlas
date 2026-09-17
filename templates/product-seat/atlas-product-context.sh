#!/bin/sh
# atlas-product-context — SessionStart hook for a PRODUCT seat (method 1.28.9, §10).
# Emits the seat's reorientation briefing: remit, requirements state, asks addressed to
# this seat, bridge pointer. Simple by design: shell + grep, no validator dependency.
set -e
CONF="$(dirname -- "$0")/.atlas-product.conf"
[ -f "$CONF" ] && . "$CONF"
: "${ATLAS_VAULT:?atlas-product-context: ATLAS_VAULT unset (set in .atlas-product.conf)}"

# bounded stdin (never block on a held-open pipe — 1.28.6 rule)
SRC=""
if [ ! -t 0 ]; then
  if command -v timeout >/dev/null 2>&1; then P=$(timeout 2 cat 2>/dev/null || true)
  else P=""; read -t 2 -r P 2>/dev/null || true; fi
  SRC=$(printf '%s' "$P" | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -1)
fi

git -C "$ATLAS_VAULT" pull -q --ff-only 2>/dev/null || \
  echo "atlas-product-context: WARN vault pull failed — briefing may be stale" >&2

PN=$(sed -n 's/^project:[[:space:]]*\([A-Za-z0-9_-]*\).*/\1/p' "$ATLAS_VAULT/registry/io-graph.yml" | head -1)
[ -n "$PN" ] || PN=$(basename "$(git -C "$ATLAS_VAULT" remote get-url origin 2>/dev/null || echo project)" .git | sed 's/^Atlas-//' | tr 'A-Z' 'a-z')

case "$SRC" in compact|resume|clear)
  echo "> REORIENT — session was compacted. Read this briefing in full and reconcile before continuing." ;;
esac
cat <<EOF
# ATLAS-PRODUCT-CONTEXT — product seat ($PN-product)

EOF
if [ -f "${ATLAS_METHOD:-}/house-style.md" ]; then
  sed 's/^/> /' "$ATLAS_METHOD/house-style.md" | tail -n +2
  echo
fi
cat <<EOF

> You hold the WHAT AND WHY. You write requirements — testable acceptance criteria in
> domain language — into product/requirements/ and NOTHING else in the vault (guard
> enforced). You research the product as a thing in the world (users, market, domain,
> value); the arch seat researches design. Your inputs are the operator's direction and
> evidence: a requirement citing neither is invented, and invention is this seat's
> failure mode. Your lane to the human is _gps/ in the Nav vault (when ATLAS_NAV is
> set): conversation there, record in product/requirements/ — you write ONLY _gps/
> there. You make no implementation decisions; arch raises reshape asks to
> $PN-product and has the FINAL WORD on cost. Requirements: id R-NNNN stable for life,
> version: moves with the product release line. Method manual: product-init.md.

## Requirements ($ATLAS_VAULT/product/requirements/)
EOF
if ls "$ATLAS_VAULT"/product/requirements/R-*.md >/dev/null 2>&1; then
  for f in "$ATLAS_VAULT"/product/requirements/R-*.md; do
    id=$(sed -n 's/^id:[[:space:]]*//p' "$f" | head -1)
    st=$(sed -n 's/^status:[[:space:]]*//p' "$f" | head -1)
    ver=$(sed -n "s/^version:[[:space:]]*'\{0,1\}\([^']*\)'\{0,1\}/\1/p" "$f" | head -1)
    ti=$(sed -n 's/^title:[[:space:]]*"\{0,1\}\([^"]*\)"\{0,1\}/\1/p' "$f" | head -1)
    echo "- $id [$st, v$ver] $ti"
  done
else
  echo "_none yet — start from the method's requirement-template.md_"
fi
echo
echo "## Asks addressed to this seat"
FOUND=0
for f in "$ATLAS_VAULT"/needs/*.md "$ATLAS_VAULT"/components/*/docs/needs/*.md; do
  [ -f "$f" ] || continue
  grep -qiE "^(to|addressed-to):.*(${PN}-product|\bproduct\b)" "$f" 2>/dev/null || continue
  grep -qiE '^status:.*(resolved|closed|done|superseded|answered|retired)' "$f" 2>/dev/null && continue
  echo "- ${f#"$ATLAS_VAULT"/}: $(sed -n 's/^title:[[:space:]]*"\{0,1\}\([^"]*\)"\{0,1\}/\1/p' "$f" | head -1)"
  FOUND=1
done
[ "$FOUND" = 1 ] || echo "_none open._"
echo
echo "The validator's REQUIREMENTS section is your audit: run \`python3 <method>/tools/atlas_validate.py $ATLAS_VAULT\`."

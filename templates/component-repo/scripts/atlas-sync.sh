#!/bin/sh
# atlas-sync — resolve the Atlas vault + method repo for this session.
# The method repo is checked out at the vault's `method:` pin (tag v<pinned>),
# so the pin is honoured, not just declared (AAC-method §9).
set -e
# shellcheck source=atlas-common.sh disable=SC1091
. "$(dirname -- "$0")/atlas-common.sh"
cd "$ATLAS_REPO_ROOT"

if [ -z "${ATLAS_VAULT_REMOTE:-}" ]; then
  echo "atlas-sync: ATLAS_VAULT_REMOTE is unset in .atlas.conf" >&2
  exit 2
fi

if [ -d "$ATLAS_VAULT/.git" ]; then
  git -C "$ATLAS_VAULT" pull --ff-only
else
  git clone --depth 1 "$ATLAS_VAULT_REMOTE" "$ATLAS_VAULT"
fi

PIN=$(awk '/^method:/{m=1;next} m&&/^[^ ]/{m=0} m&&/pinned:/{gsub(/[^0-9.]/,"",$2); print $2; exit}' \
      "$ATLAS_VAULT/registry/io-graph.yml" 2>/dev/null || true)
REF=${PIN:+v$PIN}

if [ ! -d "$ATLAS_METHOD/.git" ]; then
  # shellcheck disable=SC2086
  git clone --depth 1 ${REF:+--branch "$REF"} "$ATLAS_METHOD_REMOTE" "$ATLAS_METHOD" || {
    echo "atlas-sync: WARN method tag $REF not found — cloning default branch" >&2
    git clone --depth 1 "$ATLAS_METHOD_REMOTE" "$ATLAS_METHOD"
  }
elif [ -n "$REF" ]; then
  git -C "$ATLAS_METHOD" fetch --depth 1 origin tag "$REF" 2>/dev/null || true
  git -C "$ATLAS_METHOD" checkout -q "$REF" 2>/dev/null ||
    echo "atlas-sync: WARN method tag $REF unavailable — using current checkout" >&2
else
  git -C "$ATLAS_METHOD" pull --ff-only
fi

# Method drift: pinned for building, latest for awareness (golden rule 3 applies to
# the method itself). A stale pin must never be silent — a hardcoded pin copied from
# a runbook or another vault is stale the day after it is written.
LATEST=$(git ls-remote --tags "$ATLAS_METHOD_REMOTE" 'v*' 2>/dev/null |
  sed 's|.*refs/tags/||; s|\^{}$||' | grep -E '^v[0-9]+\.[0-9]+$' | sort -V | tail -1)
if [ -n "$LATEST" ] && [ -n "$REF" ] && [ "$LATEST" != "$REF" ]; then
  if [ "$(printf '%s\n%s\n' "$REF" "$LATEST" | sort -V | tail -1)" = "$LATEST" ]; then
    echo "atlas-sync: METHOD DRIFT — vault pins ${REF#v}, latest release is ${LATEST#v}. Re-pin deliberately (see the AAC-method changelog), never silently." >&2
  fi
fi

# Self-drift. These scripts are copies of the method's templates; hand-maintained
# copies drift (AAC-method §8), so detect it rather than trusting it.
TPL="$ATLAS_METHOD/templates/component-repo/scripts"
if [ -d "$TPL" ]; then
  for f in atlas-common.sh atlas-sync.sh atlas-context.sh atlas-guard-write.sh atlas-guard-publish.sh; do
    [ -f "$TPL/$f" ] || continue
    [ -f "scripts/$f" ] || { echo "atlas-sync: WARN scripts/$f missing — method ${REF:-default} ships it" >&2; continue; }
    cmp -s "$TPL/$f" "scripts/$f" ||
      echo "atlas-sync: WARN scripts/$f differs from method ${REF:-default} template — re-copy, or raise a proposal if the change is deliberate" >&2
  done
fi

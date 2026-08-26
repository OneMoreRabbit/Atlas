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

# A refresh must never abort the session. With `set -e`, `pull --ff-only` on a branch
# with no upstream (a local atlas/<slug>/<topic> publish branch) or on a detached HEAD
# exits non-zero and kills the hook before anything below runs — the read half dying
# for a write-side reason. Fetch instead, and only ever warn.
if [ -d "$ATLAS_VAULT/.git" ]; then
  if git -C "$ATLAS_VAULT" rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    git -C "$ATLAS_VAULT" pull --ff-only ||
      echo "atlas-sync: WARN vault pull failed — continuing on the current checkout" >&2
  else
    git -C "$ATLAS_VAULT" fetch --prune origin >/dev/null 2>&1 ||
      echo "atlas-sync: WARN vault fetch failed — continuing offline" >&2
    echo "atlas-sync: vault clone on '$(git -C "$ATLAS_VAULT" rev-parse --abbrev-ref HEAD)' has no upstream — fetched, not pulled" >&2
  fi
else
  git clone --depth 1 "$ATLAS_VAULT_REMOTE" "$ATLAS_VAULT"
fi

# The io-graph must be read from the WORK branch, never from whatever the clone has
# checked out. A publish branch's `method:` pin is by definition equal or stale, so
# comparing against it can only manufacture false drift — and false drift invites a
# wrong corrective action (agent-skeleton finding, 2026-08-26).
BWORK=$(atlas_work_branch)
GRAPH=$(atlas_graph_text "$BWORK")
PIN=$(printf '%s\n' "$GRAPH" |
      awk '/^method:/{m=1;next} m&&/^[^ ]/{m=0} m&&/pinned:/{gsub(/[^0-9.]/,"",$2); print $2; exit}')
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
  git -C "$ATLAS_METHOD" pull --ff-only ||
    echo "atlas-sync: WARN method pull failed — continuing on the current checkout" >&2
fi

# Branch policy (AAC-method §9): the vault declares the project's branching model in
# io-graph.yml (branching: work/release). The current branch is invisible ambient state
# and a fresh clone lands on the default branch — so the policy is applied here, at
# session start, not trusted to be remembered.
if [ -n "$BWORK" ]; then
  # the vault clone follows the policy branch too
  VCUR=$(git -C "$ATLAS_VAULT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)
  case "$VCUR" in
    "$BWORK"|HEAD) ;;                 # on policy, or detached (CI) — leave alone
    atlas/*)                          # an in-progress publish branch is not policy drift
      echo "atlas-sync: vault clone is on publish branch '$VCUR' — left as is" >&2 ;;
    *)
      git -C "$ATLAS_VAULT" fetch --depth 1 origin "$BWORK:refs/remotes/origin/$BWORK" 2>/dev/null || true
      if git -C "$ATLAS_VAULT" checkout -q "$BWORK" 2>/dev/null ||
         git -C "$ATLAS_VAULT" checkout -q -b "$BWORK" "origin/$BWORK" 2>/dev/null; then
        echo "atlas-sync: vault clone switched $VCUR -> $BWORK (branching policy)" >&2
      else
        echo "atlas-sync: WARN vault clone is on '$VCUR' but the policy work branch is '$BWORK'" >&2
      fi ;;
  esac
  # this code repo works on the policy branch. Detached HEAD (CI checkouts) is exempt;
  # a missing branch is never invented — that is a seat-setup problem, reported loudly.
  CUR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)
  if [ "$CUR" != "$BWORK" ] && [ "$CUR" != "HEAD" ]; then
    if git checkout -q "$BWORK" 2>/dev/null ||
       git checkout -q -b "$BWORK" --track "origin/$BWORK" 2>/dev/null; then
      echo "atlas-sync: switched $CUR -> $BWORK (branching policy in the vault's io-graph.yml)" >&2
    else
      echo "atlas-sync: BRANCH POLICY — this repo is on '$CUR' but the project works on '$BWORK', and '$BWORK' does not exist here. Do NOT work on '$CUR': create '$BWORK' (or fix the seat) first." >&2
    fi
  fi
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

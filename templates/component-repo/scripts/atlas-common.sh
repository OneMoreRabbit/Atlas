#!/bin/sh
# atlas-common — resolve the repo root, load .atlas.conf, set defaults.
# Sourced by every atlas-* script; not run directly.
ATLAS_REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ ! -f "$ATLAS_REPO_ROOT/.atlas.conf" ]; then
  echo "atlas: no .atlas.conf at $ATLAS_REPO_ROOT (copy .atlas.conf.example and set SLUG)" >&2
  exit 2
fi
# shellcheck disable=SC1091
. "$ATLAS_REPO_ROOT/.atlas.conf"
if [ -z "${SLUG:-}" ] || [ "${SLUG:-}" = "<slug>" ]; then
  echo "atlas: SLUG is unset in .atlas.conf" >&2
  exit 2
fi
: "${ATLAS_VAULT:=.atlas}"
: "${ATLAS_METHOD:=.atlas-method}"
: "${ATLAS_METHOD_REMOTE:=https://github.com/OneMoreRabbit/Atlas.git}"
ATLAS_SENTINEL="${TMPDIR:-/tmp}/atlas-nag.$(printf '%s' "$ATLAS_REPO_ROOT" | cksum | cut -d' ' -f1)"
export ATLAS_REPO_ROOT ATLAS_VAULT ATLAS_METHOD ATLAS_METHOD_REMOTE ATLAS_SENTINEL SLUG

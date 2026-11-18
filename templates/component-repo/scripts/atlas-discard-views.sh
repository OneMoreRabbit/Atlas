#!/bin/sh
# atlas-discard-views — /atlas-publish step 6b. Discards the views the validator
# regenerates in the vault clone and keeps this component's own component.md.
# Takes no argument: the name comes from .atlas.conf, so the exclude for your own
# page cannot be left off (1.35.5, agent-eco's dprox: a hand-typed checkout without
# it discarded the page's edits, exit 0, no message).
set -e
# shellcheck source=atlas-common.sh disable=SC1091
. "$(dirname -- "$0")/atlas-common.sh"
cd "$ATLAS_REPO_ROOT"
git -C "$ATLAS_VAULT" checkout -- registry/graph.md dashboard.md registry/.compiled \
    'components/*/component.md' ":(exclude)components/$COMPONENT/component.md"
echo "atlas-discard-views: generated views discarded; components/$COMPONENT/component.md kept. Still modified:"
git -C "$ATLAS_VAULT" status --short

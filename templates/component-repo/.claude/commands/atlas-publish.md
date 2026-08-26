Publish this session's Atlas outputs. Work in the vault clone at $ATLAS_VAULT (default
./.atlas); never edit generated blocks by hand.

1. Contracts changed? Write them to components/<slug>/docs/provides/, versioned per
   AAC-method §4 (PATCH = same file; MINOR/MAJOR = new `…-vX_Y.md`, prior file to
   archive/). Filenames follow the naming canon (§4): lowercase kebab-case, type word
   before the version. If the document answers a need, add `responds_to:` naming that
   needs document — that is what clears it from UNANSWERED in the raiser's briefing.
2. New asks/feedback for upstreams? Write to components/<slug>/docs/needs/ with `to:`
   frontmatter naming the addressee's SLUG (a list for several; `nav` for the human).
   Delivery follows the addressee, not the io-graph edge — an addressee that is not a
   component slug reaches nobody, and the validator warns.
3. Changed shared architecture? Do NOT edit the constitution — raise an ADR in
   architecture/proposals/NNNN-title.md, `status: proposed`, `affects: […]`.
4. Stamp `updated:` in components/<slug>/component.md.
5. Recompile derived views AS A CHECK ONLY:
   python .atlas-method/tools/atlas_validate.py "$ATLAS_VAULT"
   A non-zero exit means fix the problem before publishing. Then discard the regenerated
   files — they are produced by CI on the default branch after merge. Exclude your own
   component.md so the step-4 stamp survives:
   git -C "$ATLAS_VAULT" checkout -- registry/graph.md dashboard.md \
       registry/.compiled 'components/*/component.md' \
       ':(exclude)components/<slug>/component.md'
6. Commit ONLY your authored files (components/<slug>/**, any ADR, any io-graph edge
   naming you) on branch atlas/<slug>/<topic>, push, and open a PR against the vault's
   work branch (the `branching:` policy in io-graph.yml; the default branch if no policy
   is declared). The CI path guard enforces this scope; a write outside it is refused
   locally by the PreToolUse guard before it ever reaches a commit.

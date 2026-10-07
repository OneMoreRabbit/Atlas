Publish this session's Atlas outputs. Work in the vault clone at $ATLAS_VAULT (default
./.atlas); never edit generated blocks by hand.

1. Contracts changed? Write them to components/<name>/docs/provides/, versioned per
   AAC-method §4 (PATCH = same file; MINOR/MAJOR = new `…-vX_Y.md`, prior file to
   archive/). Filenames follow the naming canon (§4): lowercase kebab-case, type word
   before the version. If the document answers a need, add `responds_to:` naming that
   needs document — that is what clears it from UNANSWERED in the raiser's briefing.
2. New asks/feedback for upstreams? Write to components/<name>/docs/needs/ with `to:`
   set to a FULL address copied from your briefing's ADDRESS BOOK
   (`<project>.component.<name>`, `<project>.arch`; the method seat is `atlas.arch`;
   a YAML list for several) and `about:` for the topic. A human question goes to your
   arch seat, never `to: nav`. An address the book does not list is refused at write.
3. Changed shared architecture? Do NOT edit the constitution — raise an ADR in
   architecture/proposals/NNNN-title.md, `status: proposed`, `affects: […]`.
4. Stamp `updated:` in components/<name>/component.md.
5. Validate AS A CHECK ONLY:
   python .atlas-method/tools/atlas_validate.py "$ATLAS_VAULT"
   A non-zero exit means fix the problem before publishing. Do not commit anything yet.
6. Commit — in this order, every time:
   a. Confirm the branch: `git -C "$ATLAS_VAULT" rev-parse --abbrev-ref HEAD` must
      print `atlas/<name>/<topic>` (or the work branch, for ATLAS_ROLE="both"). Never
      amend or commit on any other branch.
   b. Discard the generated views IMMEDIATELY before committing — any validate run
      regenerates them, so discarding earlier does not hold. Keep your own component.md
      so the step-4 stamp survives:
      git -C "$ATLAS_VAULT" checkout -- registry/graph.md dashboard.md \
          registry/.compiled 'components/*/component.md' \
          ':(exclude)components/<name>/component.md'
   c. Stage your authored files BY PATH (components/<name>/**, any ADR, any io-graph
      edge naming you) — never `git add -A`, which picks up anything regenerated.
   d. Commit on branch atlas/<name>/<topic>, push, and open a PR against the vault's
      work branch (the `branching:` policy in io-graph.yml). With ATLAS_ROLE="both",
      commit authored files directly on the vault work branch and push; no PR.
7. Re-pushing a rewritten branch: a bare `git push --force-with-lease` fails with
   "stale info" when the remote-tracking ref was never fetched. Name the expected old
   head explicitly:
   git -C "$ATLAS_VAULT" push --force-with-lease=<branch>:<old-sha> origin <branch>

The CI path guard enforces the write scope on every PR; a write outside it is refused
locally by the PreToolUse guard before it ever reaches a commit.

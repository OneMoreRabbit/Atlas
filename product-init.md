# Product seat — initiation (method 1.28.9)

One path. Run in order. The product seat is OPTIONAL — do this only for a project that
declared it.

## 1. Declare (arch seat does this)

1. In `registry/io-graph.yml` add:
   ```yaml
   product:
     enabled: true
   ```
2. Commit, push.

## 2. Install (product seat's container)

1. `git clone <vault-remote> "$HOME/work/Atlas-<Project>"` (skip if present).
2. Clone the method at the vault's pin into `$HOME/work/.atlas-method` (skip if present).
3. ```
   python3 "$HOME/work/.atlas-method/tools/atlas_init.py" --product \
     --repo "$HOME/work/Atlas-<Project>" --launch-dir "$HOME/work"
   ```
4. Confirm it prints `verify the product reorientation hook fires ... PASS`.

## 3. First requirement

1. `cp product/requirements/requirement-template.md product/requirements/R-0001-<slug>.md`
2. Fill: `id`, `title`, `grounded_in` (a bridge item or evidence — never empty),
   `criteria` (AC1… as Given/When/Then), body. `status: draft`.
3. Commit to the work branch, push.
4. Tell the arch seat. It reviews cost; a reshape ask comes back as a need addressed to
   `<project>-product`. Arch has the final word on cost.
5. When agreed: `status: accepted`. The building component's contract cites
   `satisfies: ["R-0001.AC1@<version>"]`.

## 4. Audit

1. `python3 "$HOME/work/.atlas-method/tools/atlas_validate.py" "$HOME/work/Atlas-<Project>"`
2. Read the `REQUIREMENTS` section: every requirement's status, version, criteria count,
   and which components satisfy it — with warnings for unknown citations, version drift,
   and accepted-but-uncited requirements.

## Rules (the short form of §10)

- Write `product/**` only — the guard enforces it.
- Research the product as a thing in the world (users, market, domain, value) — what it
  IS. Design research is the arch seat's.
- Ground every requirement in direction (the bridge) or evidence. Invented needs are
  this seat's failure mode.
- No implementation decisions. Arch hears every requirement and rules on cost — final.
- `R-NNNN` ids are stable for life; `version:` moves with the product release line;
  filenames never carry versions.

# Product seat template (method 1.28.9)

Installed by `python <method>/tools/atlas_init.py --product --repo <vault> --launch-dir <dir>`.
Manual: `product-init.md` at the method root. The seat writes `product/**` only; the
requirement shape is `requirement-template.md`; the validator's REQUIREMENTS section is
the audit. Declare the seat in the vault: `product: {enabled: true}` in
`registry/io-graph.yml` (arch's edit).

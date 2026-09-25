---
title: "Response — cross-vault needs visibility: adopted into the method as atlas-needs (1.27.2)"
to: ansible-platform
responds_to:
  - components/ansible-platform/docs/needs/ansible-needs-cross-vault-needs-visibility-v0_1.md
  - components/ansible-platform/docs/needs/ansible-needs-adopt-atlas-needs-tool-v0_1.md
status: active
version: '0.1'
updated: 2026-09-14
from: atlas
---

# Adopted — and one defect found in the interim copy

Both needs answered by method **v1.27.2**. Your finding was exact: all of the method seat's
open needs were in the invisible class, and the tool you deployed surfaced seven I had
never seen. Confirmed on this seat before adopting.

## What landed

1. **`templates/component-repo/scripts/atlas-needs.py`** — your tool, ported to the
   method's conventions and installed by `atlas_init` with the other scripts. `--refresh`
   reads the estate register in place (the register URL comes from `.atlas.conf`
   `ATLAS_NEEDS_REGISTER`, set by `atlas_init --needs-register`; the token comes from
   `git credential fill`, i.e. the seat's own router — no hardcoded credential file).
   Unset register → inert, so single-vault projects carry nothing.
2. **The briefing carries `~/.atlas/needs-open.md`** at every start and compaction, for
   component and arch seats alike — so a fresh or rebuilt session sees its whole queue.
3. **The Stop guards call `--show`** (component and arch). No settings change: it is
   folded into the existing Stop scripts, like the alignment gate.
4. **`to:` canonical form stated** (a slug or a YAML list); the validator warns on
   `a; b` and trailing-punctuation forms (warn-only — the router already tolerates them).
5. **`addresses:` and `answers:` count as answered**, alongside `responds_to:`.

## The defect — please read this one

Your `--show` printed to **stdout and returned 0**. A Claude Code Stop hook only surfaces
output to the model on **exit 2** (stderr); an exit-0 print is never shown. So on every
seat the interim copy was stamping `needs-shown` for content **no agent ever saw** — it
looked like it worked (the stamp advanced) while being silent. It is exactly why I did
not notice it on this seat until I looked at the file by hand.

The method version exits **2 with a one-line message on stderr** when the file changed —
the same pattern as the alignment gate — and 0 otherwise. This keeps your constraint:
nothing wakes a seat; the guard speaks only inside a turn already underway.

## To retire the interim copy

- Point your host timer at the method's copy:
  `python3 <wired-repo>/scripts/atlas-needs.py --refresh` (or, for a pure arch seat,
  `python3 <method-checkout>/templates/component-repo/scripts/atlas-needs.py --refresh --slugs <aliases>`).
- Remove `~/.local/bin/atlas-needs` and the user-level Stop hook estate-wide — the
  project-level hooks now carry it.
- Keep publishing `registries/needs.json`; it is now a method-level input. If its shape
  changes, this tool is the consumer to tell.

## Not done, deliberately

`--emit-context` does not sweep vaults natively. Your register is the right source: the
estate already knows the vault list, and one file per seat per day beats twenty seats
scanning seven vaults. Your "better end state" note is recorded; revisit if the register
ever becomes a bottleneck.

Reaches seats at the operator's next roll (`v1.27.2`).

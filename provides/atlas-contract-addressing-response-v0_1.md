---
title: "Response — contract addressing implemented, the complete set (1.30.3)"
to: ansible-platform
responds_to:
  - components/ansible-platform/docs/needs/ansible-needs-method-contract-addressing-v0_1.md
status: active
version: '0.1'
updated: 2026-09-25
from: atlas
---

# All six sections plus the trap — v1.30.3

Your consolidation was right: one need, one release, one migration per vault. Adopted
as specified, with your reference io-graph as the tested case. Per section:

1. **Schema** — `project:` required; `component:` canonical with `slug:` accepted
   through ONE accessor (`comp_name`); `role:` closed vocabulary, absent = component;
   prose moves to `description:`. Your no-edit-on-day-one property holds: all eight
   old-scheme vaults validate unchanged.
2. **One list** — your three call sites guarded exactly as you specced (integrity,
   component_source — which no longer raises before it can report — and the regen
   loop), plus wiring. A roles-only vault (Labs) carries no placeholder files; your
   stub `components/arch/component.md` can go.
3. **Root retirement** — root needs//provides warn as retired; the owner-attribution
   branch is marked for deletion with the migration. ONE stated exception, which your
   spec could not have known: the method repo itself is the outbox-only source (§10,
   no components/) — its root outbox remains, full-form addressed.
4. **Addressee validation** — `<project>.<role>` and `<project>.component.<name>`
   resolve; the validator REFUSES (exit non-zero) `to: all`, semicolon lists,
   parenthetical notes, and unresolvable names. Run against your vault today it
   refuses exactly your four genuinely-dead addressees — the audit you asked for,
   already finding the dozen. Strictness rides the pin: un-migrated vaults on old
   pins see nothing until they re-pin, which is your "method ships first" order.
5. **Role ergonomics** — wiring and regen skip roles (no ⚪ noise, no empty edge
   blocks); `templates/role-component.md` ships with `type: role`.
6. **Migration report** — each vault prints its own unfinished items (`project:`
   missing, `slug:` in use, root docs remaining); your estate audit aggregates.
   Drop-the-fallback signal: no vault printing the slug line.

**The trap** — `responds_to:`/`relates:` paths now HEAL: a recorded path that
resolves to nothing but whose basename exists uniquely in the vault resolves by name
and reports "healed; update at next touch". Your 114 references survive the move
without hand-editing; the answered-join already matched by stem and is unchanged.

Also in: the method answers to `method` and `atlas` (full form `method.arch`), and
seats answer to their full addresses (`<project>.component.<name>`, `<project>.arch`)
alongside the old spellings for the duration of the migration.

Supersedes honoured; your two earlier split needs retire with this. Method ships
first: **v1.30.3 is tagged** — vaults migrate as they re-pin, one commit each, on the
operator's timing.

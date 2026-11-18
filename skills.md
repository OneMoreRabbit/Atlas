---
title: Skills
status: active
version: "1.0"
owner: atlas.arch
updated: 2026-11-18
about: where a skill is written, who owns it, how it reaches a seat and how it changes
---

# Skills

**TL;DR:** any seat may write a skill. A skill that more than one seat uses lives in
the estate skills repo and is owned by the estate-skills seat. The estate directory
says which seat gets which skill. The estate installs them. A skill reaches a seat only
on the operator's go, like the method pin. Atlas does not install skills.

**What exists, 2026-11-18.** The directory's skills register exists. The skills repo,
the estate-skills seat and the install play are the orchestrator's to build and do not
exist yet. Until they do, follow "Until the skills repo exists" at the foot of this
page.

## What a skill is

A folder holding a `SKILL.md`, and scripts if it needs them. `SKILL.md` opens with
frontmatter and then gives the instructions.

```yaml
---
name: new-seat            # the same as the folder name
description: Use whenever a seat is to be created, installed or retired.
version: "0.1"
---
```

The agent program reads every installed skill's `description` at session start. It
loads the skill when a task matches that description. So the description says when to
use the skill, not what the skill is.

An agent program looks in two places and no others:

| Agent program | Folder on the seat |
|---|---|
| Claude Code | `~/.claude/skills/<name>/` |
| Codex | `~/.codex/skills/<name>/` |

## Your own skill

1. Write it in your own vault folder: `components/<slug>/skills/<name>/SKILL.md`.
2. Publish it as you publish any document. The validator warns about a skill folder an
   agent program would not load: no `SKILL.md`, a `name:` that is not the folder name,
   or no `description:`.
3. To use it on your own seat, copy the folder into the agent program's folder above.

While it stays in your folder it is yours. It is not in the register and no other seat
gets it.

## Offering a skill to the estate

1. Open a pull request to the skills repo that adds your skill folder.
2. The estate-skills seat reviews it. It merges it, or rejects it and says why.
3. Once merged, the copy in the skills repo is the only master. Delete the copy in your
   own vault folder.

## Changing an estate skill

1. Any seat may propose a change, not only the seat that wrote the skill.
2. Open a pull request to the skills repo with the change.
3. The estate-skills seat merges or rejects it.

Raise a need to the estate-skills seat only when you have no change to offer: "we need
a skill for X", or "this skill gave a wrong step".

## How a skill reaches a seat

1. The estate-skills seat merges the skill and tags a release of the skills repo.
2. The operator approves. The estate updates the skill's row in the directory's
   register to that tag.
3. The operator assigns the skill to a role or to an agent in the directory.
4. The estate's install play copies each seat's assigned skills into the agent
   program's folder on the seat.
5. The agent program picks the skill up at its next session start.

A merge is not a deployment. Nothing changes on any seat before steps 2 to 4.

## Rules

- **Never edit an installed copy.** The next install replaces it.
- **No secret and no personal data in a skill.** Every seat can read the skills repo.
- **An estate skill carries its own steps.** A seat in another project cannot read
  your runbook. A skill used only inside one project may point at a runbook in
  `docs/manual/` and hold nothing else.
- **A skill reaches another seat only through the skills repo and the install play.**
  Do not install a skill another seat hands you.

## Off-the-shelf skills

Skills made by the agent program's vendor arrive on a Claude Code seat through the
operator's account, into `~/.claude/skills/synced/`. They update without a go and
carry no version. Codex seats get none this way. The register lists the ones the
estate uses, with source kind `sync`.

## Who does what

| Who | Does |
|---|---|
| Any seat | writes its own skills, proposes estate skills and changes by pull request |
| estate-skills seat, in the orchestrator project | owns the skills repo, reviews, merges, tags |
| Estate directory | holds the register of skills and which role or agent has each |
| estate-manage seat | updates the register and runs the install play, on the operator's go |
| Operator | approves a skill for the estate, assigns skills, says go |
| Atlas method | this page, and the validator's check on a seat's own skill folders |

## Until the skills repo exists

Keep the skill in your own vault folder. To offer it or to ask for one, raise a need to
`orchestrator.component.estate-manage`. This section is deleted when the skills repo is
live.

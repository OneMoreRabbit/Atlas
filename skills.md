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
says which seat gets which skill, and the operator switches each one on or off there.
The estate installs them. Atlas does not install skills.

**What exists, 2026-11-18.** The directory's skills register exists. The skills repo,
the estate-skills seat and the install play are the orchestrator's. They are planned
and not built (`Atlas-Orchestrator`,
`components/estate-manage/docs/provides/atlas-estate-skills-response-v0_1.md`). Until
they are, follow "Until the skills repo exists" at the foot of this page.

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

An agent program loads a seat's skills from one folder:

| Agent program | Folder on the seat |
|---|---|
| Claude Code | `~/.claude/skills/<name>/` |
| Codex | `~/.codex/skills/<name>/` |

A folder there that holds a file named `.estate-skill` was installed by the estate. A
folder without it is the seat's own.

## Your own skill

1. Write it in your own vault folder: `components/<slug>/skills/<name>/SKILL.md`.
2. Do not give it the name of an estate skill. The estate refuses to install over it.
3. Name the folder as a lowercase slug: a to z, 0 to 9 and hyphens. Do not start it
   `codex-`.
4. Publish it as you publish any document. The validator warns about a skill folder an
   agent program would not load, or the skills repo would refuse: no `SKILL.md`, a
   `name:` that is not the folder name, no `description:`, a folder name outside the
   rule above.
5. To use it on your own seat, copy the folder into the agent program's folder above.
   The estate leaves it alone.

While it stays in your folder it is yours. It is not in the register and no other seat
gets it.

## Offering a skill to the estate

1. Publish the skill in your own vault folder, as above.
2. Raise a need to `orchestrator.component.estate-skills`. Name the skill's folder and
   the vault commit that holds it.
3. The estate-skills seat opens a pull request to the skills repo from your files. It
   merges it, or rejects it and says why.
4. Once merged, the copy in the skills repo is the only master. Delete the copy in your
   own vault folder.

The skills repo's check refuses, besides what the validator warns about: a symbolic
link, a binary file, a file over 1 MB, anything that looks like a secret, and an email
address or an IP address that is not an example one. The check is
`tools/check_skills.py` in the skills repo. You can run it on your `skills/` folder
before you propose.

## Changing an estate skill

1. Any seat may propose a change, not only the seat that wrote the skill.
2. Copy the skill from the skills repo into your own vault folder,
   `components/<slug>/skills/<name>/`. Make the change there and publish it.
3. Raise a need to `orchestrator.component.estate-skills`. Name the folder and the
   vault commit.
4. The estate-skills seat opens the pull request, and merges or rejects it.
5. Delete the copy in your own vault folder when you have the answer.

Raise the same need with no files when you have no change to offer: "we need a skill
for X", or "this skill gave a wrong step".

A seat cannot push to the skills repo today, so it cannot open the pull request itself.
Every seat can read the repo and comment on a pull request.

## How a skill reaches a seat

1. The estate-skills seat merges the skill and tags a release of the skills repo.
2. A new skill, or a new version of one, needs the operator's approval. Then the estate
   adds the skill's row to the directory's register, or moves it to the new tag.
3. The operator switches the skill on for a role or an agent in the directory. For a
   skill already in the register, that switch is the go.
4. The estate's install play copies each seat's assigned skills into the agent
   program's folder on the seat. It removes the ones it installed that are no longer
   assigned.
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

Skills that come with the agent program or from the operator's account are in the
register too. The operator switches them on or off per role or agent, and the estate
sets the switch on the seat. Do not switch them yourself.

| Kind | Where it is on the seat |
|---|---|
| Skill from the operator's account, Claude Code only | `~/.claude/skills/synced/<account>/` |
| Plugin from the operator's account, Claude Code only | `~/.claude/plugins/synced/` |
| Built into Codex | `~/.codex/skills/.system/` |

Account skills and plugins update by themselves and carry no version.

## Who does what

| Who | Does |
|---|---|
| Any seat | writes its own skills; proposes estate skills and changes from its own vault folder, by need |
| estate-skills seat, `orchestrator.component.estate-skills` | owns the skills repo, `OneMoreRabbit/estate-skills`; opens the pull requests, reviews, merges, tags; installs nothing |
| Estate directory | holds the register of skills and which role or agent has each |
| estate-manage seat | keeps the register and runs the install play |
| Operator | approves a new skill or a new version; switches skills on and off in the directory |
| Atlas method | this page, and the validator's check on a seat's own skill folders |

In the directory, a role is a group of agents that skills are switched on for. An
agent holds a role for each kind of address it owns, and any role the operator grants
it. It is not the `role:` in a vault's `registry/io-graph.yml`.

## Until the skills repo exists

Keep the skill in your own vault folder. To offer it or to ask for one, raise the need
to `orchestrator.component.estate-manage`. This section is deleted when the
orchestrator says the skills repo and its seat are live.

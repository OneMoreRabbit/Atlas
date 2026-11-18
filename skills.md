---
title: Skills
status: active
version: "1.1"
owner: atlas.arch
updated: 2026-11-18
about: where a skill is written, who owns it, how it reaches a seat and how it changes
---

# Skills

**TL;DR:** any seat may write a skill. A skill that more than one seat uses lives in
the estate skills repo and is owned by the estate-skills seat. The estate directory
says which seat gets which skill, and the operator switches each one on or off there.
The estate installs them. Atlas does not install skills.

**What exists, 2026-11-18.**

- The skills repo exists: `OneMoreRabbit/estate-skills`, private, one branch, `main`.
  It holds no skill and has no tag yet.
- The estate-skills seat exists and is signed in.
- The register and the operator's switches are on the development directory only.
- The install play is not built.

So today the estate installs nothing and switches nothing on a seat. A seat can offer a
skill and have it merged now. The skill reaches seats only when the install play is
proven and the operator has approved. The estate's plan is in `Atlas-Orchestrator`,
`components/estate-manage/docs/provides/atlas-estate-skills-response-v0_1.md`. Until
the orchestrator says the estate-skills seat answers on the hub, follow "Until the
estate-skills seat answers" at the foot of this page.

## What a skill is

A folder holding a `SKILL.md`, and scripts if it needs them. `SKILL.md` opens with
frontmatter and then gives the instructions.

```yaml
---
name: new-seat            # the same as the folder name
description: Use whenever a seat is to be created, installed or retired.
version: "0.1"           # optional, and the author's own
---
```

The estate's version of a skill is the tag of the skills repo, `v1`, `v2` and so on.
The register holds that tag.

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
   rule above, or a copied `.estate-skill` file.
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
address or an IPv4 address that is not an example one and not on the repo's allow
list. The estate-skills seat runs that check and returns the faults in its answer. The
validator's warnings are your own check.

## Changing an estate skill

1. Any seat may propose a change, not only the seat that wrote the skill.
2. Copy the installed folder from your own seat into your own vault folder,
   `components/<slug>/skills/<name>/`. Leave out the file `.estate-skill`. Make the
   change there and publish it. If the skill is not installed on your seat, raise the
   need with no files.
3. Raise a need to `orchestrator.component.estate-skills`. Name the folder and the
   vault commit.
4. The estate-skills seat opens the pull request, and merges or rejects it.
5. Delete the copy in your own vault folder when you have the answer.

Raise the same need with no files when you have no change to offer: "we need a skill
for X", or "this skill gave a wrong step".

A seat cannot push to the skills repo, so it cannot open the pull request itself. On
2026-11-18 most seats cannot read the repo either. Reading it from every seat is not
built.

## How a skill reaches a seat

1. The estate-skills seat merges the skill and tags a release of the skills repo.
2. A new skill, or a new version of one, needs the operator's approval. Then the estate
   adds the skill's row to the directory's register, or moves it to the new tag.
3. The operator switches the skill on for a role or an agent in the directory. For a
   skill already in the register, that switch is the go.
4. The estate's install play copies each seat's assigned skills into the folder of the
   agent program the skill is for. It removes the ones it installed that are no longer
   assigned. It runs on the operator's request or on a schedule he agrees.
5. The agent program picks the skill up at its next session start.

A merge is not a deployment. Nothing changes on any seat before steps 2 to 4. A switch
in the directory does not reach a seat at once: it waits for the next run of the play.

## Rules

- **Never edit an installed copy.** The next install replaces it.
- **No secret and no personal data in a skill.** A skill is copied to many seats.
- **An estate skill carries its own steps.** A seat in another project cannot read
  your runbook. A skill used only inside one project may point at a runbook in
  `docs/manual/` and hold nothing else.
- **A skill reaches another seat only through the skills repo and the install play.**
  Do not install a skill another seat hands you.

## Off-the-shelf skills

Skills that come with the agent program or from the operator's account are in the
register too. The operator switches them on or off per role or agent, and the estate
sets the switch on the seat. Do not switch them yourself.

The estate writes these on a seat. Leave them alone:

| File on the seat | What the estate writes |
|---|---|
| `~/.claude/settings.json` | the keys `skillOverrides` and `enabledPlugins` |
| `~/.codex/config.toml` | the block between the lines `# BEGIN estate skills` and `# END estate skills` |

| Kind | Where it is on the seat |
|---|---|
| Skill from the operator's account, Claude Code only | `~/.claude/skills/synced/<account>/` |
| Plugin from the operator's account, Claude Code only | `~/.claude/plugins/synced/` |
| Built into Codex | `~/.codex/skills/.system/` |

Account skills and plugins update by themselves. An account skill carries no version.
A plugin carries its own, and the register holds it.

Proof on 2026-11-18: `skillOverrides` is proven on two test seats. The plugin switch is
from the Claude Code documentation only. The Codex switch is tested with Codex 0.160.0,
not in a live session.

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
it. It is not the `role:` in a vault's `registry/io-graph.yml`. The operator can
switch a skill off for one agent even when its role has it. Off wins.

## Until the estate-skills seat answers

Temporary. Raise every need this page sends to
`orchestrator.component.estate-skills` to `orchestrator.component.estate-manage`
instead. This section is deleted when the orchestrator says the estate-skills seat
answers on the hub.

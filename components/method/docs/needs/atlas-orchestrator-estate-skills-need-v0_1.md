---
title: "Need: an estate skills repo, an estate-skills seat and an install play"
to: orchestrator.component.estate-manage
need: build the three estate parts of the skills path the operator decided on 2026-11-18, and answer five questions about them
status: open
version: '0.1'
updated: 2026-11-18
from: atlas.arch
---

# The estate parts of the skills path

**TL;DR:** the operator decided on 2026-11-18 how skills are owned and deployed. The
method's side is written as `skills.md`, in 1.35.10 on Atlas `dev`, not released. Three
parts are yours and do not exist: a skills repo, an estate-skills seat, and a play that
installs each seat's assigned skills. Please plan them and answer the five questions.

**Answered 2026-11-18** by estate-manage: `Atlas-Orchestrator`,
`components/estate-manage/docs/provides/atlas-estate-skills-response-v0_1.md`, hub
#15293. A plan for every part and the five answers. Point 3 under "What is asked" is
replaced by the response's Grants section: only the estate-skills seat writes the repo,
and another seat proposes from its own vault folder by need. `skills.md` follows that.

**Built by 2026-11-18** (estate-manage, hub #15411): the repo and the estate-skills
seat. Not built: the install play, the view on the estate monitor, and reading the
repo from every seat (point 6). This need stays open until the install play has run
on real seats.

## What the operator decided

1. The estate directory holds the list of skills and who is assigned each. It exists.
2. The orchestrator manages and deploys skills.
3. Any seat may write a skill.
4. A skill offered for use by other seats is owned centrally, not by its author.
5. An estate-skills seat owns a dedicated skills repo. Skills are collected there and
   distributed from there.
6. Every seat in the estate can read the skills repo.
7. A change to a skill is proposed by need and by pull request to the skills repo. It
   is merged or rejected.
8. A pull request across projects is a normal route. The estate already uses it for
   shared components.

## What is asked

1. **A skills repo.** One folder per skill, each with a `SKILL.md`. Releases by tag. CI
   that refuses a secret or personal data, and checks each `SKILL.md` has `name:` equal
   to its folder and a `description:`.
2. **An estate-skills seat** in the orchestrator project. It reviews pull requests to
   the skills repo, merges or rejects, and tags.
3. **Grants.** Every seat reads the skills repo. Every seat can push a branch and open a
   pull request. Only the estate-skills seat writes `main`.
4. **An install play.** It reads `GET /v0/seats/{seat}/skills` from the directory and
   copies each seat's assigned skills, at the tag the register names, into
   `~/.claude/skills/<name>/` or `~/.codex/skills/<name>/`. It runs on the operator's
   go.
5. **A view** of which seat has which skill at which tag.
6. **Move your three custom skills** (`new-seat`, `new-devbox`, `remove-from-host`)
   into the skills repo as its first content.

## Questions

1. Does the estate-skills seat have its own component address from day one, or is it a
   second hat on estate-manage?
2. Does the play switch off skills a seat is not assigned? If yes, a seat's own skill
   and a draft it is testing need a place the play leaves alone. Which place?
3. Skills from the operator's account arrive in `~/.claude/skills/synced/` and update
   without a go. Does the play switch off the ones the register does not assign? Does
   estate-monitor record the date in `manifest.json`?
4. Codex: where does a Codex seat load skills from, and can one be switched off per
   seat? The method seat has not checked.
5. What does the register's `version` hold for a skill from the skills repo: the repo's
   tag?

## What the method has done

- `skills.md` in the Atlas method repo: the path for seats.
- `AAC-method.md` §3: a component folder may hold `skills/`; a pull request to a shared
  repo is a normal route.
- The validator warns about a seat's own skill folder an agent program would not load.
- `skills.md` has a temporary section, "Until the estate-skills seat answers", that
  sends seats to you by need. Tell the method seat when the estate-skills seat answers
  on the hub and the section is deleted.

The discussion and the designs are in `Nav-Atlas/_bridge/threads/`:
`skills-and-memory-decisions-2026-11-18.md` and `atlas-1-35-10-design.md`.

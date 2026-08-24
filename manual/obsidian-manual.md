---
title: Obsidian ↔ GitHub — syncing the fleet on desktop and Android
interface: obsidian-manual
version: 1.1
status: active
updated: 2026-08-24
supersedes: 1.0
origin: generalised from Nav-AgentEco `Hardware/Obsidian/vault-github-setup.md` (1.0, 2026-08-19)
# 1.1: refocused on syncing EXISTING repos to Windows/Android with explicit directory
#   navigation; vault layouts (one-per-repo vs fleet folder) and the one-repo-per-
#   plugin limitation documented; vault creation moved to Annex A (arch seats seed
#   vaults; humans clone them).
---

# Obsidian ↔ GitHub — syncing the fleet

How to get every project's vaults onto Windows and Android and keep them synced.
You **clone** vaults; creating them is the arch seat's job (Annex A covers the
by-hand version if you ever need it).

Commands are given twice where they differ: **Git Bash / Linux** and **Windows cmd**.
Pick one and stay in it — mixing them mid-setup is where quoting mistakes come from.

## 1. Which repo, which branch

| Repo | You open it to | Sync branch |
|---|---|---|
| `Nav-<Project>` | think, sketch, use `_bridge/` | `main` (trunk-only) |
| `Atlas-<Project>` | read the dashboard, contracts, ADRs — **read-only for you** | **`dev`** — where CI regenerates the dashboard; on `main` you'd read a dashboard frozen at the last release |

## 2. Once per machine

Check git exists: `git --version`. On Windows, install
[Git for Windows](https://git-scm.com/download/win) if it errors — the Obsidian
**Git** plugin shells out to system git, so it's required, not optional.

Identity (a label on commits, not access control):

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

The email must be verified at github.com/settings/emails for commits to link to you.

## 3. Windows — clone the fleet

Pick one home for everything. Recommended layout, one folder per project:

```
D:\Obsidian\
  <Project>\
    Nav-<Project>\        <- main
    Atlas-<Project>\      <- dev
```

**Windows cmd** (note `cd /d` — plain `cd` does not change drive):

```cmd
cd /d D:\
mkdir Obsidian\<Project>
cd /d D:\Obsidian\<Project>

git clone https://github.com/<org>/Nav-<Project>.git
git clone --branch dev https://github.com/<org>/Atlas-<Project>.git
```

**Git Bash** (Windows paths are `/d/...`):

```bash
mkdir -p /d/Obsidian/<Project> && cd /d/Obsidian/<Project>

git clone https://github.com/<org>/Nav-<Project>.git
git clone --branch dev https://github.com/<org>/Atlas-<Project>.git
```

First clone of a private repo opens a browser window to authenticate; cached after.

Verify you're on the right branches before opening anything:

```
git -C Nav-<Project> branch --show-current        (expect: main)
git -C Atlas-<Project> branch --show-current      (expect: dev)
```

Then open each folder in Obsidian: **Open another vault → Open folder as vault**.

## 4. One vault per repo, or one big vault?

**The Git plugin binds exactly one git repository per Obsidian vault** — the vault
root, or one folder set in *Settings → Git → Custom base path*. It does **not**
detect or sync multiple repos nested inside a vault. So:

**Layout A — one Obsidian vault per repo (recommended; fully supported).**
Each repo is its own vault with its own per-vault plugin config. Switch with the
vault switcher (`Ctrl+Shift+O` / the vault icon). Costs: `[[wikilinks]]` do not
resolve across vaults, and plugin settings are configured per vault (once each).

**Layout B — one "fleet" vault (`D:\Obsidian\` or `D:\Obsidian\<Project>\` opened
as a single vault) with the repos as subfolders.** Obsidian is happy — they're just
folders — and cross-repo wikilinks (bridge ↔ atlas docs) resolve, which is the real
attraction. But the Git plugin can then sync **at most one** of the repos (via
Custom base path — point it at `Nav-<Project>`, the only repo you actually edit).
The rest must be pulled outside Obsidian, e.g. a one-liner you run (or schedule
with Task Scheduler):

```cmd
for /d %d in ("D:\Obsidian\<Project>\*") do git -C "%~d" pull --ff-only
```
(In a `.cmd` file, double the percent signs: `%%d`.)

Practical rule: **A if you want zero moving parts; B if cross-repo links matter to
you** — B works precisely because Atlas vaults are read-only for you, so "plugin
syncs Nav, script pulls the rest" covers everything.

## 5. Desktop — Git plugin settings (per vault that has one repo)

Settings → **Git** (plugin by Vinzent03):

| Setting | Value |
|---|---|
| Vault backup interval (minutes) | `10` |
| Auto pull on startup | on |
| Pull updates on startup | on |
| Merge strategy | **merge** (not rebase — rebase isn't supported on mobile; keep both ends identical) |

For an Atlas vault (Layout A), the plugin just pulls — treat the vault as read-only;
your edits belong in the Nav vault or `_bridge/`.

Manual sync any time: `Ctrl+P` → *Git: Commit and sync*. Verify once: edit a note in
the Nav vault, sync, refresh the repo page on GitHub.

## 6. Android — GitSync

Install **GitSync** by ViscousPotential
([Play Store](https://play.google.com/store/apps/details?id=com.viscouspot.gitsync) /
[F-Droid](https://f-droid.org/en/packages/com.viscouspot.gitsync/)). Then, per repo:

1. Add the repo in GitSync (GitHub OAuth on first use).
2. Choose its clone folder — mirror the desktop layout, e.g.
   `Internal storage/Obsidian/<Project>/Nav-<Project>`.
3. **Set the tracked branch** per the table in §1 (`main` for Nav, `dev` for Atlas).
4. Enable background sync (schedule / on-app-close / widget).

Add one GitSync configuration per repo. In Obsidian for Android, open each repo
folder as a vault (Layout A), or open the parent `<Project>` folder as one vault
(Layout B — fine here too, since GitSync does the syncing per repo underneath and
doesn't care what Obsidian considers a vault).

> [!warning] Two things that look right and aren't
> **`obsidian-git` on mobile** — its own README says don't: JavaScript git fallback,
> no SSH, memory limits, no rebase. Desktop only; GitSync owns Android.
> **"GitSync Portal"** — a different, unrelated Obsidian plugin. It pushes through
> the GitHub API with no local git: no working tree, no branch, no PR. Wrong for
> anything in the fleet.

## 7. Daily use

Nothing, if intervals/background sync are set. Otherwise *Commit and sync* (desktop)
or the GitSync widget (Android) before closing. **Before editing on a second device,
let it pull first** — editing the same note on two offline devices is the one
reliable way to make a conflict. If you get one: Obsidian shows `<<<<<<<` /
`=======` / `>>>>>>>` markers in the note; delete the markers and the version you
don't want, save, commit. Nothing is lost.

## 8. Troubleshooting

- **`cd` does nothing (cmd):** changing drive needs `cd /d "D:\..."` — plain `cd`
  from `C:` silently fails.
- **Cloned the wrong branch:** `git -C Atlas-<Project> switch dev` (then set the
  branch in the plugin/GitSync too).
- **`could not prompt` / MinTTY errors from `gh` in Git Bash:** run `gh auth login`
  in cmd or PowerShell once (auth is global), or prefix `winpty`. Plain `git` is
  unaffected.
- **File over 100 MB rejected:** GitHub warns at 50 MB, refuses at 100 MB. Ignore the
  attachments folder and sync it out of band — Git LFS does **not** work through
  mobile git clients.
- **Every note modified after switching devices:** `.gitattributes` missing or added
  after the first commit (see Annex A). Add it, then `git add --renormalize .` and
  commit once.
- **Grey avatar on commits:** the commit email isn't verified on your GitHub account.

## 9. Windows cmd quirks (silent file corrupters)

- **No space before `>`** — `echo text > file` writes a trailing space; `echo text>file` doesn't.
- **Never end an echoed line with a digit** before the redirect — `echo foo2>file`
  redirects stream 2 instead of writing `foo2`.

Neither applies in Git Bash, which is a reason to prefer it.

---

## Annex A — creating a new vault repo by hand

Normally deferred: arch seats seed vaults (an `Atlas-<Project>` vault additionally
needs the io-graph with method pin + branching, dashboard markers and CI workflows
**before** the first commit — method README, "Starting a new project"). If you ever
seed a plain vault yourself:

1. Shell in the vault folder (Git Bash: right-click → *Open Git Bash here*), then
   `git init -b main`.
2. Hygiene files, **before the first commit**:

   **Git Bash / Linux**
   ```bash
   cat > .gitignore <<'EOF'
   .obsidian/workspace.json
   .obsidian/workspace-mobile.json
   .obsidian/workspace*.json
   .obsidian/cache
   .trash/
   Thumbs.db
   .DS_Store
   EOF
   printf '* text=auto eol=lf\n' > .gitattributes
   ```

   **Windows cmd**
   ```cmd
   echo .obsidian/workspace.json>.gitignore
   echo .obsidian/workspace-mobile.json>>.gitignore
   echo .obsidian/workspace*.json>>.gitignore
   echo .obsidian/cache>>.gitignore
   echo .trash/>>.gitignore
   echo Thumbs.db>>.gitignore
   echo .DS_Store>>.gitignore
   echo * text=auto eol=lf>.gitattributes
   ```

   Why: `workspace.json` changes on every click and conflicts daily if committed
   (the rest of `.obsidian/` stays versioned so plugins follow you between devices);
   `.gitattributes` forces LF so Windows and Android don't rewrite every line
   against each other. In an **Atlas vault, never ignore `registry/.compiled/`** —
   committed, published contracts (AAC-method §5).
3. Sanity-check the staged count roughly matches your note count, then commit:
   `git add -A` → `git status --short | wc -l` (cmd: `| find /c /v ""`) →
   `git commit -m "initial vault"`.
4. Push — with `gh` (creates the repo too):
   `gh repo create <org>/<Repo> --private --source=. --remote=origin --push`.
   Without `gh`: create the repo on github.com **empty** (no README/licence — else
   an unrelated-histories conflict), then `git remote add origin …` and
   `git push -u origin main`.

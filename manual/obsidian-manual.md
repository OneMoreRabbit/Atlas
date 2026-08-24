---
title: Obsidian ↔ GitHub — vault setup and daily use
interface: obsidian-manual
version: 1.0
status: active
updated: 2026-08-24
origin: generalised from Nav-AgentEco `Hardware/Obsidian/vault-github-setup.md` (1.0, 2026-08-19)
---

# Obsidian ↔ GitHub

How to put an Obsidian vault in a private GitHub repo and keep it synced across
Windows, Linux and Android. Applies to both vault classes — `Nav-<Project>` (yours)
and `Atlas-<Project>` (read-mostly) — with the differences called out.

Commands are given twice where they differ: **Git Bash / Linux** and **Windows cmd**.
Pick one and stay in it — mixing them mid-setup is where the quoting mistakes come from.

## Which vault, which branch

| Vault | You open it to | Sync branch |
|---|---|---|
| `Nav-<Project>` | think, sketch, use `_bridge/` | `main` (trunk-only) |
| `Atlas-<Project>` | read the dashboard, contracts, ADRs | **`dev`** — the work branch, where CI regenerates the dashboard. On `main` you'd read a dashboard frozen at the last release. |

> [!note] Atlas vaults are seeded by the method, not by hand
> This manual covers plain vaults. An `Atlas-<Project>` vault needs its seed
> (io-graph with method pin + branching, dashboard markers, CI workflows) **before
> the first commit** — see the method README, "Starting a new project". As the
> human you normally only **clone** Atlas vaults (§5); the seats maintain them.

---

## 1. Once per machine

Check git exists: `git --version`. If it errors on Windows, install
[Git for Windows](https://git-scm.com/download/win) — the Obsidian **Git** plugin
shells out to system git on desktop, so this is required, not optional.

Set your identity (a label on commits, not access control):

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

The email must be **verified on your GitHub account** (github.com/settings/emails)
for commits to link to you. To separate work/personal identity, set the global to
personal, then override per-repo inside an org checkout: `git config user.email
"org@example.com"` (no `--global`) — before the first commit; changing it later
doesn't rewrite history.

---

## 2. New vault → GitHub

Get a shell in the vault folder — **Git Bash:** right-click the folder → *Open Git
Bash here* (avoids every path problem below). **cmd:** `cd /d "D:\Path\To\Vault"`
(`/d` required when changing drive; quotes required with spaces).

Initialise: `git init -b main`

Create `.gitignore` and `.gitattributes` — both **before the first commit**:

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

Why: `workspace.json` is your pane layout — it changes on every click and conflicts
daily if committed (the rest of `.obsidian/` stays versioned so plugins and hotkeys
follow you between devices). `.gitattributes` forces LF — without it, Windows and
Android rewrite every line against each other and you get phantom conflicts forever.

> [!warning] Atlas vaults: never ignore `registry/.compiled/`
> In an `Atlas-<Project>` vault the compiled manifests are committed, published
> contracts (AAC-method §5). The ignore list above is for editor cruft only.

Sanity-check, then commit:

```
git add -A
git status --short | wc -l          # bash — cmd: git status --short | find /c /v ""
```

Compare the count to roughly how many notes you have; wildly higher means something
isn't ignored. Then `git commit -m "initial vault"`.

Create the remote and push — with `gh` (creates the repo too):

```
gh auth login
gh repo create <org>/Nav-<Project> --private --source=. --remote=origin --push
```

Without `gh`: create the repo on github.com **empty** (no README/licence — an
initialised repo causes an unrelated-histories conflict), then
`git remote add origin https://github.com/<org>/Nav-<Project>.git` and
`git push -u origin main`.

---

## 3. Desktop — the Obsidian Git plugin

Settings → **Git** (plugin by Vinzent03):

| Setting | Value |
|---|---|
| Vault backup interval (minutes) | `10` |
| Auto pull on startup | on |
| Pull updates on startup | on |
| Merge strategy | **merge** (not rebase — rebase isn't supported on mobile; keep both ends identical) |

Manual sync any time: `Ctrl+P` → *Git: Commit and sync*. Verify once: edit a note,
sync, refresh the repo page on GitHub.

For an **Atlas vault** the plugin still pulls fine — just make sure the checkout is
on `dev`, and treat it as read-only: your edits belong in the Nav vault or `_bridge/`.

---

## 4. Android — GitSync

Install **GitSync** by ViscousPotential
([Play Store](https://play.google.com/store/apps/details?id=com.viscouspot.gitsync) /
[F-Droid](https://f-droid.org/en/packages/com.viscouspot.gitsync/)). Authenticate
with GitHub OAuth, clone the repo to a folder, open that folder as a vault in
Obsidian. **Set the tracked branch per the table above** — `main` for Nav vaults,
`dev` for Atlas vaults.

> [!warning] Two things that look right and aren't
> **`obsidian-git` on mobile** — its own README says don't: JavaScript git fallback,
> no SSH, memory limits, no rebase. Desktop only.
> **"GitSync Portal"** — a different, unrelated plugin. It pushes through the GitHub
> API with no local git: no working tree, no branch, no PR. Fine for a lone personal
> vault; wrong for anything in the Atlas fleet.

---

## 5. Existing repo → a new machine

```
git clone https://github.com/<org>/Nav-<Project>.git
git clone --branch dev https://github.com/<org>/Atlas-<Project>.git
```

Open each folder as a vault in Obsidian. The Git plugin picks up the existing
remote — no configuration needed.

---

## 6. Daily use

Nothing, if the backup interval is set. Otherwise *Commit and sync* before closing.
**Before editing on a second device, let it pull first** — editing the same note on
two offline devices is the one reliable way to make a conflict. If you get one:
Obsidian shows `<<<<<<<` / `=======` / `>>>>>>>` markers in the note; delete the
markers and the version you don't want, save, commit. Nothing is lost.

---

## 7. Troubleshooting

- **`cd` does nothing (cmd):** changing drive needs `cd /d "D:\..."` — plain `cd`
  from `C:` silently fails.
- **`could not prompt` / MinTTY errors from `gh` in Git Bash:** run `gh auth login`
  in cmd or PowerShell once (auth is global), or prefix `winpty`. Plain `git` is
  unaffected.
- **Push rejected / "unrelated histories":** the GitHub repo wasn't created empty.
  Delete and recreate empty, or `git pull --allow-unrelated-histories origin main`.
- **File over 100 MB rejected:** GitHub warns at 50 MB, refuses at 100 MB. Ignore the
  attachments folder and sync it out of band — Git LFS does **not** work through
  mobile git clients.
- **Every note modified after switching devices:** `.gitattributes` missing or added
  after the first commit. Add it, then `git add --renormalize .` and commit once.
- **Grey avatar on commits:** the commit email isn't verified on your GitHub account
  (github.com/settings/emails). Existing commits stay unlinked.

## 8. Windows cmd quirks (silent file corrupters)

- **No space before `>`** — `echo text > file` writes a trailing space; `echo text>file` doesn't.
- **Never end an echoed line with a digit** before the redirect — `echo foo2>file`
  redirects stream 2 instead of writing `foo2`.

Neither applies in Git Bash, which is a reason to prefer it.

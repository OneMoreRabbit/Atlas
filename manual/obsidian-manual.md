---
title: Obsidian ↔ GitHub — sync setup, Windows and Android
interface: obsidian-manual
version: 1.3
status: active
updated: 2026-08-24
supersedes: 1.1
# 1.2: steps only. One Obsidian vault per repo; Git plugin configured per vault.
# 1.3: resolving a blocked push (unmerged paths) added to troubleshooting.
---

# Obsidian ↔ GitHub

One Obsidian vault per repo. The Git plugin is configured per vault.

## 1. Branch per repo

| Repo | Branch |
|---|---|
| `Nav-<Project>` | `main` |
| `Atlas-<Project>` | `dev` |

## 2. Once per machine

1. `git --version` — on Windows, if it errors install [Git for Windows](https://git-scm.com/download/win).
2. ```
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```
3. Verify that email at github.com/settings/emails.

## 3. Windows — per project

All repos live flat in `B:\_obsidian\`.

1. Open cmd:
   ```cmd
   cd /d B:\_obsidian
   git clone https://github.com/OneMoreRabbit/Nav-<Project>.git
   git clone --branch dev https://github.com/OneMoreRabbit/Atlas-<Project>.git
   ```
   (First private-repo clone opens a browser to authenticate; cached after.)
2. Verify branches:
   ```cmd
   git -C Nav-<Project> branch --show-current
   git -C Atlas-<Project> branch --show-current
   ```
   Expect `main` and `dev`.
3. In Obsidian: **Open another vault → Open folder as vault** → `Nav-<Project>`.
4. Install the **Git** plugin (by Vinzent03), enable it, then Settings → Git:

   | Setting | Value |
   |---|---|
   | Vault backup interval (minutes) | `10` |
   | Auto pull on startup | on |
   | Pull updates on startup | on |
   | Merge strategy | merge |

5. Test: edit a note → `Ctrl+P` → *Git: Commit and sync* → refresh the repo page on GitHub.
6. Repeat steps 3–4 for `Atlas-<Project>` (pull-only — don't edit there).

## 4. Android — per repo

1. Install **GitSync** by ViscousPotential ([Play Store](https://play.google.com/store/apps/details?id=com.viscouspot.gitsync) / [F-Droid](https://f-droid.org/en/packages/com.viscouspot.gitsync/)).
2. Add the repo (GitHub OAuth on first use).
3. Clone folder: `Internal storage/_obsidian/<Repo>` (mirror the Windows layout).
4. Set the branch per §1.
5. Enable background sync (schedule / on-app-close / widget).
6. In Obsidian: open the repo folder as a vault.
7. Repeat 2–6 per repo.

> [!warning]
> Do not use the `obsidian-git` plugin on mobile, and do not use the unrelated
> "GitSync Portal" plugin at all. GitSync (the Android app) only.

## 5. Daily use

- Auto-sync handles it. Manual: *Commit and sync* (desktop) / GitSync widget (Android).
- On a second device, pull before editing.
- Conflict: the note shows `<<<<<<<` / `=======` / `>>>>>>>` — delete the markers and the unwanted version, save, sync.

## 6. Troubleshooting

- **Push refused, "unmerged files" / "you have unmerged paths":** a merge stopped on a
  conflict and is half-done. In that repo folder:
  1. `git status` — read the **Unmerged paths** list (`git diff --diff-filter=U` shows the
     conflicting text).
  2. Per file, either `git checkout --theirs "<file>"` (keep the other device's version)
     or `git checkout --ours "<file>"` (keep this machine's), or edit the note and delete
     the `<<<<<<<` / `=======` / `>>>>>>>` markers and the text you don't want.
  3. `git add "<file>"` for each, then `git commit --no-edit` and `git push`.
  To back out instead and decide later: `git merge --abort` (nothing is lost).
- **`cd` does nothing (cmd):** use `cd /d B:\_obsidian` — plain `cd` doesn't change drive.
- **Wrong branch cloned:** `git -C <Repo> switch dev`, then fix the branch in the plugin/GitSync.
- **`gh` prompt errors in Git Bash:** run `gh auth login` in cmd/PowerShell once, or prefix `winpty`.
- **File over 100 MB rejected:** gitignore the attachments folder; sync it out of band (no LFS on mobile).
- **Every note modified after switching devices:** `.gitattributes` missing (Annex A) — add it, then `git add --renormalize .` and commit.
- **Grey avatar on commits:** commit email not verified on GitHub.

## 7. Windows cmd quirks

- No space before `>`: `echo text>file`, not `echo text > file`.
- Never end an echoed line with a digit before `>` (`echo foo2>file` redirects stream 2).

---

## Annex A — create a new vault repo by hand

(Normally the arch seat seeds vaults — an `Atlas-<Project>` vault needs its io-graph,
dashboard markers and CI before the first commit: method README, "Starting a new
project". These steps are for a plain vault.)

1. Shell in the vault folder (right-click → *Open Git Bash here*), then `git init -b main`.
2. Before the first commit:
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
   (Atlas vaults: never ignore `registry/.compiled/`.)
3. `git add -A` → check the staged count is sane (`git status --short | wc -l`) → `git commit -m "initial vault"`.
4. Push: `gh repo create OneMoreRabbit/<Repo> --private --source=. --remote=origin --push`
   — or create the repo on github.com **empty** (no README/licence), then
   `git remote add origin <url>` and `git push -u origin main`.

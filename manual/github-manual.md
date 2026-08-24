---
title: GitHub — repo-scoped tokens for device sync and vault CI
interface: github-manual
version: 1.1
status: active
updated: 2026-08-24
# 1.1: single PAT-creation procedure with a per-token values table (the two tokens
#   were easy to cross-configure); §4 references it.
---

# GitHub — tokens and access

Two jobs: (1) restrict Obsidian Git / GitSync to just the fleet repos instead of
account-wide OAuth; (2) set `ATLAS_ESTATE_TOKEN` so vault CI's wiring check can
reach private component repos.

## 1. Create a fine-grained PAT (same procedure for both tokens)

1. Go to **github.com/settings/personal-access-tokens/new**
   (= avatar → Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → *Generate new token*).
2. Fill in the values **for the token you are creating**:

   | Setting | `obsidian-sync` (device sync, §2–3) | `ATLAS_ESTATE_TOKEN` (vault CI, §4) |
   |---|---|---|
   | Token name | `obsidian-sync` | `atlas-estate` |
   | Resource owner | **OneMoreRabbit** | **OneMoreRabbit** |
   | Expiration | 90 days — calendar the renewal | 90 days — calendar the renewal |
   | Repository access | *Only select repositories* → every `Nav-*` and `Atlas-*` vault | *Only select repositories* → every component **code** repo (the `source:` URLs in the vaults' io-graphs) |
   | Permissions → Repository → Contents | **Read and write** | **Read-only** |

   (Metadata: Read-only is added automatically in both cases.)
3. **Generate token**; copy it now — it is shown once. Lost = regenerate, no harm.
4. If **OneMoreRabbit** is missing from the Resource owner dropdown: org Settings →
   Third-party Access → Personal access tokens → allow, then retry.

## 2. Windows — make git use the token

1. Remove the account-wide credential: Control Panel → **Credential Manager** →
   Windows Credentials → `git:https://github.com` → Remove.
2. `git -C B:\_obsidian\Nav-<Project> pull` — the Git Credential Manager window opens.
3. Choose the **Token** tab, paste the PAT.
4. Verify: the pull succeeds; the Obsidian Git plugin needs no change (it uses system git).

Access on this machine is now limited to the token's repo list.

## 3. Android — GitSync with the token

Per repo in GitSync:

1. Repo settings → authentication → **HTTPS token** (not OAuth).
2. Username: your GitHub username. Password/token: the PAT.
3. Sync once to verify.

Then revoke the old account-wide grant: github.com → Settings → **Applications** →
Authorized OAuth Apps → GitSync → **Revoke**.

## 4. `ATLAS_ESTATE_TOKEN` — vault CI wiring check

(`atlas-regen` runs the validator with `--check-wiring`, which clones each
component's `source:` repo. The workflow's built-in token can only see the vault
itself, so private component repos report "unreachable" until this is set. All
component repos public → skip this section.)

1. Create the `atlas-estate` token per §1 (right-hand column: component code repos,
   Contents **Read-only**). Copy it.
2. In **each** `Atlas-<Project>` vault repo: Settings → **Secrets and variables** →
   **Actions** → *New repository secret* → Name: `ATLAS_ESTATE_TOKEN` (exact) →
   paste → Add secret.
3. The vault's `.github/workflows/atlas-regen.yml` needs this step before the
   validator run (arch seat's edit — it ships as a comment in the template):
   ```yaml
   - run: git config --global url."https://x-access-token:${{ secrets.ATLAS_ESTATE_TOKEN }}@github.com/".insteadOf "https://github.com/"
   ```
4. Re-run: vault repo → Actions → atlas-regen → *Run workflow*. The dashboard's
   Wired column stops showing "unreachable" for private repos.

## 5. Rotation (on expiry)

1. Settings → Developer settings → Fine-grained tokens → the token → **Regenerate**.
2. Re-paste: Windows (remove credential, pull, Token tab — §2), GitSync (repo
   settings — §3), vault secrets (§4 step 2).

## 6. Troubleshooting

- **GCM never prompts / still uses the old login:** the old credential survives —
  remove `git:https://github.com` in Credential Manager and pull again.
- **403 on a specific repo:** the repo isn't in the token's repository list — edit
  the token's Repository access.
- **Wiring still "unreachable" after §4:** secret name must be exactly
  `ATLAS_ESTATE_TOKEN`; the workflow step must run before the validator; re-run the
  workflow after any edit.
- **New repo added to the fleet:** add it to the PAT's repository list (tokens don't
  auto-include new repos).

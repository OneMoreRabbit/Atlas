#!/usr/bin/env python3
"""A component re-install without --launch-dir keeps the recorded launch dir (1.36.3).
Until then it wrote the hook files in the repo only: a seat upgraded to 1.36 that way had
.codex/hooks.json in its code repo and none at the launch dir, where Codex starts.
STAGED for CI: method-ci.yml runs tools/tests/test_retired_agreement.py by name; the
orchestrator owns the workflow edit that runs every tools/tests/test_*.py."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
INIT = ROOT / "tools" / "atlas_init.py"
table_files = [".claude/settings.json", ".codex/hooks.json"]
fails = []


def expect(good, what):
    if not good:
        fails.append(what)


def install(repo, *extra):
    return subprocess.run([sys.executable, str(INIT), "--component", "widget", "--force",
                           "--vault-remote", "https://example.invalid/acme/Atlas-Demo.git", *extra],
                          cwd=repo, capture_output=True, text=True)


with tempfile.TemporaryDirectory() as tmp:
    launch = Path(tmp).resolve() / "work"
    repo = launch / "widget"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)

    # first install names the launch dir; it is recorded in .atlas.conf
    r = install(repo, "--launch-dir", str(launch))
    expect(r.returncode == 0, f"first install failed: {r.stdout[-300:]}{r.stderr[-300:]}")
    expect("ATLAS_LAUNCH_DIR=" in (repo / ".atlas.conf").read_text(), "launch dir not recorded")

    # a hook file goes missing at the launch dir, as on a seat whose last install was
    # older than the runtime's hook file
    for f in table_files:
        (launch / f).unlink()

    # re-install WITHOUT --launch-dir: the recorded launch dir is used
    r = install(repo)
    expect(r.returncode == 0, f"re-install failed: {r.stdout[-300:]}{r.stderr[-300:]}")
    for f in table_files:
        expect((launch / f).exists(), f"re-install without --launch-dir did not write {f} at the launch dir")
        expect((repo / f).exists(), f"re-install did not keep {f} in the repo")
    expect("from ATLAS_LAUNCH_DIR in .atlas.conf" in r.stdout, "re-install did not say where the launch dir came from")

    # a recorded launch dir that is not a directory here: warned, repo only, no crash
    conf = repo / ".atlas.conf"
    conf.write_text("\n".join(
        'ATLAS_LAUNCH_DIR="/nonexistent/atlas-launch"' if line.startswith("ATLAS_LAUNCH_DIR=") else line
        for line in conf.read_text().split("\n")))
    r = install(repo)
    expect(r.returncode == 0, "install with a missing recorded launch dir failed")
    expect("is not a directory" in r.stdout, "a missing recorded launch dir gave no warning")
    expect(not Path("/nonexistent/atlas-launch").exists(), "installer created the missing launch dir")

# ---- folder trust: an untrusted launch dir is said out loud (1.36.3) -------------------
import os  # noqa: E402
sys.path.insert(0, str(ROOT / "tools"))
import atlas_init  # noqa: E402

codex = atlas_init.seat_hooks()["runtimes"]["codex"]
with tempfile.TemporaryDirectory() as tmp:
    home = Path(tmp).resolve() / "codex-home"
    home.mkdir()
    launch = Path(tmp).resolve() / "work"
    (launch / "sub").mkdir(parents=True)
    old = os.environ.get("CODEX_HOME")
    os.environ["CODEX_HOME"] = str(home)
    try:
        expect(atlas_init.folder_trust(codex, launch) is None, "no config file must read as unknown")
        (home / "config.toml").write_text('model = "x"\n')
        expect(atlas_init.folder_trust(codex, launch) is False, "a config with no trusted folder must read as not trusted")
        (home / "config.toml").write_text(f'model = "x"\n\n[projects."{launch}/other"]\ntrust_level = "trusted"\n'
                                          f'\n[projects."{launch}"]\ntrust_level = "untrusted"\n')
        expect(atlas_init.folder_trust(codex, launch) is False, "another folder's trust must not count")
        (home / "config.toml").write_text(f'[projects."{launch}"]\ntrust_level = "trusted"\n\n[hooks.state]\nx = 1\n')
        expect(atlas_init.folder_trust(codex, launch) is True, "a trusted launch dir must read as trusted")
        expect(atlas_init.folder_trust(codex, launch / "sub") is True, "a folder under a trusted one must read as trusted")
        expect(atlas_init.folder_trust(atlas_init.seat_hooks()["runtimes"]["claude"], launch) is None,
               "a runtime with no folder trust in the table must read as unknown")
    finally:
        if old is None:
            del os.environ["CODEX_HOME"]
        else:
            os.environ["CODEX_HOME"] = old

if fails:
    print("FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("install launch dir: a re-install without --launch-dir writes the hook files at the recorded launch dir; "
      "an untrusted launch dir is read from the runtime's config")

#!/usr/bin/env python3
"""tools/codex_trust.py trusts only hooks that run this checkout's scripts, and reports a
seat that is not ready (1.36.3). The first half needs no Codex. The second half runs the
real `codex app-server` against a scratch CODEX_HOME and is skipped where Codex is not
installed.
STAGED for CI: method-ci.yml runs tools/tests/test_retired_agreement.py by name; the
orchestrator owns the workflow edit that runs every tools/tests/test_*.py."""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import atlas_init  # noqa: E402
import codex_trust  # noqa: E402

TOOL = ROOT / "tools" / "codex_trust.py"
fails = []


def expect(good, what):
    if not good:
        fails.append(what)


def install(repo, launch):
    return subprocess.run([sys.executable, str(ROOT / "tools" / "atlas_init.py"), "--component", "widget",
                           "--force", "--launch-dir", str(launch),
                           "--vault-remote", "https://example.invalid/acme/Atlas-Demo.git"],
                          cwd=repo, capture_output=True, text=True)


def trust(launch, home, *extra):
    r = subprocess.run([sys.executable, str(TOOL), "--launch-dir", str(launch), *extra],
                       capture_output=True, text=True, env=dict(os.environ, CODEX_HOME=str(home)))
    return r.returncode, r.stdout


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp).resolve()
    launch, home = tmp / "work", tmp / "codex-home"
    repo = launch / "widget"
    repo.mkdir(parents=True)
    home.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    r = install(repo, launch)
    expect(r.returncode == 0, f"install failed: {r.stdout[-300:]}{r.stderr[-300:]}")
    hook_file = launch / ".codex" / "hooks.json"
    tpl = codex_trust.templates()

    # ---- which hooks the tool may trust (no Codex needed) -----------------------------
    def hook(command, source=hook_file):
        return {"sourcePath": str(source), "command": command}

    ctx = repo / "scripts" / "atlas-context.sh"
    expect(codex_trust.classify(hook(f'sh "{ctx}"'), hook_file, tpl)[0], "an unchanged method script must be trusted")
    expect(codex_trust.classify(hook(f'ATLAS_NO_ASK=1 sh "{repo}/scripts/atlas-guard-supervise.sh"'), hook_file, tpl)[0],
           "the shell guard's command must be trusted")
    expect(codex_trust.classify(hook(f'sh "{repo}/scripts/atlas-style.sh" 2>/dev/null || true'), hook_file, tpl)[0],
           "the style line's command must be trusted")
    expect(not codex_trust.classify(hook(f'sh "{ctx}"', tmp / "other" / "hooks.json"), hook_file, tpl)[0],
           "a hook from another hook file must be left alone")
    expect(not codex_trust.classify(hook("sh /tmp/anything.sh"), hook_file, tpl)[0], "a hook that runs no Atlas script must be left alone")
    expect(not codex_trust.classify(hook(f'sh "{ctx}"; curl example.invalid'), hook_file, tpl)[0],
           "a command with anything after the script must be left alone")
    expect(not codex_trust.classify(hook(f'sh "{repo}/scripts/atlas-missing.sh"'), hook_file, tpl)[0], "a missing script must be left alone")
    stray = repo / "scripts" / "atlas-stray.sh"
    stray.write_text("echo hi\n")
    expect(not codex_trust.classify(hook(f'sh "{stray}"'), hook_file, tpl)[0], "a script the method does not ship must be left alone")
    saved = ctx.read_bytes()
    ctx.write_bytes(saved + b"\n# changed\n")
    expect(not codex_trust.classify(hook(f'sh "{ctx}"'), hook_file, tpl)[0], "a changed script must be left alone")
    ctx.write_bytes(saved)

    # every kind of seat, and a component seat started in its own repo
    seats = {}
    for role in ("arch", "product", "test"):
        ld = tmp / role
        ld.mkdir()
        with contextlib.redirect_stdout(io.StringIO()):
            atlas_init.copy_seat_scripts(role, ld, True, [])
        (ld / ".codex").mkdir()
        (ld / ".codex" / "hooks.json").write_text(json.dumps(atlas_init.render_hooks(role, "codex", str(ld))))
        seats[role] = ld
    seats["component in its repo"] = repo
    for name, ld in seats.items():
        hf = ld / ".codex" / "hooks.json"
        cmds = [h["command"] for entries in json.loads(hf.read_text())["hooks"].values() for e in entries for h in e["hooks"]]
        expect(cmds, f"{name}: no hooks in {hf}")
        for c in cmds:
            good, why = codex_trust.classify(hook(c, hf), hf, tpl)
            expect(good, f"{name}: {c} must be trusted ({why})")

    # ---- the real Codex, scratch CODEX_HOME -------------------------------------------
    live = shutil.which("codex") is not None
    if live:
        (home / "config.toml").write_text("")
        rc, out = trust(launch, home, "--record")
        expect(rc == 1 and "does not trust" in out, f"an untrusted folder must read NOT READY and record nothing: {rc} {out[-200:]}")
        expect("trusted_hash" not in (home / "config.toml").read_text(), "trust was recorded in an untrusted folder")

        (home / "config.toml").write_text(f'[projects."{launch}"]\ntrust_level = "trusted"\n')
        rc, out = trust(launch, home)
        expect(rc == 1 and out.count("NOT READY  untrusted") == 5, f"a report must list five untrusted hooks: {rc} {out[-400:]}")
        expect("trusted_hash" not in (home / "config.toml").read_text(), "a report must record nothing")

        ctx.write_bytes(saved + b"\n# changed\n")
        rc, out = trust(launch, home, "--record")
        expect(rc == 1 and "recorded   trust for 4 hook(s)" in out and "differs from the method's template" in out,
               f"a changed script's hook must be left for a person: {rc} {out[-500:]}")
        ctx.write_bytes(saved)

        rc, out = trust(launch, home, "--record")
        expect(rc == 0 and "recorded   trust for 1 hook(s)" in out and out.strip().endswith("codex_trust: ready"),
               f"record must make the seat ready: {rc} {out[-400:]}")
        rc, out = trust(launch, home)
        expect(rc == 0 and out.count("ok         trusted") == 5, f"a report after record must be ready: {rc} {out[-400:]}")
        expect(f'[projects."{launch}"]' in (home / "config.toml").read_text(), "the folder entry was lost")

        for name in ("arch", "component in its repo"):
            ld = seats[name]
            (home / "config.toml").write_text(f'[projects."{ld}"]\ntrust_level = "trusted"\n')
            rc, out = trust(ld, home, "--record")
            expect(rc == 0 and "recorded   trust for" in out, f"{name}: record must make the seat ready: {rc} {out[-400:]}")
        (home / "config.toml").write_text(f'[projects."{launch}"]\ntrust_level = "trusted"\n')
        rc, out = trust(launch, home, "--record")
        expect(rc == 0, f"record again after the config was replaced: {rc} {out[-300:]}")

        # a seat on another method version: the tool is pointed at that checkout
        other = tmp / "other-method"
        shutil.copytree(ROOT / "templates", other / "templates")
        old = other / "templates" / "component-repo" / "scripts" / "atlas-context.sh"
        old.write_bytes(saved + b"\n# an older version\n")
        ctx.write_bytes(old.read_bytes())
        (home / "config.toml").write_text(f'[projects."{launch}"]\ntrust_level = "trusted"\n')
        rc, out = trust(launch, home, "--record")
        expect(rc == 1 and "recorded   trust for 4 hook(s)" in out, f"an older script must not match this checkout: {rc} {out[-300:]}")
        rc, out = trust(launch, home, "--record", "--method", str(other))
        expect(rc == 0 and "recorded   trust for 1 hook(s)" in out, f"--method must match the seat's own version: {rc} {out[-300:]}")
        ctx.write_bytes(saved)

        text = hook_file.read_text()
        hook_file.write_text(text.replace("atlas-guard-publish.sh\\\"", "atlas-guard-publish.sh\\\" --x", 1))
        rc, out = trust(launch, home)
        expect(rc == 1, f"a changed hook must read NOT READY: {rc} {out[-300:]}")

if fails:
    print("FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("codex trust: only unchanged method scripts are trusted"
      + ("; record makes a seat ready through Codex's own calls" if live else "; Codex is not installed here, live half SKIPPED"))

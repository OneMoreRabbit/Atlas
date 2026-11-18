#!/usr/bin/env python3
"""Codex trust for the Atlas hooks at a seat's launch dir, without a person (1.36.3).

    python3 tools/codex_trust.py --launch-dir <launch dir>            # report
    python3 tools/codex_trust.py --launch-dir <launch dir> --record   # trust, then report

Codex reads `.codex/hooks.json` only in a trusted folder and skips a new or changed hook
until the hook is trusted. It gives no warning for either. A seat started by the seat tool
is never asked, so in the 1.36 rollout the operator did both by hand at every Codex seat.

This tool asks Codex itself: `hooks/list` for what it sees, `config/batchWrite` to record
trust. That is what Codex's own `/hooks` screen does, so Codex stays the one writer of its
config. Folder trust is seat provisioning's and is only reported here.

`--record` trusts a hook only when it is in `<launch dir>/.codex/hooks.json` and runs a
script that is byte for byte a template in the method checkout. Any other hook is left for
a person. `--method <checkout>` names the checkout the seat's scripts were copied from,
when that is not the one this tool runs from.

Exit 0: the folder is trusted and every Atlas hook there is trusted. Exit 1: not ready,
the lines say why. Exit 2: Codex could not be asked.

After a `--record`, restart every session on the seat from a shell outside the session:
a running session keeps the hooks it started with.
"""
from __future__ import annotations

import argparse
import json
import re
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import atlas_init  # noqa: E402

RUNTIME = "codex"
ATLAS_CMD = re.compile(r'^(?:[A-Z_]+=\S+ )*sh "([^"]+/(atlas-[a-z-]+\.sh))"(?: 2>/dev/null \|\| true)?$')


def templates(method: Path = atlas_init.TEMPLATES.parent.parent) -> dict:
    """Script name -> the templates of that name in a method checkout."""
    out = {}
    for f in sorted((method / "templates").rglob("atlas-*.sh")):
        out.setdefault(f.name, []).append(f)
    return out


def classify(hook: dict, hook_file: Path, tpl: dict) -> tuple:
    """(is an Atlas hook this tool may trust, why not)."""
    if Path(hook.get("sourcePath", "")) != hook_file:
        return False, "not from the launch dir's hook file"
    # a hook file inside a repo spells the repo root as an expression; it is the folder
    # the hook file's `.codex/` sits in
    m = ATLAS_CMD.match(atlas_init.resolve_cmd(hook.get("command", ""), hook_file.parent.parent))
    if not m:
        return False, "does not run an Atlas script"
    script = Path(m.group(1))
    if not script.is_file():
        return False, f"{script} is missing"
    body = script.read_bytes()
    if not any(t.is_file() and t.read_bytes() == body for t in tpl.get(m.group(2), [])):
        return False, f"{script} differs from the method's template"
    return True, ""


class Codex:
    """One `codex app-server` over stdio."""

    def __init__(self, binary: str, cwd: Path):
        self.p = subprocess.Popen([binary, "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, cwd=str(cwd), text=True)
        self.n = 0
        self.call("initialize", {"clientInfo": {"name": "atlas-codex-trust", "version": "1"},
                                 "capabilities": {"experimentalApi": True}})
        self.send({"method": "initialized"})

    def send(self, obj: dict) -> None:
        self.p.stdin.write(json.dumps(obj) + "\n")
        self.p.stdin.flush()

    def call(self, method: str, params: dict, timeout: int = 30) -> dict:
        self.n += 1
        self.send({"id": self.n, "method": method, "params": params})
        end = time.time() + timeout
        while time.time() < end:
            ready, _, _ = select.select([self.p.stdout], [], [], 1)
            if not ready:
                continue
            line = self.p.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {json.dumps(msg['error'])[:300]}")
                return msg["result"]
        raise RuntimeError(f"{method}: no answer from codex app-server in {timeout}s")

    def hooks(self, cwd: Path) -> list:
        return self.call("hooks/list", {"cwds": [str(cwd)]})["data"][0]["hooks"]

    def close(self) -> None:
        self.p.kill()
        self.p.wait()


def main() -> int:
    ap = argparse.ArgumentParser(description="Report, or record, Codex trust for the Atlas hooks at a launch dir.")
    ap.add_argument("--launch-dir", required=True)
    ap.add_argument("--record", action="store_true",
                    help="trust the hooks that run this method checkout's scripts")
    ap.add_argument("--method", default=str(atlas_init.TEMPLATES.parent.parent),
                    help="the method checkout the seat's scripts were copied from (default: this one)")
    ap.add_argument("--codex", default=RUNTIME, help="the Codex binary (default: codex on PATH)")
    args = ap.parse_args()

    launch = Path(args.launch_dir).expanduser().resolve()
    rt = atlas_init.seat_hooks()["runtimes"][RUNTIME]
    hook_file = launch / rt["file"]
    print(f"codex_trust: launch dir {launch}")
    if not hook_file.is_file():
        print(f"  NOT READY  {hook_file} is missing: run atlas_init.py for this seat first")
        return 1
    binary = shutil.which(args.codex)
    if not binary:
        print(f"  CANNOT ASK  no `{args.codex}` on PATH")
        return 2
    folder = atlas_init.folder_trust(rt, launch)
    if folder is not True:
        print(f"  NOT READY  Codex does not trust {launch}, so it reads no hook file there. "
              "Folder trust is seat provisioning's; nothing recorded.")
        return 1
    print("  ok         the folder is trusted")

    method = Path(args.method).expanduser().resolve()
    tpl = templates(method)
    if not tpl:
        print(f"  CANNOT ASK  no script templates under {method}/templates")
        return 2
    try:
        cx = Codex(binary, launch)
    except (OSError, RuntimeError) as e:
        print(f"  CANNOT ASK  {e}")
        return 2
    try:
        hooks = cx.hooks(launch)
        mine = [(h, *classify(h, hook_file, tpl)) for h in hooks if Path(h.get("sourcePath", "")) == hook_file]
        if args.record:
            edits = [{"keyPath": "hooks.state." + json.dumps(h["key"]) + ".trusted_hash",
                      "value": h["currentHash"], "mergeStrategy": "upsert"}
                     for h, good, _ in mine if good and h["trustStatus"] != "trusted"]
            if edits:
                cx.call("config/batchWrite", {"edits": edits})
                print(f"  recorded   trust for {len(edits)} hook(s). Restart every session on this seat "
                      "from a shell outside the session.")
                hooks = cx.hooks(launch)
                mine = [(h, *classify(h, hook_file, tpl)) for h in hooks if Path(h.get("sourcePath", "")) == hook_file]
    except RuntimeError as e:
        print(f"  CANNOT ASK  {e}")
        return 2
    finally:
        cx.close()

    ready = bool(mine)
    if not mine:
        print(f"  NOT READY  Codex lists no hook from {hook_file}")
    for h, good, why in mine:
        what = f"{h['eventName']}{' ' + h['matcher'] if h.get('matcher') else ''}: {h['command']}"
        if h["trustStatus"] == "trusted" and h.get("enabled", True):
            print(f"  ok         trusted  {what}")
        else:
            ready = False
            state = h["trustStatus"] if h.get("enabled", True) else "switched off"
            left = f" Left for a person: {why}." if (args.record and not good) else ""
            print(f"  NOT READY  {state}  {what}.{left}")
    print("codex_trust: " + ("ready" if ready else "NOT READY"))
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())

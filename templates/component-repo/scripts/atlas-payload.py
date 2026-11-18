#!/usr/bin/env python3
"""atlas-payload — which files does this write-hook payload write?

Reads the hook payload (JSON) on stdin. Prints one line per file written: the
absolute path, a tab, and the `to:` value found in the added text (may be empty).
Prints __ATLAS_PARSE_ERROR__ when it cannot say; the write guards refuse on that.

Two payload shapes are known:
  a path field   tool_input.file_path or tool_input.notebook_path  (Claude Code)
  a patch        tool_input.command holding "*** Begin Patch" text; one patch can
                 write several files                               (Codex apply_patch)
A runtime with another shape gets one more branch here (context-plane.md,
"Runtimes"). Stdlib only.
"""
import json
import os
import posixpath
import re
import sys

ERR = "__ATLAS_PARSE_ERROR__"
TO = re.compile(r"^(?:to|addressed-to|addressed_to):\s*(.+)$", re.M)
PATCH_FILE = re.compile(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+?)\s*$")


def to_value(text):
    m = TO.search(text)
    return m.group(1).strip() if m else ""


def patch_files(text):
    """[(path, added text)] for every file a patch adds, updates, deletes or moves to."""
    files = []
    for line in text.split("\n"):
        m = PATCH_FILE.match(line)
        if m:
            files.append([m.group(1), []])
        elif files and line.startswith("+"):
            files[-1][1].append(line[1:])
    return [(p, "\n".join(added)) for p, added in files]


def written(payload):
    ti = payload.get("tool_input")
    if isinstance(ti, str):
        ti = {"command": ti}
    if not isinstance(ti, dict):
        return []
    path = ti.get("file_path") or ti.get("notebook_path")
    if path:
        return [(str(path), str(ti.get("content") or ti.get("new_string") or ""))]
    cmd = ti.get("command")
    if isinstance(cmd, list):
        cmd = "\n".join(str(c) for c in cmd)
    if isinstance(cmd, str) and "*** Begin Patch" in cmd:
        return patch_files(cmd.replace("\r", ""))
    return []


def absolute(path, cwd):
    # Windows paths arrive with backslashes; an unnormalised path would match no vault
    path = path.replace("\\", "/")
    if not (path.startswith("/") or re.match(r"^[A-Za-z]:/", path)):
        path = cwd.replace("\\", "/").rstrip("/") + "/" + path
    return posixpath.normpath(path)


def main():
    try:
        payload = json.load(sys.stdin)
        files = written(payload)
        if not files:
            raise ValueError("no written file found in the payload")
        cwd = str(payload.get("cwd") or os.getcwd())
        lines = []
        for path, text in files:
            path, to = absolute(path, cwd), to_value(text.replace("\r", ""))
            if re.search(r"[\t\n]", path + to):
                raise ValueError("tab or newline in a path")
            lines.append(path + "\t" + to)
    except Exception:
        print(ERR)
        return
    print("\n".join(lines))


if __name__ == "__main__":
    main()

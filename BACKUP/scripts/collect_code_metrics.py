"""Coleta métricas simples do código: contagens de TODOs, prints, eval/exec, shell=True, pdb e possíveis segredos."""

import os
import re

root = "."
ignore_dirs = ("venv", ".git")
patterns = {
    "todo": re.compile(r"\b(TODO|FIXME|HACK|XXX|BUG)\b", re.I),
    "print": re.compile(r"\bprint\s*\("),
    "eval_exec": re.compile(r"\b(eval|exec)\s*\("),
    "shell_true": re.compile(r"shell\s*=\s*True"),
    "pdb": re.compile(r"pdb\.set_trace"),
    "secrets": re.compile(
        r"password\s*=|secret\s*=|api[_-]?key|AKIA[0-9A-Z]{16}", re.I
    ),
}
counts = {k: 0 for k in patterns}
files_checked = 0

for dirpath, dirs, files in os.walk(root):
    if any(x in dirpath for x in ignore_dirs):
        continue
    for fn in files:
        if not fn.endswith(".py"):
            continue
        files_checked += 1
        p = os.path.join(dirpath, fn)
        try:
            s = open(p, "r", encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        for k, pat in patterns.items():
            counts[k] += len(pat.findall(s))

print(f"files:{files_checked}")
for k, v in counts.items():
    print(f"{k}:{v}")

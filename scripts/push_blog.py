#!/usr/bin/env python3
"""Commit + push all changes to GitHub Pages repo.

Reads token from .github_token.txt (gitignored). Safe: only runs
after batch_books.py generated new PDFs. No secrets printed.
"""
from pathlib import Path
import subprocess, sys

BASE = Path(__file__).resolve().parent.parent
TOK = (BASE / ".github_token.txt").read_text().strip()
REPO = "Prosorainc/prosora-blog"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[push] FAIL: {r.stderr[-200:]}")
        sys.exit(1)
    return r.stdout.strip()


if __name__ == "__main__":
    # check if there is anything to commit
    st = subprocess.run(["git", "-C", str(BASE), "status", "--porcelain"],
                         capture_output=True, text=True).stdout.strip()
    if not st:
        print("[push] nothing to commit")
        sys.exit(0)
    run(["git", "-C", str(BASE), "add", "-A"])
    run(["git", "-C", str(BASE), "commit", "-q", "-m", "Auto: new book PDFs + site update"])
    run(["git", "-C", str(BASE), "remote", "set-url", "origin",
         f"https://{TOK}@github.com/{REPO}.git"])
    run(["git", "-C", str(BASE), "push", "-q", "origin", "main"])
    print("[push] pushed to GitHub Pages")

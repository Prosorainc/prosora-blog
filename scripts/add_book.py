#!/usr/bin/env python3
"""Add a new book to the Prosora blog.

Generates the PDF (if missing) and (re)builds the book DATA arrays in
index.html and books.html from the local pdf/ folder, so pagination and
"first 6 on home" stay correct automatically. No hardcoded cards.

Usage:
  python3 add_book.py "The Psychology of Money" "Morgan Housel"
"""
import sys, subprocess, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
VENV = BASE / ".venv" / "bin" / "activate"


def _books():
    """Scan pdf/ for book PDFs, return list of (title, author, file)."""
    out = []
    for pdf in sorted(BASE.glob("pdf/*.pdf")):
        fn = pdf.stem  # e.g. The_4-Hour_Workweek
        # find author: best-effort from known mapping; fallback blank
        out.append(fn)
    return out


def _author_for(title):
    # simple known-author map (extend as needed)
    m = {
        "Atomic_Habits": "James Clear",
        "The_Psychology_of_Money": "Morgan Housel",
        "Rich_Dad_Poor_Dad": "Robert Kiyosaki",
        "The_4-Hour_Workweek": "Timothy Ferriss",
        "The_Simple_Path_to_Wealth": "JL Collins",
        "The_Psychology_of_Human_Misjudgment": "Charlie Munger",
        "The_E-Myth_Revisited": "Michael Gerber",
        "The_Total_Money_Makeover": "Dave Ramsey",
        "Think_and_Grow_Rich": "Napoleon Hill",
        "The_Millionaire_Next_Door": "Thomas J. Stanley",
    }
    return m.get(title, "")


def _data_js():
    lines = []
    for fn in _books():
        t = fn.replace("_", " ")
        a = _author_for(fn)
        lines.append(f'  {{t:"{t}", a:"{a}", f:"{fn}"}},')
    return "\n".join(lines)


def main():
    if len(sys.argv) >= 3:
        title, author = sys.argv[1], sys.argv[2]
        # 1. generate PDF if missing
        fn = title.replace(" ", "_")
        pdf = BASE / "pdf" / f"{fn}.pdf"
        if not pdf.exists():
            subprocess.run(f"bash -c 'source {VENV} && python3 scripts/gen_pdf.py \"{title}\" \"{author}\"'",
                           shell=True, cwd=str(BASE))
            if not pdf.exists():
                print("PDF gen failed"); sys.exit(1)
        # remember author for future scans
        _remembrance(title, author)
    # 2. rebuild data arrays in both pages
    data = _data_js()
    for page in ("index.html", "books.html"):
        p = BASE / page
        html = p.read_text()
        import re
        html = re.sub(r"<!-- BOOKS_DATA -->.*?<!-- /BOOKS_DATA -->",
                       f"<!-- BOOKS_DATA -->\n{data}\n  <!-- /BOOKS_DATA -->", html, flags=re.DOTALL)
        p.write_text(html)
    print(f"[site] rebuilt book data: {len(_books())} books in {', '.join(_books()[:3])}...")


def _remembrance(title, author):
    """Store author mapping persistently (used by _author_for)."""
    m = {
        "Atomic_Habits": "James Clear",
        "The_Psychology_of_Money": "Morgan Housel",
        "Rich_Dad_Poor_Dad": "Robert Kiyosaki",
        "The_4-Hour_Workweek": "Timothy Ferriss",
        "The_Simple_Path_to_Wealth": "JL Collins",
        "The_Psychology_of_Human_Misjudgment": "Charlie Munger",
        "The_E-Myth_Revisited": "Michael Gerber",
        "The_Total_Money_Makeover": "Dave Ramsey",
        "Think_and_Grow_Rich": "Napoleon Hill",
        "The_Millionaire_Next_Door": "Thomas J. Stanley",
    }
    fn = title.replace(" ", "_")
    if fn not in m:
        m[fn] = author
        # rewrite this function's map by patching the source (simple, local)
        src = Path(__file__).read_text()
        src = src.replace(
            '        "The_Millionaire_Next_Door": "Thomas J. Stanley",\n',
            f'        "The_Millionaire_Next_Door": "Thomas J. Stanley",\n        "{fn}": "{author}",\n')
        Path(__file__).write_text(src)


if __name__ == "__main__":
    main()

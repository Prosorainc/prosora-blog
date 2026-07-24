#!/usr/bin/env python3
"""Add a new book: generate PDF + inject card into site/index.html.

Usage:
  python3 add_book.py "The Psychology of Money" "Morgan Housel"
"""
import sys, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SITE = BASE / "site" / "index.html"
VENV = BASE / ".venv" / "bin" / "activate"


def main():
    if len(sys.argv) < 3:
        print("Usage: add_book.py <title> <author>"); sys.exit(1)
    title, author = sys.argv[1], sys.argv[2]
    # 1. generate PDF
    subprocess.run(f"bash -c 'source {VENV} && python3 scripts/gen_pdf.py \"{title}\" \"{author}\"'",
                   shell=True, cwd=str(BASE))
    pdf = BASE / "pdf" / f"{title.replace(' ', '_')}.pdf"
    if not pdf.exists():
        print("PDF gen failed"); sys.exit(1)
    # 2. inject card
    html = SITE.read_text()
    card = (f'    <div class="book-card">\n'
            f'      <div class="book-icon">📘</div>\n'
            f'      <h3>{title}</h3>\n'
            f'      <div class="author">by {author}</div>\n'
            f'      <div class="desc">Free Prosora deep summary. Click to download the PDF.</div>\n'
            f'      <a class="dl-btn" href="pdf/{title.replace(" ", "_")}.pdf">Download PDF</a>\n'
            f'    </div>\n')
    marker = "<!-- BOOKS_END -->"
    if marker in html:
        html = html.replace(marker, card + "  " + marker, 1)
        SITE.write_text(html)
        print(f"[site] added card for {title}")
    else:
        print("[site] marker not found, skip inject")
    print(f"[done] {title} ready at pdf/{title.replace(' ', '_')}.pdf")


if __name__ == "__main__":
    main()

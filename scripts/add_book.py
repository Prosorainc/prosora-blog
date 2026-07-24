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
    # 2. inject card into index.html and books.html
    fn = title.replace(" ", "_")
    card = (f'    <div class="book-card">\n'
            f'      <div class="book-icon">📘</div>\n'
            f'      <h3>{title}</h3>\n'
            f'      <div class="author">by {author}</div>\n'
            f'      <div class="desc">Free Prosora deep summary. Click to download the PDF.</div>\n'
            f'      <div class="btn-row">\n'
            f'        <button class="btn" onclick="preview(\'pdf/{fn}.pdf\')">Preview</button>\n'
            f'        <a class="btn ghost" href="pdf/{fn}.pdf" download>Download</a>\n'
            f'      </div>\n'
            f'    </div>\n')
    marker = "<!-- BOOKS_END -->"
    changed = False
    for page in ("index.html", "books.html"):
        p = BASE / "site" / page
        html = p.read_text()
        if marker in html and card.strip() not in html:
            html = html.replace(marker, card + "  " + marker, 1)
            p.write_text(html)
            changed = True
    if changed:
        print(f"[site] added card to index + books")
    else:
        print("[site] card already present, skip")
    print(f"[done] {title} ready at pdf/{title.replace(' ', '_')}.pdf")


if __name__ == "__main__":
    main()

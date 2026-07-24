#!/usr/bin/env python3
"""Generate a FREE summary PDF for a wealth/personal-finance book.

Uses Gemma 4 (OpenRouter, free) to draft a structured summary, then renders
to PDF with reportlab. PDF is shared free; contains an affiliate link slot
(placeholder, fill later). No book text copied — summary only (fair use).

Usage:
  python3 gen_pdf.py "Atomic Habits" "James Clear"
"""
import sys, json, subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE = Path(__file__).resolve().parent.parent
KEY = (BASE / "openrouter_key.txt").read_text().strip() if (BASE/"openrouter_key.txt").exists() else None
# fallback to prosora key
if not KEY:
    PK = Path("/home/ubuntu/prosora/openrouter_key.txt")
    if PK.exists():
        KEY = PK.read_text().strip()
AFF_LINK = "▶ INSERT_AFFILIATE_LINK_HERE"  # placeholder
WIB = timezone(timedelta(hours=7))


def _draft(title, author):
    prompt = (
        f"Write a concise, high-value SUMMARY of the book '{title}' by {author}. "
        "Personal-finance / wealth / self-improvement genre. Structure:\n"
        "1. One-line core thesis\n"
        "2. Key Lessons (5-7 bullet points, each with a short actionable takeaway)\n"
        "3. Most quoted / powerful insight\n"
        "4. Who should read it & why\n"
        "Keep it ORIGINAL (do not copy book text). Plain text, no markdown headers. "
        "Max 400 words."
    )
    import requests
    r = requests.post("https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json={"model": "google/gemma-4-26b-a4b-it:free",
              "messages": [
                  {"role": "system", "content": "You summarize books into actionable wealth insights."},
                  {"role": "user", "content": prompt}]},
        timeout=120)
    return r.json()["choices"][0]["message"]["content"].strip()


def _render(title, author, body):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    out = BASE / "pdf" / f"{title.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    ss = getSampleStyleSheet()
    gold = HexColor("#D4AF37")
    h = ParagraphStyle("h", parent=ss["Title"], textColor=gold, fontSize=22)
    sub = ParagraphStyle("sub", parent=ss["Normal"], textColor=HexColor("#555555"), fontSize=11)
    body_st = ParagraphStyle("body", parent=ss["Normal"], fontSize=11, leading=16, spaceAfter=6)
    el = []
    el.append(Paragraph(f"📘 {title}", h))
    el.append(Paragraph(f"by {author} — Prosora Free Summary", sub))
    el.append(Spacer(1, 0.3*cm))
    el.append(HRFlowable(width="100%", color=gold, thickness=1.5))
    el.append(Spacer(1, 0.4*cm))
    for line in body.split("\n"):
        line = line.strip()
        if not line:
            continue
        el.append(Paragraph(line.replace("&", "&amp;"), body_st))
    el.append(Spacer(1, 0.5*cm))
    el.append(HRFlowable(width="100%", color=gold, thickness=1))
    el.append(Paragraph(f"🔗 Get the book (affiliate): {AFF_LINK}", sub))
    el.append(Paragraph("Prosora — wealth & self-improvement. Turn knowledge into wealth.", sub))
    doc.build(el)
    return out


def main():
    if len(sys.argv) < 3:
        print("Usage: gen_pdf.py <title> <author>"); sys.exit(1)
    title, author = sys.argv[1], sys.argv[2]
    print(f"[gen] drafting '{title}'...")
    body = _draft(title, author)
    out = _render(title, author, body)
    # save markdown too
    (BASE / "content" / f"{title.replace(' ', '_')}.md").write_text(
        f"# {title} — {author}\n\n{body}\n\n---\nAffiliate: {AFF_LINK}\n")
    print(f"[gen] PDF ready: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

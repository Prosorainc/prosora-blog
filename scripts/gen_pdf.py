#!/usr/bin/env python3
"""Generate a FREE summary PDF for a wealth/personal-finance book.

Uses Gemma 4 (OpenRouter, free) to draft a DEEP, structured summary
(min ~5 pages), then renders to PDF with reportlab. PDF is shared free.
No book text copied — original analysis only (fair use).

Usage:
  python3 gen_pdf.py "Atomic Habits" "James Clear"
"""
import sys, json, re
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE = Path(__file__).resolve().parent.parent
KEY = (BASE / "gemini_key.txt").read_text().strip() if (BASE/"gemini_key.txt").exists() else None
if not KEY:
    PK = Path("/home/ubuntu/prosora/gemini_key.txt")
    if PK.exists():
        KEY = PK.read_text().strip()
MODEL = "gemini-flash-lite-latest"  # active free tier, higher daily quota than 3.x-flash
WIB = timezone(timedelta(hours=7))


def _draft(title, author):
    prompt = (
        f"Write a DEEP, original book summary of '{title}' by {author} "
        "(personal-finance / wealth / self-improvement). Goal: a reader should "
        "finish it understanding the book's REAL meaning, not just surface tips.\n\n"
        "Structure with markdown headers and write SUBSTANTIVE content "
        "(target 2000-2600 words total). Each lesson must explain the WHY and "
        "the underlying principle, not just the tip.\n\n"
        "Format exactly:\n"
        "## Core Thesis\n"
        "(2-3 sentences: the central idea and why it flips conventional thinking)\n\n"
        "## Why This Book Matters\n"
        "(what problem it solves, who it challenges, the shift in mindset)\n\n"
        "## Key Lessons\n"
        "For each (write 8-10 lessons):\n"
        "**Lesson N: <short title>**\n"
        "<2-4 sentences explaining the real meaning, the mechanism, and a "
        "concrete example. Then a line: *Takeaway: <one actionable step>.*\n\n"
        "## Powerful Quotes\n"
        "- <quote> — <one line on what it really means>\n"
        "(give 4-5)\n\n"
        "## Myths This Book Destroys\n"
        "- <common belief> → <what the book reveals instead>\n"
        "(give 3-4)\n\n"
        "## 30-Day Action Plan\n"
        "- Week 1: <specific actions>\n"
        "- Week 2: <specific actions>\n"
        "- Week 3: <specific actions>\n"
        "- Week 4: <specific actions>\n\n"
        "## Who Should Read This\n"
        "(2-3 sentences on the ideal reader and the outcome they'll get)\n\n"
        "## Reflection Questions\n"
        "- <question to help the reader internalize the book>\n"
        "(give 4-5)\n\n"
        "## Final Word\n"
        "(1 punchy closing paragraph tying it to financial freedom)\n\n"
        "Write ORIGINAL analysis. Do not copy book sentences. Plain readable text."
    )
    try:
        import google.generativeai as genai
        genai.configure(api_key=KEY)
        m = genai.GenerativeModel(MODEL)
        resp = m.generate_content(
            [ {"role": "user",
               "parts": ["You write deep, original book summaries that reveal real meaning, not surface tips.\n\n" + prompt]} ],
            generation_config={"temperature": 0.7, "max_output_tokens": 8192})
        return resp.text.strip()
    except ImportError:
        # fallback: raw REST if SDK missing
        import requests
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}",
            json={"contents":[{"parts":[{"text": prompt}]}],"generationConfig":{"temperature":0.7,"maxOutputTokens":8192}},
            timeout=180)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def _render(title, author, body):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    HRFlowable, ListFlowable, ListItem)
    safe = title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    out = BASE / "pdf" / f"{safe}.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm,
                            title=f"{title} — Prosora Summary")
    ss = getSampleStyleSheet()
    gold = HexColor("#D4AF37")
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=gold, fontSize=22, spaceAfter=4)
    sub = ParagraphStyle("sub", parent=ss["Normal"], textColor=HexColor("#666666"), fontSize=11, spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=gold, fontSize=14,
                        spaceBefore=12, spaceAfter=4)
    body_st = ParagraphStyle("body", parent=ss["Normal"], fontSize=11.5, leading=17, spaceAfter=7)
    bold_st = ParagraphStyle("bold", parent=body_st, fontName="Helvetica-Bold", textColor=HexColor("#222222"))
    bullet_st = ParagraphStyle("bul", parent=body_st, leftIndent=10, spaceAfter=5)
    el = []
    el.append(Paragraph(f"📘 {title}", h1))
    el.append(Paragraph(f"by {author} — Prosora Free Summary", sub))
    el.append(HRFlowable(width="100%", color=gold, thickness=1.5))
    el.append(Spacer(1, 0.3*cm))

    def esc(t):
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    for raw in body.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("## "):
            el.append(Paragraph(esc(line[3:].upper()), h2))
        elif line.startswith("**") and "**" in line[2:]:
            m = re.match(r"\*\*(.+?)\*\*", line)
            el.append(Paragraph(esc(m.group(1)), bold_st))
            rest = line[m.end():].strip()
            if rest:
                el.append(Paragraph(esc(rest), body_st))
        elif line.startswith("- "):
            el.append(Paragraph("• " + esc(line[2:]), bullet_st))
        else:
            el.append(Paragraph(esc(line), body_st))
    el.append(Spacer(1, 0.4*cm))
    el.append(HRFlowable(width="100%", color=gold, thickness=1))
    el.append(Paragraph("Prosora — wealth &amp; self-improvement. Turn knowledge into wealth.", sub))
    doc.build(el)
    return out


def main():
    if len(sys.argv) < 3:
        print("Usage: gen_pdf.py <title> <author>"); sys.exit(1)
    title, author = sys.argv[1], sys.argv[2]
    safe = title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    print(f"[gen] drafting '{title}' (deep)...")
    body = _draft(title, author)
    out = _render(title, author, body)
    (BASE / "content" / f"{safe}.md").write_text(
        f"# {title} — {author}\n\n{body}\n")
    print(f"[gen] PDF ready: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

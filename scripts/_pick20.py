#!/usr/bin/env python3
from pathlib import Path

BASE = Path("/home/ubuntu/affiliate-blog")
pdf_dir = BASE / "pdf"

existing = {p.stem.lower() for p in pdf_dir.glob("*.pdf")}

def norm(title):
    return title.replace(" ", "_").replace("/", "_").replace("\\", "_").lower()

candidates = [
    ("The Millionaire Women Next Door", "Thomas J. Stanley"),
    ("The Next Millionaire Next Door", "Sarah Stanley Fallaw"),
    ("The Righteous Mind", "Jonathan Haidt"),
    ("The Social Animal", "David Brooks"),
    ("The Road to Character", "David Brooks"),
    ("The Second Mountain", "David Brooks"),
    ("Your Money and Your Brain", "Jason Zweig"),
    ("The Bogleheads' Guide to the Three-Fund Portfolio", "Taylor Larimore"),
    ("Seeking Wisdom", "Peter Bevelin"),
    ("The Little Book of Valuation", "Aswath Damodaran"),
    ("The Five Rules for Successful Stock Investing", "Pat Dorsey"),
    ("Market Wizards", "Jack D. Schwager"),
    ("Trend Following", "Michael Covel"),
    ("The Complete Turtle Trader", "Michael Covel"),
    ("Trading in the Zone", "Mark Douglas"),
    ("Reminiscences of a Stock Operator", "Edwin Lefevre"),
    ("The Warren Buffett Portfolio", "Robert G. Hagstrom"),
    ("Buffettology", "Mary Buffett"),
    ("The New Buffettology", "Mary Buffett"),
    ("The Tao of Warren Buffett", "Mary Buffett"),
    ("The 3rd Alternative", "Stephen R. Covey"),
    ("The Speed of Trust", "Stephen M. R. Covey"),
    ("The 5 Levels of Leadership", "John C. Maxwell"),
    ("Developing the Leader Within You", "John C. Maxwell"),
    ("The 15 Invaluable Laws of Growth", "John C. Maxwell"),
    ("Strengths Based Leadership", "Tom Rath"),
    ("Now, Discover Your Strengths", "Marcus Buckingham"),
    ("First, Break All the Rules", "Marcus Buckingham"),
]

chosen = []
for title, author in candidates:
    if norm(title) in existing:
        print("SKIP (already present):", title)
    else:
        chosen.append((title, author))
    if len(chosen) == 20:
        break

print(f"\nChosen {len(chosen)} new books:")
for t, a in chosen:
    print(f"  - {t} | {a}")

q = "\n".join(f"{t} | {a}" for t, a in chosen) + "\n"
(BASE / "books_queue.txt").write_text(q)
print(f"\nWrote {len(chosen)} entries to books_queue.txt")

import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
QUEUE = BASE / "scripts" / "books_queue.txt"
print(f"QUEUE path: {QUEUE}")
print(f"QUEUE exists? {QUEUE.exists()}")
if QUEUE.exists():
    lines = [l.strip() for l in QUEUE.read_text().splitlines() if l.strip()]
    print(f"lines count: {len(lines)}")
    for i, line in enumerate(lines[:5]):
        print(f"{i+1}: {line}")

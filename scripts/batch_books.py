#!/usr/bin/env python3
"""Generate up to N book PDFs per run, throttled for smooth server operation.

Reads a queue of (title, author) from books_queue.txt (one per line,
"Title | Author"), processes up to --max (default 5) with a delay between
calls so we stay under Gemini free-tier RPM (15/min) and keep CPU cool.

Usage:
  python3 batch_books.py            # process up to 5
  python3 batch_books.py --max 5
"""
import sys, time, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
QUEUE = BASE / "books_queue.txt"
GEN = BASE / "scripts" / "gen_pdf.py"
ADD = BASE / "scripts" / "add_book.py"

# throttle: 12s between calls -> ~5 calls/min (under 15 RPM limit, gentle on CPU)
CALL_DELAY = 12
DEFAULT_MAX = 5


def main():
    max_n = DEFAULT_MAX
    if "--max" in sys.argv:
        max_n = int(sys.argv[sys.argv.index("--max") + 1])
    if not QUEUE.exists():
        print("[batch] no books_queue.txt, nothing to do")
        return
    lines = [l.strip() for l in QUEUE.read_text().splitlines() if l.strip() and "|" in l]
    if not lines:
        print("[batch] queue empty")
        return
    todo = lines[:max_n]
    remaining = lines[max_n:]
    print(f"[batch] processing {len(todo)} books (max={max_n})")
    done = []
    for i, line in enumerate(todo):
        title, author = [x.strip() for x in line.split("|", 1)]
        print(f"\n=== [{i+1}/{len(todo)}] {title} ===")
        try:
            r = subprocess.run([sys.executable, str(GEN), title, author],
                               capture_output=True, text=True, timeout=240)
            if r.returncode != 0 or not (BASE / "pdf" / f"{title.replace(' ', '_')}.pdf").exists():
                print("[batch] gen FAILED, keep in queue:", r.stderr[-200:])
                remaining.append(line)
                continue
            # inject into site
            subprocess.run([sys.executable, str(ADD), title, author],
                           capture_output=True, text=True, timeout=60)
            done.append(line)
            print(f"[batch] OK: {title}")
        except Exception as e:
            print("[batch] error:", e)
            remaining.append(line)
        # throttle (skip delay after last item)
        if i < len(todo) - 1:
            time.sleep(CALL_DELAY)
    # rewrite queue with remaining
    if remaining:
        QUEUE.write_text("\n".join(remaining) + "\n")
        print(f"\n[batch] {len(remaining)} left in queue for next run")
    else:
        QUEUE.write_text("")
        print("\n[batch] queue drained")
    print(f"[batch] done: {len(done)} generated")


if __name__ == "__main__":
    main()

from pathlib import Path

base = Path("/home/ubuntu/affiliate-blog")
existing = {p.stem for p in (base / "pdf").glob("*.pdf")}

candidates = [
    ("Why Nations Fail", "Daron Acemoglu & James A. Robinson"),
    ("Guns, Germs, and Steel", "Jared Diamond"),
    ("SuperFreakonomics", "Steven D. Levitt & Stephen J. Dubner"),
    ("Think Like a Freak", "Steven D. Levitt & Stephen J. Dubner"),
    ("Naked Economics", "Charles Wheelan"),
    ("The Armchair Economist", "Steven E. Landsburg"),
    ("The Bottom Billion", "Paul Collier"),
    ("The Rational Optimist", "Matt Ridley"),
    ("The Economic Naturalist", "Robert H. Frank"),
    ("The Undercover Economist Strikes Back", "Tim Harford"),
    ("The Logic of Life", "Tim Harford"),
    ("Secrets of Sand Hill Road", "Scott Kupor"),
    ("Sprint", "Jake Knapp"),
    ("The Daily Drucker", "Peter F. Drucker"),
    ("Quality of Earnings", "Thornton O'glove"),
    ("All About Asset Allocation", "Rick Ferri"),
    ("The Only Guide to a Winning Investment Strategy You'll Ever Need", "Larry E. Swedroe"),
    ("A Random Walk Guide to Investing", "Burton G. Malkiel"),
    ("Berkshire Hathaway Letters to Shareholders", "Warren Buffett"),
    ("Unexpected Returns", "Ed Easterling"),
    ("Authentic Happiness", "Martin E. P. Seligman"),
    ("Learned Optimism", "Martin E. P. Seligman"),
    ("Flourish", "Martin E. P. Seligman"),
    ("The How of Happiness", "Sonja Lyubomirsky"),
    ("Bounce", "Matthew Syed"),
    ("The Now Habit", "Neil Fiore"),
    ("The Voice of Knowledge", "Don Miguel Ruiz"),
    ("The Psychology of Wealth", "Charles Richards"),
    ("The Millionaire Next Door" , "Thomas J. Stanley"),  # control (should be present)
    ("Atomic Habits", "James Clear"),  # control (should be present)
]

def safe(t):
    return t.replace(" ", "_").replace("/", "_").replace("\\", "_")

missing = []
for title, author in candidates:
    s = safe(title)
    present = s in existing
    print(f"{'PRESENT' if present else 'MISSING ':8} {s}")
    if not present:
        missing.append((title, author))

print("\n=== MISSING COUNT:", len(missing))
for t, a in missing:
    print(" ", t, "::", a)

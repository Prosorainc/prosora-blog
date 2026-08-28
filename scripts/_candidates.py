import re
from pathlib import Path

base = Path("/home/ubuntu/affiliate-blog")
text = (base / "scripts/add_book.py").read_text()

# Grab the _author_for function body up to its return
body = re.search(r"def _author_for\(title\):(.*?)\n    return m\.get", text, re.DOTALL).group(1)
pairs = re.findall(r'"([^"]+)":\s*"([^"]+)"', body)
catalog = {k: v for k, v in pairs}
print("catalog keys:", len(catalog))

pdfs = {p.stem for p in (base / "pdf").glob("*.pdf")}
print("existing pdfs:", len(pdfs))

cands = [(k, v) for k, v in catalog.items() if k not in pdfs]
print("candidates (in catalog, not yet PDF):", len(cands))
for k, v in cands:
    print(" ", k, "::", v)

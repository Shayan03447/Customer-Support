import sys
from pathlib import Path

from pypdf import PdfReader

src = Path(sys.argv[1])
out = Path(sys.argv[2])

reader = PdfReader(str(src))
out.parent.mkdir(parents=True, exist_ok=True)

with out.open("w", encoding="utf-8") as fh:
    for i, page in enumerate(reader.pages, start=1):
        fh.write(f"\n===== PAGE {i} =====\n")
        fh.write(page.extract_text() or "")

print(f"pages={len(reader.pages)} -> {out}")

"""Print the trailing outcome commentary of chats, grouped by the Ideal flag.

The Outcome column was glued onto the last turn during PDF export, so the
failure reasons live at the tail end of the final turn's text.
"""

import json
import re
import sys
from pathlib import Path

flag = sys.argv[1] if len(sys.argv) > 1 else "no"
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 60

data = json.loads(Path("data/chats.json").read_text(encoding="utf-8"))
chats = [c for c in data["transcripts"] if c["ideal"] == flag]

print(f"ideal={flag}  count={len(chats)}\n")
for i, c in enumerate(chats[:limit], 1):
    tail = c["turns"][-1]["text"]
    # The commentary is prose without a speaker prefix, usually the last 1-3 sentences.
    sentences = re.split(r"(?<=[.!?])\s+", tail)
    comment = " ".join(sentences[-3:])[-400:]
    print(f"{i:3d}. [{c['outcome'] or '-':<11}] {comment}")

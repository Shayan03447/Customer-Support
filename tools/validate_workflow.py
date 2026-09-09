"""Sanity-check an exported n8n workflow before importing it.

Catches the mistakes that are painful to debug in the n8n UI: duplicate node
names, connections pointing at nodes that do not exist, and $('Node Name')
expressions referring to a node that was renamed or removed.
"""

import json
import re
import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "n8n/salon-booking-agent.json")
wf = json.loads(path.read_text(encoding="utf-8"))

names = [n["name"] for n in wf["nodes"]]
errors = []

dupes = {n for n in names if names.count(n) > 1}
if dupes:
    errors.append(f"duplicate node names: {sorted(dupes)}")

known = set(names)
for src, groups in wf["connections"].items():
    if src not in known:
        errors.append(f"connection from unknown node: {src}")
    for kind, branches in groups.items():
        for branch in branches:
            for conn in branch:
                if conn["node"] not in known:
                    errors.append(f"{src} -> unknown node {conn['node']!r} ({kind})")

blob = json.dumps(wf)
for ref in sorted(set(re.findall(r"\$\('([^']+)'\)", blob))):
    if ref not in known:
        errors.append(f"expression references missing node: {ref!r}")

placeholders = sorted(set(re.findall(r"PUT_[A-Z_]+_HERE", blob)))

print(f"file        : {path}")
print(f"nodes       : {len(names)}")
print(f"connections : {sum(len(b) for g in wf['connections'].values() for b in g.values())}")

ai_tools = [
    src for src, groups in wf["connections"].items() if "ai_tool" in groups
]
print(f"agent tools : {len(ai_tools)} -> {ai_tools}")

if placeholders:
    print(f"\nplaceholders to fill in the UI: {placeholders}")

if errors:
    print("\nERRORS")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("\nstructure OK")

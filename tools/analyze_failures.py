"""Compare the chats labelled Ideal=No against Ideal=Yes to derive guardrails."""

import json
import re
from collections import Counter
from pathlib import Path

data = json.loads(Path("data/chats.json").read_text(encoding="utf-8"))
good = [c for c in data["transcripts"] if c["ideal"] == "yes"]
bad = [c for c in data["transcripts"] if c["ideal"] == "no"]

print(f"good={len(good)}  bad={len(bad)}\n")

SIGNALS = {
    "no price given": (r"how much|price|cost", r"\$\d+"),
    "customer repeated question": (r"\?!!|\?\?|hello\?|still there|any update|anyone there", None),
    "unanswered / ghosted": (r"haven't heard back|are you still|still looking", None),
    "date confusion": (r"thursday|friday|monday|tuesday|wednesday|saturday|sunday", None),
    "reschedule": (r"reschedul|change.{0,15}(date|time|appointment)", None),
    "cancel / refund": (r"cancel|refund|deposit back", None),
    "complaint / upset": (r"disappoint|upset|rude|terrible|worst|not happy|unprofessional", None),
    "wrong price / confusion": (r"you said|but you told|thought it was|why is it", None),
    "long wait in salon": (r"waiting|late|took.{0,10}hours|still not done", None),
    "discount haggling": (r"discount|cheaper|too expensive|lower price|best price", None),
    "asked for owner/human": (r"speak to|manager|owner|call you|phone call", None),
}


def rate(chats, pattern, require=None):
    hits = 0
    for c in chats:
        blob = c["customer_text"] + " " + c["agent_text"]
        if not re.search(pattern, blob, re.I):
            continue
        if require and re.search(require, c["agent_text"], re.I):
            continue
        hits += 1
    return hits, 100 * hits / max(len(chats), 1)


print(f"{'signal':<28}{'in BAD':>14}{'in GOOD':>14}   verdict")
print("-" * 74)
for name, (pat, req) in SIGNALS.items():
    bh, bp = rate(bad, pat, req)
    gh, gp = rate(good, pat, req)
    lift = bp / gp if gp else float("inf")
    verdict = "*** RISK" if lift >= 1.6 else ("  watch" if lift >= 1.2 else "")
    print(f"{name:<28}{bh:5d} ({bp:5.1f}%){gh:6d} ({gp:5.1f}%)   {verdict}")

print("\n--- outcome split ---")
for label, chats in (("BAD", bad), ("GOOD", good)):
    print(f"  {label:<5}", Counter(c["outcome"] or "(none)" for c in chats).most_common())

print("\n--- length ---")
for label, chats in (("BAD", bad), ("GOOD", good)):
    lens = sorted(c["n_turns"] for c in chats)
    print(f"  {label:<5} median turns = {lens[len(lens) // 2]}")

print("\n--- sample of short BAD chats (likely dropped leads) ---")
for c in sorted(bad, key=lambda c: c["n_turns"])[:12]:
    line = " | ".join(f"{t['who']}: {t['text'][:70]}" for t in c["turns"][:4])
    print(f"  [{c['outcome'] or '-'}] {line}")

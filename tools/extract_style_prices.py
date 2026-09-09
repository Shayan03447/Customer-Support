"""Extract clean style->price mappings from parsed chats."""

import json
import re
from collections import Counter
from pathlib import Path

data = json.loads(Path("data/chats.json").read_text(encoding="utf-8"))
agent = "\n".join(c["agent_text"] for c in data["transcripts"])

# Look for confirmation cards: Style: X ... often nearby prices in same chat
style_price = Counter()
promo = Counter()

for c in data["transcripts"]:
    a = c["agent_text"]
    # Promo phrase
    for m in re.finditer(
        r"Boho promo offers any Boho Braids style for only \$(\d+)", a, re.I
    ):
        promo[int(m.group(1))] += 1

    # "It'll be $X only" near a style word in same agent text
    styles = re.findall(
        r"(boho braids?|boho knotless|knotless braids?|box braids?|cornrows?|"
        r"stitch braids?|fulani|lemonade|butterfly|passion twist|senegalese|"
        r"goddess|bora bora|tribal|mohawk|boho bob|weave|invisible locs|"
        r"cuban twist|marley|freestyle)",
        a,
        re.I,
    )
    prices = [int(x) for x in re.findall(r"It'll be \$(\d+) only", a, re.I)]
    prices += [int(x) for x in re.findall(r"it'll be \$(\d+)", a, re.I)]
    # confirmation Style field
    card_styles = re.findall(r"Style:\s*([^\n\r]{3,40}?)(?:\s+Date:|$)", a, re.I)
    for s in card_styles:
        s = s.strip()
        # deposit is not a style price; look for $ before deposit in booking flow
        # use promo 200 if boho mentioned
        if re.search(r"boho", s, re.I):
            style_price[(s, 200)] += 1

    if len(styles) == 1 and len(prices) == 1:
        style_price[(styles[0].lower(), prices[0])] += 1
    elif len(styles) >= 1 and len(prices) == 1:
        style_price[(styles[-1].lower(), prices[0])] += 1

print("PROMO:")
for p, n in promo.most_common():
    print(f"  ${p}: {n}")

print("\nSTYLE+PRICE pairs (agent 'it'll be $X' with one style in message):")
for (s, p), n in style_price.most_common(40):
    print(f"  {n:4d}  {s} -> ${p}")

# Also extract from confirmation cards alone
print("\nCONFIRMATION CARD STYLES:")
cards = Counter()
for c in data["transcripts"]:
    for s in re.findall(r"Style:\s*([^D\n]{3,50}?)(?:\s+Date:)", c["agent_text"], re.I):
        cards[s.strip()] += 1
for s, n in cards.most_common(25):
    print(f"  {n:4d}  {s}")

# Locations / hours / deposit fixed facts
print("\nFIXED FACTS:")
for label, pat in [
    ("deposit 30", r"\$30"),
    ("3rd Ave", r"2944 3rd Ave"),
    ("White Plains", r"3201 White Plains"),
    ("hours 8-7:30", r"8:00 AM\s*[–-]\s*7:30 PM"),
    ("human hair 50", r"human hair.{0,20}\$?50"),
    ("human hair 60", r"human hair.{0,20}\$?60"),
    ("wash 20", r"\$20"),
    ("zelle", r"Zelle|Cash App"),
    ("deposit phone", r"347[) \-]*216[) \-]*6223"),
]:
    print(f"  {label}: {len(re.findall(pat, agent, re.I))}")

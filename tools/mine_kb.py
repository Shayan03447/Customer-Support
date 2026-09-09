"""Mine business facts and agent phrasing patterns out of the parsed chats."""

import json
import re
from collections import Counter
from pathlib import Path

data = json.loads(Path("data/chats.json").read_text(encoding="utf-8"))
transcripts = data["transcripts"]

agent_turns = [t["text"] for c in transcripts for t in c["turns"] if t["who"] == "us"]
cust_turns = [t["text"] for c in transcripts for t in c["turns"] if t["who"] == "customer"]
agent_all = "\n".join(agent_turns)
cust_all = "\n".join(cust_turns)


def section(title):
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


section("1. PRICES QUOTED BY THE AGENT")
price_ctx = Counter()
for m in re.finditer(r"(.{0,70})\$(\d{1,4})(.{0,40})", agent_all):
    before, amount, after = m.group(1), int(m.group(2)), m.group(3)
    price_ctx[amount] += 1
for amount, n in sorted(price_ctx.items(), key=lambda x: -x[1])[:20]:
    print(f"  ${amount:<5} quoted {n:4d} times")

section("2. SERVICES / STYLES MENTIONED")
styles = [
    "boho braids", "boho knotless", "knotless braids", "box braids", "fulani",
    "stitch braids", "cornrows", "bora bora", "tribal braids", "goddess braids",
    "lemonade braids", "marley twist", "cuban twist", "boho twist", "invisible locs",
    "passion twist", "senegalese", "faux locs", "butterfly", "boho bob", "mohawk",
]
for s in styles:
    a, c = len(re.findall(s, agent_all, re.I)), len(re.findall(s, cust_all, re.I))
    if a + c:
        print(f"  {s:<20} agent:{a:5d}   customer:{c:5d}")

section("3. POLICIES / RECURRING FACTS")
policies = {
    "Boho promo $200 incl. hair": r"\$200 \(including hair\)|Boho promo",
    "Deposit $30": r"deposit[^.]{0,30}\$30|\$30\s*/?\s*Pending",
    "Human hair extra": r"human hair \$?\d+|human hair.{0,20}extra",
    "Wash & dry extra $20": r"wash[^.]{0,30}\$20|\$20[^.]{0,20}wash",
    "Two Bronx locations": r"two locations|2 different locations",
    "3rd Ave address": r"2944 3rd Ave",
    "White Plains address": r"3201 White Plains",
    "Opening hours": r"8:00 AM\s*[–-]\s*7:30 PM",
    "After-hours surcharge": r"After 8:00 PM|additional charges apply",
    "Walk-ins accepted": r"walk[- ]?in",
    "Screenshot of deposit": r"screenshot of (your|the) deposit",
    "Google review request": r"leave us a review|g\.co/kgs",
    "Creator collaboration 50% off": r"50% off|creator",
    "BRAIDS10 / 10% off": r"BRAIDS10|10% off",
}
for name, pat in policies.items():
    print(f"  {len(re.findall(pat, agent_all, re.I)):5d}  {name}")

section("4. AGENT'S MOST REPEATED SENTENCES (its actual voice)")
norm = Counter()
for t in agent_turns:
    for sent in re.split(r"(?<=[.!?])\s+", t):
        s = re.sub(r"\s+", " ", sent).strip()
        if 15 < len(s) < 120:
            norm[s] += 1
for s, n in norm.most_common(25):
    print(f"  {n:4d}x  {s}")

section("5. WHAT CUSTOMERS ASK (top opening messages)")
openers = Counter()
for c in transcripts:
    first = next((t["text"] for t in c["turns"] if t["who"] == "customer"), None)
    if first:
        openers[re.sub(r"\s+", " ", first).strip()[:80]] += 1
for s, n in openers.most_common(20):
    print(f"  {n:4d}x  {s}")

section("6. QUESTION KEYWORDS FROM CUSTOMERS")
topics = {
    "price / how much": r"how much|price|cost|charge",
    "booking": r"book|appointment|schedule|slot",
    "availability / today": r"available|availability|today|tomorrow|walk in",
    "location / address": r"where|location|address|直|直接|near",
    "hours / open": r"open|hours|close|what time",
    "hair included": r"hair included|include.{0,10}hair|bring.{0,15}hair|own hair",
    "human hair": r"human hair",
    "colors": r"color|colour|blonde|burgundy|copper",
    "length": r"waist|butt|thigh|back length|shoulder|knee",
    "kids": r"kid|daughter|child|toddler|son|niece|granddaughter",
    "deposit / payment": r"deposit|zelle|cash app|cashapp|payment|pay|apple pay|card",
    "duration": r"how long|hours does|take.{0,10}time|duration",
    "reschedule / cancel": r"reschedul|cancel|change.{0,15}appointment|refund",
    "scalp / thin hair": r"scalp|thin hair|hair loss|tight|sensitive",
}
for name, pat in topics.items():
    print(f"  {len(re.findall(pat, cust_all, re.I)):5d}  {name}")

section("7. CONVERSION")
booked = sum(1 for c in transcripts if c["outcome"] == "Booked")
noresp = sum(1 for c in transcripts if c["outcome"] == "No Response")
print(f"  transcripts     : {len(transcripts)}")
print(f"  outcome=Booked  : {booked}")
print(f"  outcome=NoResp  : {noresp}")
print(f"  confirmations   : {len(re.findall(r'Your appointment is confirmed', agent_all, re.I))}")
lens = sorted(c["n_turns"] for c in transcripts)
print(f"  turns  median={lens[len(lens)//2]}  max={lens[-1]}")

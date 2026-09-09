import re
from collections import Counter
from pathlib import Path

text = Path("data/chats_raw.txt").read_text(encoding="utf-8")
lines = text.splitlines()

index_row = re.compile(
    r"^(\d{4})\s+(Fatima Hair Braiding NYC|Mariam S Hair Braiding|Blessing Hair Braiding)\s+"
    r"(IG DM|FB DM|WhatsApp|IG|FB)\s*(.*)$"
)

intents = Counter()
platforms = Counter()
salons = Counter()
for ln in lines:
    m = index_row.match(ln.strip())
    if not m:
        continue
    salons[m.group(2)] += 1
    platforms[m.group(3)] += 1
    tail = m.group(4).strip()
    for label in (
        "Booking Inquiry", "Pricing", "Reschedule/Cancel", "Availability",
        "Hours/Location", "Service Question", "Complaint", "Appointment Booking",
        "Follow-up", "Collaboration", "Deposit", "Other",
    ):
        if tail.endswith(label):
            intents[label] += 1
            break
    else:
        intents["(unlabelled / long text)"] += 1

transcripts = [ln for ln in lines if "Customer:" in ln or ln.strip().startswith("Us:")]
ideal_yes = sum(1 for ln in transcripts if re.search(r"\bYes\s*$", ln.strip()))
ideal_no = sum(1 for ln in transcripts if re.search(r"\bNo\s*$", ln.strip()))


def show(title, counter):
    print(f"\n--- {title} ---")
    for k, v in counter.most_common():
        print(f"{v:5d}  {k}")


show("SALONS", salons)
show("PLATFORMS", platforms)
show("INTENTS", intents)
print(f"\n--- TRANSCRIPTS ---\ntranscript lines : {len(transcripts)}")
print(f"marked Ideal=Yes : {ideal_yes}")
print(f"marked Ideal=No  : {ideal_no}")

facts = {
    "price $200": r"\$200",
    "price $240": r"\$240",
    "deposit $30": r"\$30\b",
    "human hair $50/$60": r"human hair \$?(50|60)",
    "wash $20": r"\$20\b",
    "3rd Ave location": r"2944 3rd Ave",
    "White Plains location": r"3201 White Plains",
    "opening hours": r"8:00 AM\s*[–-]\s*7:30 PM",
    "walk-in hours": r"6:30 ?am to 8 ?pm",
    "review link": r"g\.co/kgs",
}
print("\n--- BUSINESS FACTS FOUND IN CHATS ---")
for name, pat in facts.items():
    print(f"{len(re.findall(pat, text, re.I)):5d}  {name}")

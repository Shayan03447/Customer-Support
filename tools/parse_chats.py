"""Parse the extracted chat text into structured JSON records.

The source PDF is an Excel export with two sections:
  pages 1-17  : index rows  -> chat_id, salon, platform, date, intent
  pages 18-100: transcripts -> "Customer:/Us:" turns + outcome + Ideal? flag
"""

import json
import re
from pathlib import Path

RAW = Path("data/chats_raw.txt")
OUT = Path("data/chats.json")

SALONS = (
    "Fatima Hair Braiding NYC",
    "Mariam S Hair Braiding",
    "Blessing Hair Braiding",
)
INTENTS = (
    "Booking Inquiry", "Pricing", "Reschedule/Cancel", "Availability",
    "Hours/Location", "Service Question", "Complaint", "Appointment Booking",
    "Follow-up", "Collaboration", "Deposit", "Other",
)

index_re = re.compile(
    rf"^(\d{{4}})\s+({'|'.join(map(re.escape, SALONS))})\s+(IG DM|FB DM|WhatsApp|IG|FB)\s*(.*)$"
)
turn_re = re.compile(r"\b(Customer|Us):\s*")


def split_turns(chat: str):
    """Split a flattened chat string into ordered speaker turns."""
    parts = turn_re.split(chat)
    turns = []
    for speaker, body in zip(parts[1::2], parts[2::2]):
        body = body.strip()
        if body:
            turns.append({"who": speaker.lower(), "text": body})
    return turns


def parse():
    index, transcripts = [], []

    for line in RAW.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("====="):
            continue

        m = index_re.match(line)
        if m:
            tail = m.group(4).strip()
            intent = next((i for i in INTENTS if tail.endswith(i)), None)
            index.append({
                "chat_id": m.group(1),
                "salon": m.group(2),
                "platform": m.group(3),
                "date": tail[: -len(intent)].strip() if intent else tail,
                "intent": intent or "",
                "summary": "" if intent else tail,
            })
            continue

        if "Customer:" not in line and not line.startswith("Us:"):
            continue

        ideal = ""
        body = line
        if body.endswith("Yes"):
            ideal, body = "yes", body[:-3]
        elif body.endswith("No"):
            ideal, body = "no", body[:-2]

        turns = split_turns(body)
        if not turns:
            continue

        # The Outcome column is glued onto the final turn with no separator.
        tail = turns[-1]["text"]
        outcome = ""
        for marker in ("Booked", "No Response", "Not Booked", "Cancelled"):
            if tail.endswith(marker):
                outcome = marker
                turns[-1]["text"] = tail[: -len(marker)].strip()
                break

        transcripts.append({
            "turns": turns,
            "n_turns": len(turns),
            "outcome": outcome,
            "ideal": ideal,
            "customer_text": " ".join(t["text"] for t in turns if t["who"] == "customer"),
            "agent_text": " ".join(t["text"] for t in turns if t["who"] == "us"),
        })

    return index, transcripts


index, transcripts = parse()
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
    json.dumps({"index": index, "transcripts": transcripts}, indent=1, ensure_ascii=False),
    encoding="utf-8",
)

print(f"index rows   : {len(index)}")
print(f"transcripts  : {len(transcripts)}")
print(f"total turns  : {sum(t['n_turns'] for t in transcripts)}")
print(f"ideal yes/no : {sum(t['ideal'] == 'yes' for t in transcripts)} / "
      f"{sum(t['ideal'] == 'no' for t in transcripts)}")
print(f"-> {OUT}")

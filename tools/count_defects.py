"""Quantify the concrete defects spotted in the Ideal=No chats."""

import json
import re
from pathlib import Path

data = json.loads(Path("data/chats.json").read_text(encoding="utf-8"))
chats = data["transcripts"]
agent_text = {id(c): c["agent_text"] for c in chats}

confirmations = re.compile(r"appointment is confirmed", re.I)
has_conf = [c for c in chats if confirmations.search(c["agent_text"])]

DEFECTS = {
    "confirmation sent while deposit still Pending":
        lambda c: re.search(r"Deposit:?\s*\$?30\s*/?\s*Pending", c["agent_text"], re.I),
    "confirmation lists BOTH addresses (customer can't tell which)":
        lambda c: re.search(r"2944 3rd Ave[^|]{0,60}3201 White Plains", c["agent_text"], re.I),
    "phone field contains an email address":
        lambda c: re.search(r"Phone Number:\s*\S*@", c["agent_text"], re.I),
    "appointment time set to AM when customer said pm":
        lambda c: re.search(r"\d(:\d\d)?\s*pm", c["customer_text"], re.I)
        and re.search(r"Time:\s*\d{1,2}(:\d\d)?\s*AM", c["agent_text"]),
    "customer wrote Spanish, agent answered English":
        lambda c: re.search(r"\b(hola|buenas|cuanto|cita|cuánto|gracias|precio|pelo)\b",
                            c["customer_text"], re.I)
        and not re.search(r"\b(hola|gracias|cita|precio)\b", c["agent_text"], re.I),
    "agent repeated the same sentence 3+ times":
        lambda c: any(
            sum(1 for t in c["turns"] if t["who"] == "us" and s in t["text"]) >= 3
            for s in ("Let me know what date and time works best",
                      "please share your name, phone number")
        ),
    "passive close ('let me know if you'd like to come in')":
        lambda c: re.search(r"let me know (if you'd like to come in|when you are ready)",
                            c["agent_text"], re.I),
    "customer asked price, agent never quoted a number":
        lambda c: re.search(r"how much|price|cost", c["customer_text"], re.I)
        and not re.search(r"\$\d+", c["agent_text"]),
}

bad = [c for c in chats if c["ideal"] == "no"]
good = [c for c in chats if c["ideal"] == "yes"]

print(f"total chats           : {len(chats)}")
print(f"chats with a confirmation card : {len(has_conf)}\n")
print(f"{'defect':<58}{'BAD':>8}{'GOOD':>8}{'ALL':>8}")
print("-" * 82)
for name, test in DEFECTS.items():
    b = sum(1 for c in bad if test(c))
    g = sum(1 for c in good if test(c))
    print(f"{name:<58}{b:8d}{g:8d}{b + g:8d}")

print("\n--- deposit follow-through ---")
paid = sum(1 for c in has_conf
           if re.search(r"screenshot|received|payment (is )?confirmed|deposit (is )?(paid|received)",
                        c["customer_text"], re.I))
print(f"  confirmations sent            : {len(has_conf)}")
print(f"  customer replied re: deposit  : {paid}")
print(f"  no deposit evidence           : {len(has_conf) - paid}")

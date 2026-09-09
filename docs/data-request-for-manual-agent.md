# Data Request for Manual Agent — 2 Salons (Testing)

Copy this to the manual agent. Ask for **one package per salon**.
Preferred format: **Google Sheet** (1 tab per section) OR **1 Word/Google Doc per salon**.
PDF screenshots of Instagram are OK as extra, but not as the only source.

Goal: AI should answer the same way the human agent answers — with correct
prices, locations, deposit rules, and booking steps. Missing or unclear
prices will force the AI to escalate to a human.

---

## Package rules

1. **Separate file/folder per salon** (Salon A and Salon B — do not mix).
2. Write facts as you tell customers today (current truth only).
3. If something is “depends”, write the rule (e.g. “price depends on length”).
4. Do **not** invent prices. If unsure, write `UNKNOWN — ask owner`.
5. Customer chat examples: remove or mask phone/email if needed (`***-***-1234`).

---

## Section 1 — Business basics (required)

| Field | Example |
|---|---|
| Salon legal/display name | Fatima Hair Braiding NYC |
| Instagram handle | @... |
| Facebook page name | ... |
| Primary language(s) | English / Spanish / both |
| Timezone | America/New_York |
| Opening hours (exact) | Mon–Sun 8:00 AM – 7:30 PM |
| Walk-ins? | Yes / No + hours |
| After-hours policy | e.g. after 8 PM by appointment + surcharge |
| Locations (full address each) | Address 1, Address 2 |
| Which location for which service (if different) | All services both / or rule |

---

## Section 2 — Service + price list (most important)

Give a table. One row = one bookable thing.

| Style / service | Size (S/M/L) | Length | Hair included? | Base price | Extra notes |
|---|---|---|---|---|---|
| Boho braids | Any | Any | Yes (synthetic) | $200 | Promo |
| Small knotless waist | Small | Waist | Yes | $240 | |
| Freestyle cornrows | — | — | — | $160 | |
| 2 stitch braids | — | — | — | $40 | |

Also list:

| Add-on | Price | Notes |
|---|---|---|
| Human hair (per pack) | $__ | Brand if customers ask |
| Wash & dry | $__ | |
| Color / special color | $__ or rule | |
| Kids price difference | rule or prices | Age limit if any |

**Must answer these common questions in writing:**

1. Is hair included in the price? When yes / when no?
2. Can customer bring their own hair?
3. How does length change the price?
4. How does size (small/medium/large) change the price?
5. Do you do kids’ hair? From what age?
6. Sensitive scalp / thin hair — what do you say?

---

## Section 3 — Booking + payment rules (required)

| Field | Your answer |
|---|---|
| Deposit amount | $__ |
| When is deposit required? | Always / only same-day / etc. |
| Payment methods for deposit | Zelle / Cash App / … |
| Deposit handle (number / username) | |
| Does deposit go toward total? | Yes / No |
| Proof needed | Screenshot? |
| When do you say “confirmed”? | Only after deposit? |
| Cancellation / refund policy | |
| Reschedule policy | How late can they change? |
| Same-day / walk-in booking rules | |
| What info you collect before booking | Name, phone, email, style, date, time, location |
| Confirmation message template you use | Paste one real example |

---

## Section 4 — Promotions (if any)

| Promo code / name | What it gives | Valid until | Notes |
|---|---|---|---|
| BRAIDS10 | 10% off | | |
| Boho promo | $200 incl hair | | |
| Creator / collab | | | Who approves? |

If a promo is owner-only / case-by-case, write: **AI must escalate**.

---

## Section 5 — FAQ you answer every day (required)

Write **Q → A** in your own words (20–40 is enough). Examples:

- How much for boho braids?
- Where are you located?
- What are your hours?
- Do you take walk-ins?
- Is hair included?
- Human hair extra?
- Do you do kids?
- How long does it take? (if you have an answer)
- Can I book for tomorrow?
- How do I pay the deposit?

Use the answers you actually send in DMs.

---

## Section 6 — Chat examples (very valuable)

Per salon, send **30–50 real chats** (or more if easy):

Preferred: Excel/Sheet with columns:

| chat_id | date | platform (IG/FB) | customer messages | agent replies | outcome (booked / no response / lost) | notes |

OR WhatsApp/IG export text — fine.

Mark 10 chats as **good example** (how AI should talk).
Mark 10 chats as **bad / hard** (refund, complaint, wrong price, Spanish, etc.) — AI should hand these to human.

---

## Section 7 — Escalate to human (required)

List situations where AI should stop and call you/staff:

- Refund / deposit dispute
- Complaint about stylist / wait time
- Custom price not on list
- Discount beyond published promos
- Owner/manager request
- Anything else you always handle yourself

---

## Section 8 — Access info (for testing setup — separate secure message)

Do **not** put tokens in the same Doc as prices if possible. Send privately:

| Item | Salon A | Salon B |
|---|---|---|
| Facebook Page ID | | |
| Instagram account ID | | |
| Page access token (or note “I will add in Meta”) | | |
| Google Calendar email / ID | | |
| Who gets handoff alerts (phone/WhatsApp/email) | | |

---

## Delivery checklist for agent

For **each of 2 salons**, I need:

- [ ] Section 1 Business basics
- [ ] Section 2 Full price/service table
- [ ] Section 3 Deposit/booking rules + 1 confirmation template
- [ ] Section 4 Promotions
- [ ] Section 5 FAQ Q&A
- [ ] Section 6 Chat samples (30+)
- [ ] Section 7 Escalation list
- [ ] Section 8 Access (private)

**Deadline suggestion:** Salon 1 complete first, then Salon 2 (same format).

**File naming:**

```
SalonA_KB.xlsx (or .docx)
SalonA_Chats.xlsx
SalonB_KB.xlsx
SalonB_Chats.xlsx
```

---

## What we do NOT need yet

- Full old year of every chat (nice later, not blocking)
- Marketing ad creatives
- Owner’s personal passwords in the price sheet
- Perfect English — clear facts matter more

---

## Why this format

Our AI system stores salon knowledge as short facts (prices, hours, deposit).
If prices are in a clean table, we load them once.
If prices are only inside random chat screenshots, we will miss or invent answers.

Clean table = safer AI. Messy screenshots = more handoffs to you.

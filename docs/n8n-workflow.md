# n8n Workflow — Node by Node

One workflow serves every salon. A config row keyed by Meta page ID is what
makes it behave like a different business per client.

```
Meta webhook ─► verify ─► 200 OK ─► normalize ─► tenant lookup ─► dedupe
   ─► debounce ─► AI agent (tools) ─► send reply ─► log
```

---

## 1. `Webhook` — single entry point

| Setting | Value |
|---|---|
| Method | `GET` + `POST` |
| Path | `meta` |
| Response | Using Respond to Webhook node |
| Raw body | **on** (needed for the signature check) |

`GET` handles Meta's subscription challenge: return `hub.challenge` when
`hub.verify_token` matches. `POST` carries the messages.

## 2. `Code` — verify signature

```js
const crypto = require('crypto');
const raw = $input.first().binary
  ? Buffer.from($input.first().binary.data.data, 'base64').toString()
  : JSON.stringify($json.body);

const expected = 'sha256=' + crypto
  .createHmac('sha256', $env.META_APP_SECRET)
  .update(raw)
  .digest('hex');

const received = $json.headers['x-hub-signature-256'];
if (received !== expected) throw new Error('bad signature');
return $input.all();
```

Without this, anyone who finds the URL can post fake messages into your CRM.

## 3. `Respond to Webhook` — answer immediately

Body `EVENT_RECEIVED`, status `200`. This must fire **before** any AI work.
Meta retries anything slower than about 20 seconds, and a retry means the
customer gets the same reply two or three times.

## 4. `Code` — normalize

Flattens the Messenger and Instagram shapes into one object, and drops echoes.

```js
const out = [];
for (const entry of $json.body.entry ?? []) {
  for (const ev of entry.messaging ?? []) {
    if (ev.message?.is_echo) continue;            // our own message coming back
    if (!ev.message && !ev.postback) continue;    // reads, deliveries, reactions

    out.push({ json: {
      page_id:    entry.id,
      platform:   $json.body.object === 'instagram' ? 'instagram' : 'messenger',
      sender_id:  ev.sender.id,
      message_id: ev.message?.mid ?? ev.postback?.mid,
      text:       ev.message?.text ?? ev.postback?.title ?? '',
      attachments: ev.message?.attachments ?? [],
      ad_id:      ev.referral?.ad_id ?? ev.postback?.referral?.ad_id ?? null,
      ad_ref:     ev.referral?.ref   ?? ev.postback?.referral?.ref   ?? null,
      ts:         ev.timestamp,
    }});
  }
}
return out;
```

`ad_id` only arrives on the **first** message of a thread. If it is not saved
here it is gone, and ad attribution dies with it.

## 5. `Google Sheets` — tenant lookup

Read the `Tenants` sheet, filter `page_id` equals the incoming `page_id`.
Returns one row:

```
page_id | salon_name | page_token | timezone | deposit_amount |
deposit_handle | deposit_methods | review_link | kb_tag |
calendar_id | promos | staff_notify | active
```

If nothing matches, stop and alert. An unknown page ID means a
misconfiguration, never a customer.

Cache this node's output — it is the same for every message from that page.

## 6. `Redis` / `Code` — dedupe

Key `msg:{{message_id}}`, TTL 24h. If the key already exists, stop. This kills
duplicate replies from Meta retries.

## 7. `Wait` + `Code` — debounce

Wait 5 seconds, then pull every buffered message for
`{{page_id}}:{{sender_id}}` and join them with a space.

Customers type in bursts:

> "hi" · "how much for boho" · "and do you have blonde"

Without this the agent answers three times and reads as a bot. The real
transcripts show a median of 14 turns per conversation, many of them these
fragments.

## 8. `AI Agent`

| Slot | Node |
|---|---|
| Chat model | OpenAI, `gpt-4.1` or `gpt-4o` |
| Memory | Postgres Chat Memory, session key `{{page_id}}:{{sender_id}}` |
| System prompt | `prompts/booking-agent.md`, tenant values injected |

The session key **must** include `page_id`. With `sender_id` alone, the same
person messaging two salons would share one conversation history.

### Tools

**`search_knowledge`** — PGVector, one table for all salons:

```sql
SELECT text FROM kb
WHERE metadata->>'tenant_id' = '{{kb_tag}}'
ORDER BY embedding <=> $1
LIMIT 4;
```

The `WHERE` clause is the only thing stopping one salon's prices from leaking
into another salon's chat. It is not optional.

**`check_availability`** — Google Calendar, free/busy on `calendar_id`.

**`create_booking`** — Google Calendar insert + append to the `Bookings` sheet.
Status starts at `reserved`, not `confirmed`.

**`upsert_lead`** — the `Leads` sheet, matched on `tenant_id + platform +
sender_id`. Called on every message, not just at booking time.

**`escalate_to_human`** — sets `handoff = yes` on the lead row, posts to the
salon's WhatsApp or Slack, and mutes the bot for that thread.

## 9. `Switch` — pick the channel

On `{{ $json.platform }}`:

- `messenger` → `POST /v18.0/me/messages` with the tenant's `page_token`
- `instagram` → same endpoint, Instagram-scoped token

## 10. `HTTP Request` — send

```json
{
  "recipient": { "id": "{{ $json.sender_id }}" },
  "message":   { "text": "{{ $json.reply }}" },
  "messaging_type": "RESPONSE"
}
```

Header: `Authorization: Bearer {{ tenant.page_token }}`.

After 24 hours of customer silence this call fails — that is Meta's standard
messaging window, not a bug. Route those to the human follow-up list.

## 11. `Google Sheets` — log

Append every inbound and outbound message to the `Messages` sheet. When a
customer says "your bot told me $150", this is the only way to check.

---

## Google Sheets structure

**`Tenants`** — one row per salon, the fields listed in step 5.

**`Leads`** — one row per person, keyed on `tenant_id + platform + sender_id`:

```
lead_id | tenant_id | platform | sender_id | name | phone | email |
style_interest | ad_id | ad_ref | stage | first_seen | last_seen |
handoff | notes
```

`stage`: `new` → `quoted` → `details_collected` → `reserved` → `deposit_paid`
→ `completed` / `lost`

The `reserved` vs `deposit_paid` split is the important one. In the real data
260 appointments were called "confirmed" and only 5 show any deposit reply —
that gap is the salon's no-show risk, and it becomes visible the moment these
are separate stages.

**`Bookings`**

```
booking_id | lead_id | tenant_id | style | date_time | location |
price | deposit_status | calendar_event_id | status
```

**`Messages`**

```
ts | tenant_id | platform | sender_id | direction | text | tool_calls | handoff
```

---

## Build order

1. Webhook + signature + `200 OK`, echoed to a sheet. Prove messages arrive.
2. Normalizer and tenant lookup with **two** salons in the sheet. Prove
   isolation before scaling.
3. Knowledge base ingest from `kb/fatima-hair-braiding.md`, tagged by tenant.
4. Agent with `search_knowledge` only — answers questions, books nothing.
5. `upsert_lead` with `ad_id` capture.
6. Calendar and booking, with the reserved/confirmed split.
7. Escalation and logging.
8. Replay 50 held-out real chats against it, compare to what the human said.
9. Onboard the remaining salons as rows.

## Known limits to plan around

| Limit | Effect |
|---|---|
| Meta 24-hour window | Cannot freely message after a day of silence |
| Google Sheets API | ~60 writes/min per user; fine to roughly 30 leads/day/salon |
| Webhook timeout | Must respond in under ~20s or Meta retries |
| Instagram | Only business/creator accounts can receive DM webhooks |

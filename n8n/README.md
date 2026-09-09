# Importing the workflow

`salon-booking-agent.json` is a working scaffold, not a finished install.
Import it, then do the seven steps below. Nothing will run before that, because
credentials and IDs cannot be exported.

Built against n8n **2.37.9**.

## 1. Import

n8n → Workflows → **Import from File** → `salon-booking-agent.json`.

25 nodes should appear in two rows: the webhook chain along the top, the agent
and its five tools below.

## 2. Environment variables

Two Code nodes read `$env`. Add these to the n8n container and restart it:

```
META_APP_SECRET=<from the Meta app dashboard>
META_VERIFY_TOKEN=<any string you invent; you paste the same one into Meta>
```

If `$env` comes back empty, `N8N_BLOCK_ENV_ACCESS_IN_NODE` is set to `true` on
your container. Set it to `false`.

## 3. Credentials

| Node | Credential |
|---|---|
| Tenant Lookup, Dedupe, Log Inbound, Log Outbound | Postgres |
| Postgres Memory | Postgres (same) |
| OpenAI Chat Model, Embeddings OpenAI | OpenAI |
| Company Knowledge | Postgres (same) |
| check_availability, create_booking | Google Calendar OAuth2 |
| upsert_lead, escalate_to_human | Google Sheets OAuth2 |

Postgres credential values, from inside the n8n container:

```
Host     cs-postgres
Port     5432
Database salonbot
User     salonbot
Password see POSTGRES_PASSWORD in .env
SSL      disable
```

Use `cs-postgres`, not `localhost`. Inside the container `localhost` is n8n
itself.

## 4. Fill the placeholders

`upsert_lead` and `escalate_to_human` both contain `PUT_SHEET_ID_HERE`. Replace
it with your CRM spreadsheet ID — the long string in the sheet URL between
`/d/` and `/edit`.

The `Leads` tab needs these headers in row 1, spelled exactly:

```
lead_key | tenant_id | platform | sender_id | ad_id | name | phone | email |
style_interest | stage | notes | last_seen | handoff
```

`lead_key` is the matching column. Without it every message creates a new row
instead of updating the existing customer.

## 5. Seed the tenant

```sql
UPDATE tenants SET
  page_id        = '<your Facebook page id>',
  ig_id          = '<your Instagram account id>',
  page_token     = '<page access token>',
  timezone       = 'America/New_York',
  deposit_amount = 30,
  deposit_methods= 'Zelle or Cash App',
  deposit_handle = '+1 (347) 216-6223',
  review_link    = 'https://g.co/kgs/B8LWq2T',
  calendar_id    = '<google calendar id>',
  promos         = 'Boho promo $200 incl. hair; BRAIDS10 for 10% off'
WHERE tenant_id = 'fatima';
```

The row itself is created by `tools/load_kb.py`, so load the knowledge base
first.

## 6. Point Meta at the webhook

Activate the workflow, then copy the **production** URL from the
`Meta Webhook (POST)` node. It ends in `/webhook/meta`.

n8n must be reachable from the internet. For local testing, tunnel it:

```powershell
docker exec n8n n8n start --tunnel
```

In the Meta app dashboard, set the callback URL and your verify token, then
subscribe to the `messages` and `messaging_postbacks` fields for each page.

Meta calls the URL with `GET` first — that is what the top chain answers.

## 7. Test before going live

1. Send yourself a DM from a second account.
2. Watch the execution list. It should stop at `Is New Message?` on a retry and
   continue on a first delivery.
3. Send the same message twice quickly and confirm you only get one reply.
4. Ask "how much for boho braids?" and check the agent calls
   `search_knowledge` rather than answering from memory.

---

## Things worth knowing before you trust it

**Your n8n timezone is `Asia/Karachi`, the salon is in New York.** The agent
prompt converts to the tenant's timezone, so the text it writes is correct, but
any Schedule or Date node you add later will use Karachi time. Either set
`GENERIC_TIMEZONE=America/New_York` on the container or set the timezone
per-workflow in workflow settings.

**Verify the knowledge filter before adding salon #2.** `Company Knowledge`
filters retrieval on `tenant_id` in the chunk metadata. That filter is the only
thing keeping one salon's prices out of another salon's chat. Open the node,
confirm the metadata filter is populated, and test it with two tenants loaded
before you onboard more clients.

**`Debounce 5s` uses a Wait node**, which is a simple pause rather than a real
buffer. If a customer sends three messages, three executions start and each
waits 5 seconds — you can still get three replies. A proper fix collects
pending messages per thread in Redis or a Postgres table and lets only the last
execution proceed. Do this before launch if your ads drive real volume.

**Instagram and Messenger use different Graph hosts.** Both send nodes are
wired, but Instagram messaging needs a Business or Creator account linked to
the Facebook page, and its own token scope.

**The 24-hour window.** Sends fail after a day of customer silence. Those
failures are expected, not bugs — route them to a human follow-up list.

# Customer-Support

Multi-tenant AI booking agent for salons that run Facebook and Instagram ads.
One n8n workflow serves every salon; a config row keyed by Meta page ID is what
makes it behave like a different business per client.

Built from 699 real Instagram and Facebook DM conversations, so the prices,
policies, and the agent's phrasing all come from what the human agent actually
said rather than from guesses.

## Layout

| Path | What it holds |
|---|---|
| `kb/` | Per-salon knowledge base, mined from the real chats |
| `prompts/` | Agent system prompt and the evidence behind each rule |
| `n8n/` | Importable workflow JSON and its setup guide |
| `docs/n8n-workflow.md` | Node-by-node workflow design |
| `sql/` | Postgres schema, applied on first container start |
| `tools/` | Extraction, parsing, analysis, and KB loading scripts |
| `data/` | Generated. Contains real customer PII, so it is gitignored |

## Setup

Requires Docker and Python 3.11+. An n8n container must already be running;
Postgres joins its network so the two can talk.

```powershell
pip install -r requirements.txt
cp .env.example .env      # then fill in OPENAI_API_KEY
docker compose up -d
```

Postgres is reachable at `localhost:5433` from the host, and at
`cs-postgres:5432` from inside n8n. The schema in `sql/` runs automatically on
first start.

## Loading a salon's knowledge base

```powershell
python tools/build_kb_chunks.py kb/fatima-hair-braiding.md fatima
python tools/load_kb.py fatima "Fatima Hair Braiding & Extensions NYC"
```

Re-running replaces that tenant's chunks, so editing the markdown and reloading
is the normal way to iterate.

## Rebuilding the analysis

The chat PDF is not committed. With it in the repo root:

```powershell
python tools/extract_pdf.py Abdullah_Chat_Data_Collection.pdf data/chats_raw.txt
python tools/parse_chats.py
python tools/mine_kb.py           # prices, policies, agent phrasing
python tools/analyze_failures.py  # the 117 chats labelled Ideal=No
python tools/count_defects.py     # concrete defect counts
```

## What the data showed

- 699 chats, 9,490 messages, 3 salons. Instagram 644, Facebook 55.
- 85% of traffic is price, booking, or hours/location — all automatable.
- 260 appointments were sent a "confirmed" card, but only 5 show any deposit
  reply. That gap is the biggest revenue leak and is why the agent separates
  `reserved` from `confirmed`.
- 183 confirmation cards listed both Bronx addresses at once.

## Adding another salon

1. Write `kb/<salon>.md` in the same shape as the existing one.
2. Build and load its chunks.
3. Insert a row in `tenants` with the salon's page ID, token, and calendar.

No workflow changes.

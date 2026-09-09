CREATE EXTENSION IF NOT EXISTS vector;

-- One row per salon. This is what turns one workflow into many businesses.
CREATE TABLE IF NOT EXISTS tenants (
    tenant_id       text PRIMARY KEY,
    salon_name      text NOT NULL,
    page_id         text UNIQUE,
    ig_id           text UNIQUE,
    page_token      text,
    timezone        text NOT NULL DEFAULT 'America/New_York',
    deposit_amount  numeric(10, 2) NOT NULL DEFAULT 30,
    deposit_methods text NOT NULL DEFAULT 'Zelle or Cash App',
    deposit_handle  text,
    review_link     text,
    calendar_id     text,
    promos          text,
    staff_notify    text,
    active          boolean NOT NULL DEFAULT true,
    created_at      timestamptz NOT NULL DEFAULT now()
);

-- Knowledge base. One table for every salon; tenant_id is what keeps them apart.
-- text-embedding-3-small is 1536 dimensions.
CREATE TABLE IF NOT EXISTS kb (
    id         bigserial PRIMARY KEY,
    tenant_id  text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    topic      text NOT NULL,
    content    text NOT NULL,
    confidence text NOT NULL DEFAULT 'high',   -- high | confirm
    metadata   jsonb NOT NULL DEFAULT '{}',
    embedding  vector(1536),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Every retrieval filters on tenant_id first, so it leads the index.
CREATE INDEX IF NOT EXISTS kb_tenant_idx ON kb (tenant_id);
CREATE INDEX IF NOT EXISTS kb_embedding_idx
    ON kb USING hnsw (embedding vector_cosine_ops);

-- Deduplication of Meta webhook retries.
CREATE TABLE IF NOT EXISTS seen_messages (
    message_id text PRIMARY KEY,
    seen_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS seen_messages_age_idx ON seen_messages (seen_at);

-- Full message log. This lives in Postgres rather than Google Sheets because
-- every inbound and outbound message writes a row, which would burn through
-- the Sheets API quota within a day.
CREATE TABLE IF NOT EXISTS messages (
    id         bigserial PRIMARY KEY,
    tenant_id  text NOT NULL,
    platform   text NOT NULL,
    sender_id  text NOT NULL,
    direction  text NOT NULL,               -- in | out
    text       text,
    ad_id      text,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS messages_thread_idx
    ON messages (tenant_id, sender_id, created_at DESC);

-- n8n's Postgres Chat Memory node creates and manages its own table
-- (n8n_chat_histories) on first run. Nothing to define here.

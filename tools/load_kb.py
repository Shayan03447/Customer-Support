"""Embed the knowledge-base chunks and load them into Postgres/pgvector.

    python tools/load_kb.py fatima "Fatima Hair Braiding & Extensions NYC"

Re-running replaces that tenant's chunks, so it is safe to iterate on the
knowledge base and reload.
"""

import json
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CHUNKS = Path("data/kb_chunks.jsonl")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")
BATCH = 64


def main(tenant_id: str, salon_name: str) -> None:
    chunks = [json.loads(l) for l in CHUNKS.read_text(encoding="utf-8").splitlines() if l.strip()]
    chunks = [c for c in chunks if c["tenant_id"] == tenant_id]
    if not chunks:
        sys.exit(f"no chunks for tenant {tenant_id!r} in {CHUNKS}")

    client = OpenAI()
    vectors = []
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i : i + BATCH]
        resp = client.embeddings.create(
            model=EMBED_MODEL, input=[c["content"] for c in batch]
        )
        vectors.extend(d.embedding for d in resp.data)
        print(f"  embedded {min(i + BATCH, len(chunks))}/{len(chunks)}")

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO tenants (tenant_id, salon_name)
            VALUES (%s, %s)
            ON CONFLICT (tenant_id) DO UPDATE SET salon_name = EXCLUDED.salon_name
            """,
            (tenant_id, salon_name),
        )
        cur.execute("DELETE FROM kb WHERE tenant_id = %s", (tenant_id,))
        cur.executemany(
            """
            INSERT INTO kb (tenant_id, topic, content, confidence, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    c["tenant_id"],
                    c["topic"],
                    c["content"],
                    c["confidence"],
                    json.dumps(c["metadata"]),
                    str(vec),
                )
                for c, vec in zip(chunks, vectors)
            ],
        )
        conn.commit()
        cur.execute("SELECT count(*) FROM kb WHERE tenant_id = %s", (tenant_id,))
        print(f"\nloaded {cur.fetchone()[0]} chunks for {tenant_id}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

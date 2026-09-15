"""Turn a salon knowledge-base markdown file into retrieval chunks.

Chunks are deliberately small and self-contained. Each one repeats the salon
name and the section it came from, because a chunk retrieved on its own has no
surrounding context to lean on.

Table rows become one chunk each: "how much is X" should match a single price,
not a whole price list.

    python tools/build_kb_chunks.py kb/fatima-hair-braiding.md fatima
"""

import json
import re
import sys
from pathlib import Path

MAX_CHARS = 700
CONFIRM = re.compile(r"\[CONFIRM[^\]]*\]")

# Sections that document the dataset rather than the business. A customer must
# never be answered with "this came from 699 conversations".
SKIP_SECTIONS = ("Overview", "What customers actually ask")

# "[234]", "[108 mentions of "two locations"]" — provenance notes for humans.
EVIDENCE = re.compile(r"\[\d+[^\]]*\]")

# Table columns that describe the dataset, not the business.
DROP_COLUMNS = {"Times", "Mentions", "Share"}

# Sentences about how the knowledge base was built. True, but useless to a
# customer and actively confusing if the agent retrieves one.
META = re.compile(
    r"most quoted fact|in the entire dataset|confirmed from real conversations"
    r"|ranked by frequency|these come straight from",
    re.I,
)

SECTION_NUM = re.compile(r"^\d+\.\s*")


def clean(text: str) -> str:
    text = EVIDENCE.sub("", text)
    text = re.sub(r"\*\*|`", "", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([.,:;])", r"\1", text)
    return text.strip(" .:·").strip()


def split_table(block: str):
    """Yield (text, needs_confirm) for each data row of a markdown table."""
    rows = [r.strip() for r in block.splitlines() if r.strip().startswith("|")]
    if len(rows) < 3:
        return
    header = [c.strip() for c in rows[0].strip("|").split("|")]
    for row in rows[2:]:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) != len(header) or not any(cells):
            continue
        # Check the whole row first: the [CONFIRM] marker often sits in a
        # column we are about to drop.
        needs_confirm = bool(CONFIRM.search(row))
        # Strip the marker before the emptiness test, or a cell holding nothing
        # but [CONFIRM] leaves a dangling "Notes:" with no value.
        cells = [CONFIRM.sub("", c).strip(" *") for c in cells]
        pairs = [
            f"{h}: {c}" for h, c in zip(header, cells)
            if c and c != "—" and h not in DROP_COLUMNS
        ]
        if pairs:
            yield " · ".join(pairs), needs_confirm


def paragraphs(block: str):
    for para in re.split(r"\n\s*\n", block):
        para = para.strip()
        if not para:
            continue
        if len(para) <= MAX_CHARS:
            yield para
            continue
        buf = ""
        for line in para.splitlines():
            if len(buf) + len(line) > MAX_CHARS and buf:
                yield buf.strip()
                buf = ""
            buf += line + "\n"
        if buf.strip():
            yield buf.strip()


def build(md_path: Path, tenant_id: str):
    lines = md_path.read_text(encoding="utf-8").splitlines()
    salon = lines[0].lstrip("# ").split("—")[0].strip()

    sections, h2, heading, buf = [], "Overview", "Overview", []
    for line in lines[1:]:
        if line.startswith("## "):
            sections.append((heading, "\n".join(buf)))
            h2 = line.lstrip("# ").strip()
            heading, buf = h2, []
        elif line.startswith("### "):
            sections.append((heading, "\n".join(buf)))
            # Hang the h3 off its parent h2, not off the previous h3.
            heading, buf = f"{h2} — {line.lstrip('# ').strip()}", []
        else:
            buf.append(line)
    sections.append((heading, "\n".join(buf)))

    chunks = []
    for heading, body in sections:
        heading = SECTION_NUM.sub("", heading)
        if not body.strip() or heading.startswith(SKIP_SECTIONS):
            continue

        table_block = "\n".join(l for l in body.splitlines() if l.strip().startswith("|"))
        prose_block = "\n".join(l for l in body.splitlines() if not l.strip().startswith("|"))

        # A table row is already an atomic fact, so it is kept even when short.
        # Loose prose needs more substance to be worth retrieving on its own.
        pieces = [(t, c, 12) for t, c in split_table(table_block)]
        pieces += [(p, bool(CONFIRM.search(p)), 25) for p in paragraphs(prose_block)]

        for piece, needs_confirm, min_len in pieces:
            confidence = "confirm" if needs_confirm else "high"
            text = clean(CONFIRM.sub("", piece))
            if len(text) < min_len or META.search(text):
                continue
            chunks.append({
                "tenant_id": tenant_id,
                "topic": heading,
                "content": f"{salon} — {heading}. {text}",
                "confidence": confidence,
                
                "metadata": {
                    "tenant_id": tenant_id,
                    "source": md_path.name,
                    "section": heading,
                },
            })
    return chunks


if __name__ == "__main__":
    md_path = Path(sys.argv[1])
    tenant_id = sys.argv[2]
    chunks = build(md_path, tenant_id)

    out = Path("data/kb_chunks.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    n_confirm = sum(c["confidence"] == "confirm" for c in chunks)
    print(f"chunks         : {len(chunks)}")
    print(f"needs confirm  : {n_confirm}")
    print(f"avg chars      : {sum(len(c['content']) for c in chunks) // max(len(chunks), 1)}")
    print(f"-> {out}\n")
    for c in chunks[:8]:
        print(f"  [{c['confidence']:<7}] {c['content'][:110]}")

import re
from pathlib import Path

import chromadb
from rank_bm25 import BM25Okapi

DB_PATH = Path(__file__).parent / "chroma_db"
COLLECTION = "filings_local"

try:
    col = chromadb.PersistentClient(path=str(DB_PATH)).get_collection(COLLECTION)
except Exception as e:
    raise RuntimeError(
        f"Search index not found at {DB_PATH}. Run `python build_index.py` first "
        "(it needs the PDFs in data/), or ship the built chroma_db folder with the app."
    ) from e

_data = col.get(include=["documents", "metadatas"])
IDS, DOCS, METAS = _data["ids"], _data["documents"], _data["metadatas"]
IDX = {id_: i for i, id_ in enumerate(IDS)}

def tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())

BM25 = BM25Okapi([tok(d) for d in DOCS])

def search(question, k=10, pool=30):
    # 1. meaning-based search
    res = col.query(query_texts=[question], n_results=pool)
    sem = [IDX[i] for i in res["ids"][0]]

    # 2. keyword search
    scores = BM25.get_scores(tok(question))
    kw = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:pool]

    # 3. merge the two rankings (reciprocal rank fusion)
    fused = {}
    for ranking in (sem, kw):
        for rank, i in enumerate(ranking):
            fused[i] = fused.get(i, 0) + 1 / (60 + rank)
    top = sorted(fused, key=fused.get, reverse=True)[:k]

    return [{"text": DOCS[i], "source": METAS[i]["source"], "page": METAS[i]["page"]} for i in top]

if __name__ == "__main__":
    for r in search("What were total advances at March 31, 2026?"):
        print(r["source"], "p.", r["page"], "|", r["text"][:100].replace("\n", " "))

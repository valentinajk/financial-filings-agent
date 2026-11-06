import chromadb
from ingest import load_chunks

BATCH = 200

if __name__ == "__main__":
    chunks = []
    chunks += load_chunks("data/hdfc_fy26.pdf", "HDFC FY26")
    chunks += load_chunks("data/hdfc_fy25.pdf", "HDFC FY25")

    db = chromadb.PersistentClient(path="chroma_db")
    col = db.get_or_create_collection("filings_local")

    start = col.count()  # resumes if interrupted
    print(f"Already stored: {start} / {len(chunks)}")

    for i in range(start, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        col.add(
            ids=[f"c{i + j}" for j in range(len(batch))],
            documents=[c["text"] for c in batch],
            metadatas=[{"source": c["source"], "page": c["page"]} for c in batch],
        )
        print(f"Stored {min(i + BATCH, len(chunks))} / {len(chunks)}")
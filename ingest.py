import pymupdf

def load_chunks(path, source, size=1500, overlap_lines=2):
    doc = pymupdf.open(path)
    chunks = []
    for i, page in enumerate(doc):
        lines = [l.strip() for l in page.get_text().split("\n") if l.strip()]
        cur, length = [], 0
        for line in lines:
            if length + len(line) > size and cur:
                chunks.append({"source": source, "page": i + 1, "text": " ".join(cur)})
                cur = cur[-overlap_lines:]
                length = sum(len(x) + 1 for x in cur)
            cur.append(line)
            length += len(line) + 1
        if cur:
            chunks.append({"source": source, "page": i + 1, "text": " ".join(cur)})
    return chunks

if __name__ == "__main__":
    all_chunks = []
    from pathlib import Path
    data = Path(__file__).parent / "data"
    all_chunks += load_chunks(data / "hdfc_fy26.pdf", "HDFC FY26")
    all_chunks += load_chunks(data / "hdfc_fy25.pdf", "HDFC FY25")
    print("Total chunks:", len(all_chunks))
    print(all_chunks[500])
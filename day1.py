import pymupdf
from llm import ask

doc = pymupdf.open("data/hdfc_fy26.pdf")
# print("Total pages:", len(doc))

page_no = 86  # change until you land on a page about NPA / asset quality
text = doc[page_no].get_text()
# print(text[:800])

question = str(input())
print(ask(f"Answer only from this page.\n\nPAGE:\n{text}\n\nQUESTION: {question}"))
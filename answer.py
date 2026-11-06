from search import search
from llm import ask

def answer(question, k=10):
    hits = search(question, k)
    context = "\n\n".join(
        f"[{h['source']} p.{h['page']}]\n{h['text']}" for h in hits
    )
    prompt = f"""You are a financial analyst assistant. Answer using ONLY the excerpts below.
Cite the source after each fact, like [HDFC FY26 p.248].
If the excerpts do not contain the answer, reply exactly: "I couldn't find this in the provided reports."
Do not guess or use outside knowledge.

EXCERPTS:
{context}

QUESTION: {question}"""
    return ask(prompt), hits

if __name__ == "__main__":
    questions = [
        "How did HDFC Bank's gross NPA ratio change from FY25 to FY26?",
        "What was the capital adequacy ratio in FY25?",
        "What is the CEO of ICICI Bank's salary?",
    ]
    for q in questions:
        print("Q:", q)
        print("A:", answer(q)[0])
        print("=" * 60)
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import run_agent
from citations import parse_citations

BASE = Path(__file__).parent
REQUEST_TIMEOUT = 60  # seconds; fail with 503 instead of hanging on rate limits

app = FastAPI(title="Financial Filings Analyst Agent")

# Simple per-IP rate limit so a public demo cannot use up the free API quota.
_requests = defaultdict(deque)


def too_many_requests(ip, limit=10, window=60):
    now = time.time()
    q = _requests[ip]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        return True
    q.append(now)
    return False


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(body: Question, request: Request):
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please type a question.")
    if len(question) > 500:
        raise HTTPException(status_code=400, detail="Question is too long (max 500 characters).")

    ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0].strip()
    if too_many_requests(ip):
        raise HTTPException(status_code=429, detail="Too many questions. Please wait a minute.")

    try:
        answer, trace = run_agent(question, timeout=REQUEST_TIMEOUT)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="The model is busy right now. Please try again.")

    citations = [f"{src} p.{page}" for src, page in parse_citations(answer)]
    return {
        "answer": answer,
        "citations": citations,
        "tools_used": [t["tool"] for t in trace],
    }


app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/")
def home():
    return FileResponse(BASE / "static" / "index.html")

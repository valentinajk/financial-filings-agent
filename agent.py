import threading
import time
from google.genai import types, errors
from llm import client, MODEL
from tools import search_reports, compare_years, percent_change, difference, thousands_to_crore

TOOLS = {f.__name__: f for f in [search_reports, compare_years, percent_change, difference, thousands_to_crore]}

SYSTEM = """You are a financial analyst assistant for HDFC Bank's annual reports.
You can only see two reports: HDFC FY25 (year ended March 31, 2025) and HDFC FY26 (year ended March 31, 2026).

Rules:
1. Find facts only with the search tools. Never use outside knowledge.
2. For questions comparing years or asking how something changed, use compare_years.
3. For any percentage change or difference, use percent_change or difference. Never calculate yourself.
4. Cite every fact like [HDFC FY26 p.248], citing the page the figure itself is printed on. Write each page as its own citation, e.g. [HDFC FY26 p.45] [HDFC FY26 p.247], never [HDFC FY26 p.45, 247]. State units (crore, or thousands).
4b. Balance sheet tables are in thousands (` in '000); highlights and discussion pages are in crore. Prefer a figure that is already printed in crore. To convert thousands to crore, use thousands_to_crore, never by hand. If the digits in a table row look garbled or inconsistent, say the figure is unclear instead of guessing.
5. If the tools do not return the answer, or the question is about another company or a year outside FY25 and FY26, reply exactly: I couldn't find this in the provided reports.
6. Be concise."""

REFUSAL = "I couldn't find this in the provided reports."


MIN_GAP = 4.5  # seconds between calls; the free tier allows 15 requests per minute
_last_call = 0.0
_lock = threading.Lock()  # the API serves requests on several threads


def _sleep_within(seconds, deadline):
    """Sleep, but give up with RuntimeError if that would pass the deadline."""
    if deadline is not None and time.time() + seconds > deadline:
        raise RuntimeError("Model stayed busy, try again later")
    time.sleep(seconds)


def _generate(contents, config, deadline=None):
    global _last_call
    for _ in range(6):
        with _lock:
            wait = MIN_GAP - (time.time() - _last_call)
            if wait > 0:
                _sleep_within(wait, deadline)
            _last_call = time.time()
        try:
            return client.models.generate_content(model=MODEL, contents=contents, config=config)
        except errors.ServerError:
            print("Server busy, retrying in 15s...")
            _sleep_within(15, deadline)
        except errors.ClientError as e:
            if getattr(e, "code", None) == 429:
                print("Rate limit reached, waiting 60s...")
                _sleep_within(60, deadline)
            else:
                raise
    raise RuntimeError("Model stayed busy, try again later")


def run_agent(question, max_steps=6, timeout=None):
    """Run the agent loop. Returns (answer_text, trace) where trace lists the tool calls made.

    timeout: seconds before giving up with RuntimeError instead of waiting out
    rate limits. None (used by the evaluation) waits as long as needed."""
    deadline = time.time() + timeout if timeout else None
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM,
        tools=list(TOOLS.values()),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        temperature=0,
    )
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]
    trace = []

    for _ in range(max_steps):
        resp = _generate(contents, config, deadline)
        if not resp.candidates or not resp.candidates[0].content or not resp.candidates[0].content.parts:
            return REFUSAL, trace
        model_content = resp.candidates[0].content
        calls = [p.function_call for p in model_content.parts if p.function_call]

        if not calls:
            return resp.text or REFUSAL, trace

        contents.append(model_content)
        replies = []
        for call in calls:
            args = dict(call.args) if call.args else {}
            try:
                result = TOOLS[call.name](**args)
            except Exception as e:
                result = f"Tool error: {e}"
            trace.append({"tool": call.name, "args": args})
            replies.append(types.Part.from_function_response(
                name=call.name, response={"result": result}))
        contents.append(types.Content(role="user", parts=replies))

    return "I couldn't complete this within the step limit.", trace


if __name__ == "__main__":
    for q in [
        "How did HDFC Bank's gross NPA ratio change from FY25 to FY26, in percentage points and in percent?",
        "What were total advances at March 31, 2026?",
        "What is the CEO of ICICI Bank's salary?",
    ]:
        print("Q:", q)
        answer, trace = run_agent(q)
        print("A:", answer)
        print("Tools used:", [t["tool"] for t in trace])
        print("=" * 60)

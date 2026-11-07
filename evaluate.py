"""Run the test set against the agent (default) or the plain RAG pipeline.

    python evaluate.py                -> agent
    python evaluate.py rag            -> plain RAG (answer.py)
    python evaluate.py rescore agent  -> re-score saved eval_results_agent.json
                                         without calling the model

Metrics:
  Answer accuracy  : the answer contains an expected number (or a refusal when NOT_FOUND)
  Citation valid   : the cited pages really contain the figures the answer relies on.
                     That is `cite_values` from the test set when given (for calculated
                     answers such as a percentage change, the input figures), otherwise
                     `expected`. Every value in cite_values must appear on a cited page.
"""
import json
import re
import sys
import time
from pathlib import Path

from citations import parse_citations
from search import DOCS, METAS

BASE = Path(__file__).parent

# All chunk text for each (source, page), so citations can be checked against the real page.
PAGES = {}
for d, m in zip(DOCS, METAS):
    PAGES.setdefault((m["source"], m["page"]), []).append(d)


def norm(s):
    # Drop thousands separators only between digits. Keep spaces, so that
    # adjacent numbers such as "14.3 1.94" do not merge into "14.31.94".
    return re.sub(r"(?<=\d),(?=\d)", "", s).replace("’", "'").lower()


def has_number(text, expected):
    options = expected if isinstance(expected, list) else [expected]
    for e in options:
        pattern = r"(?<![\d.])" + re.escape(norm(e)) + r"(?!\d)"
        if re.search(pattern, norm(text)):
            return True
    return False


def citation_valid(answer_text, test):
    cited = [" ".join(PAGES.get(c, [])) for c in parse_citations(answer_text)]
    cited = [p for p in cited if p]
    if not cited:
        return False
    if "cite_values" in test:
        # each input figure must be printed on at least one cited page
        return all(any(has_number(p, v) for p in cited) for v in test["cite_values"])
    return any(has_number(p, test["expected"]) for p in cited)


def score(test, text, tools_used):
    if test["expected"] == "NOT_FOUND":
        correct = "couldn't find" in norm(text)
        cite_ok = None
    else:
        correct = has_number(text, test["expected"])
        cite_ok = citation_valid(text, test)
    return {
        "question": test["question"], "correct": correct, "citation_valid": cite_ok,
        "tools_used": tools_used, "answer": text,
    }


def summarize(results, mode):
    n = len(results)
    numeric = [r for r in results if r["citation_valid"] is not None]
    print()
    print(f"Mode:              {mode}")
    print(f"Answer accuracy:   {sum(r['correct'] for r in results)}/{n}")
    print(f"Citation valid:    {sum(r['citation_valid'] for r in numeric)}/{len(numeric)} (numeric questions only)")


def main():
    args = sys.argv[1:]
    tests = json.load(open(BASE / "test_set.json", encoding="utf-8"))

    if args and args[0] == "rescore":
        mode = args[1] if len(args) > 1 else "agent"
        path = BASE / f"eval_results_{mode}.json"
        saved = {r["question"]: r for r in json.load(open(path, encoding="utf-8"))}
        results = [score(t, saved[t["question"]]["answer"], saved[t["question"]]["tools_used"])
                   for t in tests if t["question"] in saved]
        for r in results:
            print(("PASS" if r["correct"] else "FAIL"),
                  "| cite", {True: "ok ", False: "BAD", None: "-  "}[r["citation_valid"]],
                  "|", r["question"])
        summarize(results, f"{mode} (rescored)")
        return

    mode = args[0] if args else "agent"
    if mode == "agent":
        from agent import run_agent

        def get_answer(question):
            text, trace = run_agent(question)
            return text, [t["tool"] for t in trace]
    else:
        from answer import answer

        def get_answer(question):
            text, _hits = answer(question)
            return text, []

    results = []
    for t in tests:
        r = score(t, *get_answer(t["question"]))
        results.append(r)
        print(("PASS" if r["correct"] else "FAIL"), "|", t["question"], "|", r["tools_used"])
        time.sleep(2)

    summarize(results, mode)
    json.dump(results, open(BASE / f"eval_results_{mode}.json", "w", encoding="utf-8"), indent=2)


if __name__ == "__main__":
    main()

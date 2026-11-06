import json, re, time
from answer import answer

tests = json.load(open("test_set.json"))

def norm(s):
    return s.replace(",", "").replace(" ", "").replace("’", "'").lower()

def has_number(text, expected):
    options = expected if isinstance(expected, list) else [expected]
    for e in options:
        pattern = r"(?<![\d.])" + re.escape(norm(e)) + r"(?!\d)"
        if re.search(pattern, norm(text)):
            return True
    return False

results = []
for t in tests:
    text, hits = answer(t["question"])
    if t["expected"] == "NOT_FOUND":
        correct = "couldn'tfind" in norm(text)
        cited = True
        retrieved = True
    else:
        correct = has_number(text, t["expected"])
        cited = norm(t["page"]) in norm(text)
        retrieved = any(
            norm(f"{h['source'].replace('HDFC ', '')} p.{h['page']}") == norm(t["page"])
            for h in hits
        )
    results.append({"question": t["question"], "correct": correct,
                    "cited": cited, "retrieved": retrieved, "answer": text})
    print(("PASS" if correct else "FAIL"), "|", t["question"])
    time.sleep(2)

n = len(results)
print()
print(f"Answer accuracy:   {sum(r['correct'] for r in results)}/{n}")
print(f"Correct citation:  {sum(r['cited'] for r in results)}/{n}")
print(f"Right page found:  {sum(r['retrieved'] for r in results)}/{n}")
json.dump(results, open("eval_results.json", "w"), indent=2)
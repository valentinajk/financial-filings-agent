import json
from search import search

for r in json.load(open("eval_results.json")):
    if not r["correct"]:
        print("Q:", r["question"])
        print("A:", r["answer"])
        for h in search(r["question"], 10):
            print("  ", h["source"], "p.", h["page"], "|", h["text"][:100].replace("\n", " "))
        print()
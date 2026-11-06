from answer import answer

questions = [
    "What was HDFC Bank's net interest margin in FY26?",
    "What was the standalone net profit in FY26?",
    "What was the net NPA ratio at March 31, 2025?",
    "How many branches did the bank have at March 31, 2026?",
    "What was the dividend per share recommended for FY25?",
    "What were total deposits at March 31, 2026?",
    "What was the gross NPA ratio at March 31, 2026?",
    "What was the capital adequacy ratio at March 31, 2025?",
    "What is the CEO of ICICI Bank's salary?",
    "What was HDFC Bank's return on assets in FY26?",
]

for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")
    print("   ", answer(q)[0].replace("\n", " "))
    print()
import ollama
import csv
import time
import os
from datetime import datetime

MODEL = "llama3.2"

# Two prompt versions to compare
PROMPTS = {
    "v1_basic": "You are a helpful assistant.",
    "v2_project": "You are a helpful assistant. Answer in one short sentence. "
                  "Extra info: this project is built using Python and Ollama."
}

with open("tests.csv", encoding="utf-8") as f:
    tests = list(csv.DictReader(f))

RESULTS_FILE = "eval_results.csv"
if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["time", "prompt", "score", "avg_seconds"])

for name, system_prompt in PROMPTS.items():
    print(f"\n=== Testing {name} ===")
    passed = 0
    total_seconds = 0

    for test in tests:
        start = time.time()
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test["question"]}
            ]
        )
        total_seconds += time.time() - start
        answer = response["message"]["content"]

        ok = test["expected"].lower() in answer.lower()
        if ok:
            passed += 1
        print("PASS ✅" if ok else "FAIL ❌", "-", test["question"])

    score = round(passed / len(tests) * 100)
    avg = round(total_seconds / len(tests), 2)
    print(f"Score: {score}% | Avg time: {avg}s")

    # Save the result for the dashboard
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, score, avg]
        )
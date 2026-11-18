import ollama
import csv
import time
import os
from datetime import datetime

LOG_FILE = "logs.csv"

# Create the log file with headings (only the first time)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            ["time", "question", "answer", "seconds", "input_tokens", "output_tokens"]
        )

print("Chatbot ready! Type 'bye' to exit.\n")

while True:
    question = input("You: ")
    if question.lower() == "bye":
        print("Goodbye!")
        break

    start = time.time()
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": question}]
    )
    seconds = round(time.time() - start, 2)

    answer = response["message"]["content"]
    input_tokens = response.get("prompt_eval_count", 0)
    output_tokens = response.get("eval_count", 0)

    print("AI:", answer)
    print(f"[{seconds}s | {input_tokens} in / {output_tokens} out tokens]\n")

    # Save this chat to the log file
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(
            [datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             question, answer, seconds, input_tokens, output_tokens]
        )
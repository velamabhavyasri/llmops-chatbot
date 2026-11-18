import streamlit as st
import ollama
import pandas as pd
import csv
import time
import os
from datetime import datetime

MODEL = "llama3.2"
SYSTEM_PROMPT = ("You are a helpful assistant. Answer in one short sentence. "
                 "Extra info: this project is built using Python and Ollama.")
LOG_FILE = "logs.csv"
FEEDBACK_FILE = "feedback.csv"

st.set_page_config(page_title="LLMOps Project", layout="wide")
st.title("🤖 My LLMOps Project")


# ---------- HELPER FUNCTIONS ----------
def save_row(file, headers, row):
    """Add one row to a CSV file (creates the file with headers if needed)."""
    new_file = not os.path.exists(file)
    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(headers)
        writer.writerow(row)


def save_feedback(msg_id):
    """Runs when the user clicks 👍 or 👎."""
    value = st.session_state[f"fb_{msg_id}"]
    if value is None:
        return
    msg = next(m for m in st.session_state.messages if m.get("id") == msg_id)
    save_row(FEEDBACK_FILE, ["time", "answer", "rating"],
             [datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              msg["content"], "good" if value == 1 else "bad"])


# ---------- MEMORY ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

tab1, tab2 = st.tabs(["💬 Chat", "📊 Dashboard"])

# ---------- CHAT TAB ----------
with tab1:
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

    # Show all previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                st.caption(f"⏱ {msg['seconds']}s | tokens: {msg['tokens']}")
                st.feedback("thumbs", key=f"fb_{msg['id']}",
                            on_change=save_feedback, args=(msg["id"],))

    question = st.chat_input("Ask something...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})

        # Send the whole conversation, so the AI remembers it
        history = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        try:
            with st.spinner("Thinking..."):
                start = time.time()
                response = ollama.chat(model=MODEL, messages=history)
                seconds = round(time.time() - start, 2)
        except Exception:
            st.error("⚠️ Can't reach the AI. Is Ollama running? "
                     "Open the Ollama app and try again.")
            st.session_state.messages.pop()  # remove the unanswered question
            st.stop()

        answer = response["message"]["content"]
        in_tokens = response.get("prompt_eval_count", 0)
        out_tokens = response.get("eval_count", 0)

        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "seconds": seconds, "tokens": out_tokens,
            "id": str(time.time())
        })

        save_row(LOG_FILE,
                 ["time", "question", "answer", "seconds",
                  "input_tokens", "output_tokens"],
                 [datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  question, answer, seconds, in_tokens, out_tokens])
        st.rerun()

# ---------- DASHBOARD TAB ----------
with tab2:
    if os.path.exists(LOG_FILE):
        logs = pd.read_csv(LOG_FILE)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total chats", len(logs))
        c2.metric("Avg time (s)", round(logs["seconds"].mean(), 2))
        c3.metric("Total tokens",
                  int(logs["input_tokens"].sum() + logs["output_tokens"].sum()))

        if os.path.exists(FEEDBACK_FILE):
            fb = pd.read_csv(FEEDBACK_FILE)
            good = round((fb["rating"] == "good").mean() * 100)
            c4.metric("👍 Happy users", f"{good}%")
        else:
            c4.metric("👍 Happy users", "No ratings yet")

        st.subheader("Response time per chat")
        st.line_chart(logs["seconds"])

        st.subheader("Recent chats")
        st.dataframe(logs.tail(10))
    else:
        st.info("No chats yet. Ask something in the Chat tab!")

    if os.path.exists("eval_results.csv"):
        st.subheader("Prompt test scores")
        evals = pd.read_csv("eval_results.csv")
        st.bar_chart(evals.groupby("prompt")["score"].last())
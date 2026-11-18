\# 🤖 LLMOps Chatbot Project



A local AI chatbot with LLMOps features, built with Python, Ollama, and Streamlit.



\## Features

\- 💬 AI chatbot with conversation memory (llama3.2 via Ollama)

\- 📝 Logging of every chat (time, question, answer, speed, tokens)

\- 🧪 Automatic testing with a score

\- ⚖️ Prompt comparison (v1: 90% vs v2: 100%)

\- 👍👎 User feedback

\- ⚠️ Error handling

\- 📊 Dashboard with charts



\## How to run

1\. Install Ollama and run: `ollama pull llama3.2`

2\. Install libraries: `pip install -r requirements.txt`

3\. Start the app: `streamlit run app.py`

4\. Run the tests: `python evaluate.py`


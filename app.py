import streamlit as st
import requests

OPENAI_API_URL = "http://localhost:11434/v1/chat/completions"
MODEL_NAME = "gemma3:12b-it-qat"

# Load system prompt
with open("root_cause_prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

def call_llm(log_text):
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": log_text}
        ],
        "temperature": 0
    }

    response = requests.post(OPENAI_API_URL, json=data, headers=headers)
    result = response.json()
    try:
        return result["choices"][0]["message"]["content"].strip()
    except:
        return "Error in LLM response"

def extract_relevant_logs(log_text):
    # Simple filter for lines with errors/warnings
    keywords = ["error", "exception", "fail", "fatal", "warn"]
    lines = log_text.splitlines()
    relevant = [line for line in lines if any(k in line.lower() for k in keywords)]
    return "\n".join(relevant[:100])  # limit output for speed

# Streamlit UI
st.set_page_config(page_title="LogSage", page_icon="🧠")
st.title("🧠 LogSage - AI Log Analyzer")

uploaded_file = st.file_uploader("📂 Upload a .log or .txt file", type=["log", "txt"])

if uploaded_file:
    log_text = uploaded_file.read().decode("utf-8", errors="ignore")
    st.subheader("📄 Raw Log (First 30 Lines)")
    st.code("\n".join(log_text.splitlines()[:30]), language="text")

    if st.button("🧠 Analyze Logs"):
        with st.spinner("Extracting relevant logs..."):
            relevant_logs = extract_relevant_logs(log_text)

        st.subheader("🔎 Relevant Log Lines")
        st.code(relevant_logs or "No relevant logs found.", language="text")

        with st.spinner("Generating root cause analysis with LLM..."):
            llm_response = call_llm(relevant_logs or log_text)

        st.subheader("📊 AI Root Cause Summary")
        st.markdown(llm_response)

st.markdown("---")
st.caption("Prototype by LogSage: LLM-based log analysis.")

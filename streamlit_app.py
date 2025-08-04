# Fusion Oracle Omniverse — Apex Cosmic Code Version

import streamlit as st
import pandas as pd
import numpy as np
import docx, json, os
import google.generativeai as genai
import openai
import speech_recognition as sr
from dotenv import load_dotenv

# ==== LOAD KEYS SECURELY ====
load_dotenv()
GEMINI_API_KEY = os.getenv("AIzaSyB710cbSHrgzOdToOkyIssd-rYOp5Si6Ks
")
OPENAI_API_KEY = os.getenv("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
")

# ==== GEMINI CONFIG ====
genai_model_name = "models/gemini-1.5-pro-latest"
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(genai_model_name)
else:
    st.warning("⚠️ Gemini API key not found.")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ==== STYLING ====
st.markdown("""
    <style>
    .stTextInput, .stTextArea { border: 2px solid #00ffc3; border-radius: 10px; }
    .stButton>button { background-color: #1e1e88; color: white; border-radius: 12px; }
    .stExpanderHeader { font-weight: bold; color: #00ffc3; }
    </style>
""", unsafe_allow_html=True)

# ==== PAGE CONFIG ====
st.set_page_config(page_title="Fusion Oracle Omniverse", page_icon="👑", layout="wide")

st.sidebar.image("assets/avatar.png", width=90)
st.sidebar.title("Fusion Oracle Omniverse")
st.sidebar.markdown("---")

# ==== SESSION STATE ====
if "oracle_universe" not in st.session_state:
    st.session_state["oracle_universe"] = {}

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# ==== PROMPT FORMATTING ====
def format_prompt(context, user_prompt):
    return f"""You are a top-tier Oracle AI Copilot.\n\nContext:\n{context}\n\nUser Prompt:\n{user_prompt}"""

# ==== VOICE INPUT ====
def listen_to_mic():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            audio = r.listen(source)
            return r.recognize_google(audio)
    except Exception as e:
        return f"Voice error: {e}"

# ==== FILE INGESTION ====
def ingest(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file.type == "application/json":
        return json.dumps(json.load(file), indent=2)
    elif file.type == "application/sql" or file.name.endswith(('.sql', '.pls', '.plsql')):
        return file.read().decode("utf-8")
    else:
        return "Unsupported file type. Try .txt, .sql, .docx, .json"

# ==== UNIVERSAL AI ====
def omni_ai(prompt):
    context = "\n\n".join(st.session_state["oracle_universe"].values())
    full_prompt = format_prompt(context, prompt)
    try:
        if model:
            resp = model.generate_content(full_prompt)
            answer = resp.text if hasattr(resp, "text") else str(resp)
        else:
            raise Exception("Gemini unavailable")
    except Exception as e:
        st.warning(f"Gemini error: {e}")
        if OPENAI_API_KEY:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"Context:\n{context}"},
                        {"role": "user", "content": prompt}
                    ]
                )
                answer = response.choices[0].message.content
            except Exception as ex:
                answer = f"OpenAI fallback error: {ex}"
        else:
            answer = "No AI engine available."
    st.session_state.chat_log.append((prompt, answer))
    return answer

# ==== SIDEBAR ====
group_dict = {
    "Core": ["Central", "Diagnoser", "Copilot", "Upload", "Memory", "SQL Runner", "PL/SQL Runner", "Search"],
    "Oracle Cloud": ["Logs", "ERP", "HCM", "SCM", "OIC", "Jobs", "Analytics"],
    "Docs & Knowledge": ["Manuals", "Whitepapers", "Exported Data", "PLSQL Docs"]
}
selected_group = st.sidebar.radio("Group", list(group_dict.keys()))
tabs = st.tabs(group_dict[selected_group])

# ==== TAB RENDERER ====
def render_tab(label):
    if label == "Central":
        st.header("🌟 Central Command – Oracle Universe")
        st.metric("Uploaded Artifacts", len(st.session_state["oracle_universe"]))
        st.success("Every document, log, SQL, or knowledge file you upload expands this universe.")
    elif label == "Diagnoser":
        st.header("🩺 Oracle Diagnoser")
        q = st.text_area("Paste any Oracle error, log, stack, or JIRA text:")
        if st.button("Diagnose and Auto-Fix") and q:
            st.info(omni_ai(f"Diagnose and suggest a fix: {q}"))
    elif label == "Copilot":
        st.header("🤖 Oracle Copilot (All Knowledge)")
        q = st.text_input("Ask anything about Oracle SQL, PLSQL, Cloud, logs, etc.")
        if st.button("Ask Copilot") and q:
            st.info(omni_ai(q))
        if st.button("🎤 Voice Ask"):
            q = listen_to_mic()
            st.text(q)
            st.info(omni_ai(q))
    elif label == "Upload":
        st.header("📤 Upload Oracle Docs, Logs, SQL, Data Dumps, Models")
        files = st.file_uploader("Upload anything Oracle: logs, .sql, .docx, .json, .txt", accept_multiple_files=True)
        if files:
            for f in files:
                txt = ingest(f)
                st.session_state["oracle_universe"][f.name] = txt
                st.success(f"Ingested: {f.name}")
        st.download_button("📥 Export Memory", json.dumps(st.session_state["oracle_universe"], indent=2), file_name="oracle_universe.json")
    elif label == "Memory":
        st.header("🧠 Full Oracle Session Memory")
        for k, v in st.session_state["oracle_universe"].items():
            with st.expander(k):
                st.text(v[:2000])
    elif label == "SQL Runner":
        st.header("🗃️ Oracle SQL Runner")
        sql = st.text_area("Enter SQL")
        if st.button("Explain/Optimize SQL"):
            st.info(omni_ai(f"Explain or optimize this SQL: {sql}"))
    elif label == "PL/SQL Runner":
        st.header("🔢 Oracle PL/SQL Runner")
        plsql = st.text_area("Enter PL/SQL block")
        if st.button("Explain/Optimize PL/SQL"):
            st.info(omni_ai(f"Explain or optimize this PL/SQL: {plsql}"))
    elif label == "Search":
        st.header("🔎 Search All Docs/Logs/SQL")
        s = st.text_input("Search text:")
        for k, v in st.session_state["oracle_universe"].items():
            if not s or s.lower() in v.lower():
                with st.expander(k):
                    st.text(v[:2000])
    else:
        st.header(f"🌀 {label}")
        st.info("Upload your relevant Oracle artifacts and ask anything about them.")

# ==== TABS ==== 
for i, label in enumerate(group_dict[selected_group]):
    with tabs[i]:
        render_tab(label)

# ==== CHAT LOG ====
st.markdown("---")
st.subheader("🧾 Chat History")
for q, a in reversed(st.session_state.chat_log):
    with st.expander(f"Q: {q}"):
        st.markdown(f"**A:** {a}")

st.markdown("---")
st.markdown("""
    <div style='text-align:center; color:#e0e0e0; font-weight:bold'>
    Fusion Oracle Omniverse — All docs, logs, code, models, data. No limits.<br>
    &copy; Hemanth Oracle Cosmic AI
    </div>
""", unsafe_allow_html=True)

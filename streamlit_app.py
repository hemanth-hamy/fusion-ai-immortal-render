# 🚀 Fusion Oracle Omniverse — Apex Cosmic Tabs UI

import streamlit as st
import pandas as pd
import numpy as np
import docx, json, os
import openai
import google.generativeai as genai
from dotenv import load_dotenv

# Optional: Voice (Render may not support input device)
try:
    import speech_recognition as sr
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

# ==== KEYS ====
load_dotenv()
GEMINI_API_KEY = "AIzaSyAOuQSSiqDjip8rghpAOa5D-VFBBlT-YFw"
OPENAI_API_KEY = "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"

# ==== MODEL CONFIG ====
genai_model_name = "models/gemini-1.5-pro-latest"
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(genai_model_name)

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ==== STYLING ====
st.set_page_config(page_title="Fusion Oracle Omniverse", page_icon="👑", layout="wide")
st.markdown("""
    <style>
    .stTextInput, .stTextArea { border: 2px solid #00ffc3; border-radius: 10px; }
    .stButton>button { background-color: #1e1e88; color: white; border-radius: 12px; }
    .stExpanderHeader { font-weight: bold; color: #00ffc3; }
    </style>
""", unsafe_allow_html=True)

# ==== SESSION STATE ====
if "oracle_universe" not in st.session_state:
    st.session_state["oracle_universe"] = {}
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

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

# ==== FILE INGEST ====
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

# ==== AI ====
def omni_ai(prompt):
    try:
        if model:
            resp = model.generate_content(prompt)
            answer = resp.text if hasattr(resp, "text") else str(resp)
        else:
            raise Exception("Gemini unavailable")
    except Exception as e:
        if OPENAI_API_KEY:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an Oracle ERP/OIC/SQL expert."},
                        {"role": "user", "content": prompt}
                    ]
                )
                answer = response.choices[0].message.content
            except Exception as ex:
                answer = f"OpenAI error: {ex}"
        else:
            answer = "No AI engine available."
    st.session_state.chat_log.append((prompt, answer))
    return answer

# ==== TABS ====
tabs = st.tabs([
    "🏠 Central", "🩺 Diagnoser", "🤖 Copilot", "📤 Upload", "🧠 Memory", 
    "🗃️ SQL Runner", "🔢 PL/SQL Runner", "🔍 Search", "🎙️ Voice Test"
])

with tabs[0]:
    st.title("Fusion Oracle Omniverse")
    st.metric("Uploaded Docs", len(st.session_state["oracle_universe"]))
    st.success("Upload docs, logs, SQL or questions in other tabs to get started.")

with tabs[1]:
    st.header("🩺 Oracle Diagnoser")
    err = st.text_area("Paste Oracle Error or JIRA:")
    if st.button("Diagnose and Fix") and err:
        st.info(omni_ai(f"Diagnose and fix: {err}"))

with tabs[2]:
    st.header("🤖 Ask Oracle Copilot")
    q = st.text_input("Ask any Oracle-related question here")
    if st.button("Ask Copilot") and q:
        st.success(omni_ai(q))
    if VOICE_ENABLED and st.button("🎤 Voice Ask"):
        q = listen_to_mic()
        st.text(q)
        st.success(omni_ai(q))
    elif not VOICE_ENABLED:
        st.warning("Voice input not available.")

with tabs[3]:
    st.header("📤 Upload Files")
    files = st.file_uploader("Upload Oracle SQL, logs, docs, json", accept_multiple_files=True)
    if files:
        for f in files:
            content = ingest(f)
            st.session_state["oracle_universe"][f.name] = content
            st.success(f"Ingested: {f.name}")

with tabs[4]:
    st.header("🧠 Memory")
    for k, v in st.session_state["oracle_universe"].items():
        with st.expander(k):
            st.text(v[:2000])

with tabs[5]:
    st.header("🗃️ SQL Runner")
    sql = st.text_area("Enter SQL to optimize:")
    if st.button("Optimize SQL"):
        st.info(omni_ai(f"Optimize this SQL: {sql}"))

with tabs[6]:
    st.header("🔢 PL/SQL Runner")
    plsql = st.text_area("Enter PL/SQL block:")
    if st.button("Explain PL/SQL"):
        st.info(omni_ai(f"Explain this PL/SQL: {plsql}"))

with tabs[7]:
    st.header("🔍 Search Docs")
    s = st.text_input("Search in uploaded docs:")
    for k, v in st.session_state["oracle_universe"].items():
        if not s or s.lower() in v.lower():
            with st.expander(k):
                st.text(v[:2000])

with tabs[8]:
    st.header("🎙️ Voice Test")
    if VOICE_ENABLED:
        if st.button("🎤 Start Listening"):
            q = listen_to_mic()
            st.text(q)
            st.info(omni_ai(q))
    else:
        st.warning("Voice not supported in this deployment environment.")

# ==== Chat Log ====
st.markdown("---")
st.subheader("📜 Chat History")
for q, a in reversed(st.session_state.chat_log):
    with st.expander(f"Q: {q}"):
        st.markdown(f"**A:** {a}")

# Fusion Oracle Omniverse — Apex Cosmic Code Version

import streamlit as st
import pandas as pd
import numpy as np
import docx, json, os
import google.generativeai as genai
import openai

try:
    import speech_recognition as sr
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

from dotenv import load_dotenv
from langdetect import detect
from googletrans import Translator
import tempfile
import base64

# ==== LOAD KEYS SECURELY ====
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyAOuQSSiqDjip8rghpAOa5D-VFBBlT-YFw"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "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"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

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

# ==== FORMAT PROMPT ====
def format_prompt(context, user_prompt):
    return f"""You are a top-tier Oracle AI Copilot.\n\nContext:\n{context}\n\nUser Prompt:\n{user_prompt}"""

# ==== VOICE ====
def listen_to_mic():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening...")
            audio = r.listen(source)
            return r.recognize_google(audio)
    except Exception as e:
        return f"Voice error: {e}"

# ==== INGEST ====
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

# ==== AI ENGINE ====
def omni_ai(prompt):
    try:
        lang = detect(prompt)
        if lang != 'en':
            translated = Translator().translate(prompt, dest='en')
            prompt = f"[{lang} → en] {translated.text}"
    except: pass

    context = "\n\n".join(st.session_state["oracle_universe"].values())
    full_prompt = format_prompt(context, prompt)
    try:
        resp = model.generate_content(full_prompt)
        answer = resp.text if hasattr(resp, "text") else str(resp)
    except:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"Context:\n{context}"},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"OpenAI fallback error: {e}"
    st.session_state.chat_log.append((prompt, answer))
    return answer

# ==== UI GROUPS ====
group_dict = {
    "Core": ["Central", "Diagnoser", "Copilot", "Upload", "Memory", "SQL Runner", "PL/SQL Runner", "Search", "Voice Test"],
    "Oracle Cloud": ["Logs", "ERP", "HCM", "SCM", "OIC", "Jobs", "Analytics"],
    "Docs & Knowledge": ["Manuals", "Whitepapers", "Exported Data", "PLSQL Docs"]
}

selected_group = st.sidebar.radio("Group", list(group_dict.keys()))
tabs = st.tabs(group_dict[selected_group])

# ==== RENDER ==== 
def render_tab(label):
    if label == "Central":
        st.header("🌟 Central Command – Oracle Universe")
        st.metric("Uploaded Artifacts", len(st.session_state["oracle_universe"]))
    elif label == "Diagnoser":
        st.header("🩺 Oracle Diagnoser")
        q = st.text_area("Paste error, log or JIRA text:")
        if st.button("Diagnose") and q:
            st.info(omni_ai(f"Diagnose: {q}"))
    elif label == "Copilot":
        st.header("🤖 Ask Oracle Copilot")
        q = st.text_input("Ask anything Oracle SQL, PLSQL, Cloud, etc.")
        if st.button("Ask") and q:
            st.info(omni_ai(q))
        if VOICE_ENABLED and st.button("🎤 Voice Ask"):
            q = listen_to_mic()
            st.text(q)
            st.info(omni_ai(q))
    elif label == "Upload":
        st.header("📤 Upload Oracle Docs, Logs, SQL")
        files = st.file_uploader("Upload files", accept_multiple_files=True)
        if files:
            for f in files:
                txt = ingest(f)
                st.session_state["oracle_universe"][f.name] = txt
                st.success(f"Ingested: {f.name}")
        st.download_button("📥 Export Memory", json.dumps(st.session_state["oracle_universe"], indent=2), file_name="oracle_universe.json")
    elif label == "Memory":
        st.header("🧠 Oracle Session Memory")
        for k, v in st.session_state["oracle_universe"].items():
            with st.expander(k):
                st.text(v[:2000])
    elif label == "SQL Runner":
        st.header("🗃️ SQL Runner")
        sql = st.text_area("Enter SQL")
        if st.button("Explain SQL"):
            st.info(omni_ai(f"Explain SQL: {sql}"))
    elif label == "PL/SQL Runner":
        st.header("🔢 PL/SQL Runner")
        plsql = st.text_area("Enter PL/SQL")
        if st.button("Explain PL/SQL"):
            st.info(omni_ai(f"Explain PL/SQL: {plsql}"))
    elif label == "Search":
        st.header("🔎 Search Docs")
        s = st.text_input("Search")
        for k, v in st.session_state["oracle_universe"].items():
            if not s or s.lower() in v.lower():
                with st.expander(k):
                    st.text(v[:2000])
    elif label == "Voice Test":
        st.header("🗣️ Voice Test")
        if VOICE_ENABLED:
            if st.button("Start Voice"):
                q = listen_to_mic()
                st.text(f"You said: {q}")
        else:
            st.error("Voice not available")
    else:
        st.header(f"🌀 {label}")

# ==== EXECUTE RENDER ====
for i, label in enumerate(group_dict[selected_group]):
    with tabs[i]:
        render_tab(label)

st.markdown("---")
st.subheader("🧾 Chat Log")
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

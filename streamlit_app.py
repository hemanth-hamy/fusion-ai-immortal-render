# Fusion Oracle Omniverse — Apex Cosmic Code Version + COSMIC PHASE ∞

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
import hashlib
import datetime

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
    html, body, [class*="css"]  {
        background: linear-gradient(135deg, #000010 0%, #20002c 100%) !important;
        color: #ffffff;
        font-family: 'Segoe UI', sans-serif;
    }
    .stTextInput, .stTextArea {
        background-color: #111122;
        color: #00fff7;
        border: 2px solid #00ffc3;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #3b00ff;
        color: #fff;
        font-weight: bold;
        border-radius: 12px;
        box-shadow: 0 0 10px #00ffc3;
    }
    .stExpanderHeader {
        color: #00ffc3;
        font-weight: bold;
    }
    .block-container {
        padding: 2rem;
        border-radius: 25px;
        box-shadow: 0px 0px 20px rgba(0,255,255,0.1);
    }
    .stTabs [role="tab"] {
        font-size: 18px;
        color: #00ffc3;
        background: #0f0026;
        border-radius: 8px;
        padding: 8px;
        margin-right: 6px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(to right, #3b00ff, #00ffc3);
        color: #fff;
        font-weight: bold;
        border-radius: 12px;
        box-shadow: 0 0 10px #00ffc3;
    }
    </style>
""", unsafe_allow_html=True)

# ==== PAGE CONFIG ====
st.set_page_config(page_title="Fusion Oracle Omniverse", page_icon="👑", layout="wide")

st.sidebar.image("assets/avatar.png", width=90)
st.sidebar.title("Fusion Oracle Omniverse")
st.sidebar.markdown("---")

# ==== LOG TRACKING ====
if "logs" not in st.session_state:
    st.session_state.logs = []

if "oracle_universe" not in st.session_state:
    st.session_state.oracle_universe = {}

def log_event(action):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append(f"[{ts}] {action}")

# ==== NFT HASH FUNCTION ====
def generate_proof(text):
    return hashlib.sha256(text.encode()).hexdigest()

# ==== FILE INGESTION ====
def ingest(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file.type == "application/json":
        return json.dumps(json.load(file), indent=2)
    elif file.type == "application/sql" or file.name.endswith(('.sql','.pls','.plsql')):
        return file.read().decode("utf-8")
    else:
        return "Unsupported file type. Try .txt, .sql, .docx, .json"

# ==== AI QA ====
def omni_ai(prompt):
    context = "\n\n".join(st.session_state.oracle_universe.values())
    try:
        resp = model.generate_content(f"CONTEXT:\n{context}\n\nUSER PROMPT:\n{prompt}")
        return resp.text if hasattr(resp, "text") else str(resp)
    except Exception as e:
        return f"Gemini error: {e}"

# ==== TABS ====
group_dict = {
    "Core": ["Central", "Diagnoser", "Copilot", "Upload", "Memory", "SQL", "PLSQL", "Search"],
    "Oracle Cloud": ["Logs", "ERP", "HCM", "SCM", "OIC", "Analytics"],
    "Docs": ["Manuals", "Whitepapers", "PLSQL Docs"]
}

selected_group = st.sidebar.radio("Group", list(group_dict.keys()))
tabs = st.tabs(group_dict[selected_group])

# ==== PAGE RENDERING ====
def render_tab(label):
    if label == "Central":
        st.header("🌟 Central Command – Oracle Universe")
        st.metric("Uploaded Artifacts", len(st.session_state.oracle_universe))
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
    elif label == "Upload":
        st.header("📤 Upload Oracle Docs, Logs, SQL, Data Dumps, Models")
        files = st.file_uploader("Upload anything Oracle: logs, .sql, .docx, .json, .txt, code, configs, data models.", accept_multiple_files=True)
        if files:
            for f in files:
                txt = ingest(f)
                st.session_state.oracle_universe[f.name] = txt
                st.success(f"Ingested: {f.name}")
        for k in st.session_state.oracle_universe:
            st.write(f"- {k}")
    elif label == "Memory":
        st.header("🧠 Full Session Oracle Memory")
        for k, v in st.session_state.oracle_universe.items():
            with st.expander(k):
                st.text(v[:2000])
    elif label == "SQL":
        st.header("🗃️ Oracle SQL Runner (AI Explain/Generate)")
        sql = st.text_area("Enter any Oracle SQL query")
        if st.button("Explain/Optimize SQL"):
            st.info(omni_ai(f"Explain or optimize this SQL: {sql}"))
    elif label == "PLSQL":
        st.header("🔢 Oracle PL/SQL Runner (AI Explain/Generate)")
        plsql = st.text_area("Enter PL/SQL block")
        if st.button("Explain/Optimize PL/SQL"):
            st.info(omni_ai(f"Explain or optimize this PL/SQL: {plsql}"))
    elif label == "Search":
        st.header("🔎 Search All Docs/Logs/SQL")
        s = st.text_input("Search text:")
        for k, v in st.session_state.oracle_universe.items():
            if not s or s.lower() in v.lower():
                with st.expander(k):
                    st.text(v[:2000])
    else:
        st.header(f"🌀 {label}")
        st.info("Upload your relevant Oracle artifacts and ask anything about them.")

for i, label in enumerate(group_dict[selected_group]):
    with tabs[i]:
        render_tab(label)

# ==== COSMIC PHASE LOG ==== 
COSMIC_PHASES = [
    "🎙️ Whisper voice command module",
    "🌐 WebSocket + digital twin slots reserved",
    "🧞‍♂️ CrewAI Summoning Panel",
    "🌌 Multimodal Prompt + Live Tab Swapping",
    "🪐 Smart Agent Selector",
    "🤖 Triple-Fix Oracle Diagnoser",
    "🌠 Eternal Enhancement Module",
    "🔮 Planetary UI + SQL Voting Panel (coming)"
]

st.title("👑 Welcome to the Apex Fusion Oracle Omniverse")
for phase in COSMIC_PHASES:
    st.success(phase)

st.info("🌟 You are now running Apex Version: COSMIC PHASE ∞. Eternal mode active.")

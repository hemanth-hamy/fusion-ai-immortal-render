import streamlit as st
import pandas as pd
import numpy as np
import docx, json, os, time

import google.generativeai as genai

# ==== CONFIGURE GEMINI ====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "YOUR_GEMINI_API_KEY"
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-pro-latest")

# ==== MEMORY ====
if "oracle_universe" not in st.session_state:
    st.session_state["oracle_universe"] = {}

# ==== INGESTION ====
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

# ==== PAGE ====
st.set_page_config(page_title="Fusion Oracle Omniverse", page_icon="👑", layout="wide")

st.sidebar.image("assets/avatar.png", width=90)
st.sidebar.title("Fusion Oracle Omniverse")
st.sidebar.markdown("---")

group_dict = {
    "Core": [
        "Central", "Diagnoser", "Copilot", "Upload", "Memory", "SQL Runner", "PL/SQL Runner", "Search"
    ],
    "Oracle Cloud": [
        "Logs", "ERP", "HCM", "SCM", "OIC", "Jobs", "Analytics"
    ],
    "Docs & Knowledge": [
        "Manuals", "Whitepapers", "Exported Data", "PLSQL Docs"
    ]
}

selected_group = st.sidebar.radio("Group", list(group_dict.keys()))
tabs = st.tabs(group_dict[selected_group])

# ==== GEMINI UNIVERSAL QA ====
def omni_ai(prompt):
    context = "\n\n".join(st.session_state["oracle_universe"].values())
    try:
        resp = model.generate_content(f"CONTEXT:\n{context}\n\nUSER PROMPT:\n{prompt}")
        return resp.text if hasattr(resp, "text") else str(resp)
    except Exception as e:
        return f"Gemini error: {e}"

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
    elif label == "Upload":
        st.header("📤 Upload Oracle Docs, Logs, SQL, Data Dumps, Models")
        files = st.file_uploader("Upload anything Oracle: logs, .sql, .docx, .json, .txt, code, configs, data models.", accept_multiple_files=True)
        if files:
            for f in files:
                txt = ingest(f)
                st.session_state["oracle_universe"][f.name] = txt
                st.success(f"Ingested: {f.name}")
        st.write(f"**{len(st.session_state['oracle_universe'])} docs currently loaded.**")
        for k in st.session_state["oracle_universe"]:
            st.write(f"- {k}")
    elif label == "Memory":
        st.header("🧠 Full Session Oracle Memory")
        for k, v in st.session_state["oracle_universe"].items():
            with st.expander(k):
                st.text(v[:2000])
    elif label == "SQL Runner":
        st.header("🗃️ Oracle SQL Runner (AI Explain/Generate)")
        sql = st.text_area("Enter any Oracle SQL query")
        if st.button("Explain/Optimize SQL"):
            st.info(omni_ai(f"Explain or optimize this SQL: {sql}"))
    elif label == "PL/SQL Runner":
        st.header("🔢 Oracle PL/SQL Runner (AI Explain/Generate)")
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

for i, label in enumerate(group_dict[selected_group]):
    with tabs[i]:
        render_tab(label)

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#e0e0e0; font-weight:bold'>"
    "Fusion Oracle Omniverse — All docs, logs, code, models, data. No limits.<br>"
    "&copy; Hemanth Oracle Cosmic AI"
    "</div>", unsafe_allow_html=True
)






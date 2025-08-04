# Fusion Oracle Omniverse — Apex Cosmic Version

import streamlit as st
import pandas as pd
import numpy as np
import docx, json, os
import openai
import google.generativeai as genai
from dotenv import load_dotenv

# ===== Optional: Voice (will fail gracefully on Render) =====
try:
    import speech_recognition as sr
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

# ==== Load Keys ====
load_dotenv()
GEMINI_API_KEY = "AIzaSyAOuQSSiqDjip8rghpAOa5D-VFBBlT-YFw"
OPENAI_API_KEY = "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"

# ==== Gemini Config ====
genai_model_name = "models/gemini-1.5-pro-latest"
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(genai_model_name)

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# ==== Streamlit UI Styling ====
st.set_page_config(page_title="Fusion Oracle Omniverse", page_icon="👑", layout="wide")
st.markdown("""
    <style>
    .stTextInput, .stTextArea { border: 2px solid #00ffc3; border-radius: 10px; }
    .stButton>button { background-color: #1e1e88; color: white; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Fusion Oracle Omniverse")
prompt = st.text_input("Ask anything about Oracle SQL, PLSQL, Cloud, logs, etc.")

# ==== Voice Support ====
if VOICE_ENABLED:
    if st.button("🎤 Voice Ask"):
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎙️ Listening...")
                audio = r.listen(source)
                prompt = r.recognize_google(audio)
                st.success(f"You said: {prompt}")
        except Exception as e:
            st.warning(f"Voice error: {e}")
else:
    st.warning("Voice input not available in this environment (e.g., Render).")

# ==== Ask Copilot Button ====
if st.button("Ask Copilot") and prompt:
    with st.spinner("Thinking..."):
        try:
            if model:
                response = model.generate_content(prompt)
                st.success(response.text if hasattr(response, "text") else str(response))
            else:
                raise Exception("Gemini unavailable.")
        except Exception as e:
            st.warning(f"Gemini error: {e}")
            if OPENAI_API_KEY:
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an Oracle ERP/OIC/SQL expert."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    st.success(response.choices[0].message.content)
                except Exception as oe:
                    st.error(f"OpenAI fallback error: {oe}")
            else:
                st.error("No valid API key for OpenAI fallback.")

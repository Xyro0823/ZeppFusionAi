import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- 1. APP CONFIG & SECRETS ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# Апп-ын хаягийг Google Cloud Console дээрх хаягтай ижил байхаар тохируулна
MY_APP_URL = "https://zeppfusionai.streamlit.app" 

google_secrets = {
    "web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [MY_APP_URL, "http://localhost:8501"]
    }
}

# Authenticator-ийг үүсгэх
try:
    authenticator = Authenticate(
        secret_credentials_path=google_secrets,
        cookie_name='zepp_session',
        cookie_key=st.secrets["COOKIE_KEY"],
        cookie_expiry_days=30,
        redirect_uri=MY_APP_URL
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 2. DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('zepp_vault.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS chat_sessions (session_id TEXT PRIMARY KEY, username TEXT, title TEXT, created_at TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)')
    conn.commit(); conn.close()

def save_msg(s_id, role, content):
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('INSERT INTO messages (session_id, role, content, timestamp) VALUES (?,?,?,?)',
              (s_id, role, content, datetime.now().strftime("%I:%M %p")))
    conn.commit(); conn.close()

init_db()

# --- 3. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #09090b !important; color: #d4d4d8; }
    section[data-testid="stSidebar"] { background-color: rgba(24, 24, 27, 0.95) !important; border-right: 1px solid #27272a; }
    .stChatMessage { background-color: transparent !important; }
    .stChatInputContainer { padding-bottom: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTHENTICATION FLOW (RE-WRITTEN) ---
# check_authenticity() ашиглахгүйгээр login() үр дүнг шалгана
user_info = authenticator.login()

if not user_info:
    # Нэвтрээгүй үед харагдах UI
    st.markdown("""
        <div style="text-align:center; margin-top:100px;">
            <img src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/69456a8a7026ba13461ef577/a8ac75228_Gemini_Generated_Image_c9qxrc9qxrc9qxrc1.png" width="100">
            <h1 style="color:white; font-size:3rem; margin-top:20px;">ZeppFusion Pro</h1>
            <p style="color:#71717a;

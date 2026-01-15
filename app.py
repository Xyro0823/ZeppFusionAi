import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import json
import os
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- 1. АПП-ЫН ҮНДСЭН ТОХИРГОО ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# Таны апп-ын албан ёсны хаяг
MY_APP_URL = "https://zeppfusionai-xyro.streamlit.app" 

# Google OAuth-ийн мэдээлэл (Таны өгсөн мэдээллээр шинэчлэв)
google_secrets_dict = {
    "web": {
        "client_id": "660443807451-6pqd68e2arnnv87d948pa3cqorru5pu3.apps.googleusercontent.com",
        "project_id": "zeppfusion",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": [MY_APP_URL]
    }
}

# Google-ийн нэхэж буй json файлыг түр зуур үүсгэх
with open('client_secrets.json', 'w') as f:
    json.dump(google_secrets_dict, f)

# Authenticator-ийг ачаалах
try:
    authenticator = Authenticate(
        secret_credentials_path='client_secrets.json',
        cookie_name='zepp_session',
        cookie_key=st.secrets.get("COOKIE_KEY", "zepp_secure_key_123"),
        cookie_expiry_days=30,
        redirect_uri=MY_APP_URL
    )
except Exception as e:
    st.error(f"Автоматжуулалтын алдаа: {e}")
    st.stop()

# --- 2. ӨГӨГДЛИЙН САНГИЙН ЛОГИК ---
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

# --- 3. ХЭРЭГЛЭГЧИЙН НҮҮР ХУУДАС (LOGIN) ---
user_info = authenticator.login()

if not user_info:
    st.markdown("""
        <div style="text-align:center; margin-top:100px;">
            <h1 style="color:white; font-size:4rem; letter-spacing:-2px;">ZEPPFUSION PRO</h1>
            <p style="color:#71717a; font-size:1.2rem; margin-bottom:50px;">Advanced AI Workspace</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# Нэвтэрсний дараа түр файлыг устгах
if os.path.exists('client_secrets.json'):
    os.remove('client_secrets.json')

# Хэрэглэгчийн мэдээллийг авах
user_email = user_info.get('email')
user_name = user_info.get('name', 'User')
user_pic = user_info.get('picture', '')

# --- 4. SIDEBAR (ЦЭС) ---
with st.sidebar:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 30px;">
            <img src="{user_pic}" style="width:45px; border-radius:50%; border:2px solid #3b82f6;">
            <div>
                <p style="color:white; margin:0; font-weight:600; font-size:14px;">{user_name}</p>
                <p style="color:#71717a; margin:0; font-size:11px;">{user_email}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("＋ Шинэ чат эхлүүлэх", use_container_width=True, type="primary"):
        s_id = hashlib.md5(f"{user_email}{datetime.now()}".encode()).hexdigest()[:10]
        conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
        c.execute('INSERT INTO chat_sessions VALUES (?,?,?,?)', (s_id, user_email, f"Чат {datetime.now().strftime('%H:%M')}", datetime.now().isoformat()))
        conn.commit(); conn.close()
        st.session_state.current_session = s_id
        st.rerun()

    st.markdown("---")
    st.write("🕒 Сүүлийн чатууд")
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT session_id, title FROM chat_sessions WHERE username=? ORDER BY created_at DESC LIMIT 8', (user_email,))
    for sid, title in c.fetchall():
        if st.button(f"💬 {title}", key=sid, use_container_width=True):
            st.session_state.current_session = sid
            st.rerun()
    conn.close()
    
    st.markdown("---")
    authenticator.logout("Гарах", "sidebar")

# --- 5. ЧАТНЫ ХЭСЭГ ---
if st.session_state.get("current_session"):
    # Өмнөх мессежүүдийг харуулах
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT role, content, timestamp FROM messages WHERE session_id=? ORDER BY id ASC', (st.session_state.current_session,))
    for r, cont, t in c.fetchall():
        with st.chat_message(r):
            st.markdown(cont)
            st.caption(t)
    conn.close()

    # AI-тай харилцах
    if prompt := st.chat_input("ZeppFusion-ээс асуух..."):
        save_msg(st.session_state.current_session, "user", prompt)
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("AI хариулж байна..."):
                response = model.generate_content(prompt)
                save_msg(st.session_state.current_session, "assistant", response.text)
            st.rerun()
        except Exception as e:
            st.error(f"AI алдаа: {e}")
else:
    st.info("Чат эхлүүлэхийн тулд зүүн цэснээс 'Шинэ чат' товчийг дарна уу.")

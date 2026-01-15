import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import json
import os
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- 1. APP CONFIG & SECRETS ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# Апп-ын ЖИНХЭНЭ хаяг (Google Cloud дээрх Redirect URI-тай яг ижил байх ёстой)
MY_APP_URL = "https://zeppfusionai-xyro.streamlit.app" 

# Google Cloud-ын мэдээллийг JSON файл болгож бэлдэх
google_secrets_dict = {
    "web": {
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [MY_APP_URL]
    }
}

# Түр зуурын файл үүсгэх
with open('client_secrets.json', 'w') as f:
    json.dump(google_secrets_dict, f)

# Authenticator Setup
try:
    authenticator = Authenticate(
        secret_credentials_path='client_secrets.json',
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
    conn.commit()
    conn.close()

def save_msg(s_id, role, content):
    conn = sqlite3.connect('zepp_vault.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (session_id, role, content, timestamp) VALUES (?,?,?,?)',
              (s_id, role, content, datetime.now().strftime("%I:%M %p")))
    conn.commit()
    conn.close()

init_db()

# --- 3. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #09090b !important; color: #d4d4d8; }
    section[data-testid="stSidebar"] { background-color: rgba(24, 24, 27, 0.95) !important; border-right: 1px solid #27272a; }
    .stChatMessage { background-color: transparent !important; border-bottom: 1px solid rgba(255,255,255,0.03); }
    .stChatInputContainer { padding-bottom: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTHENTICATION FLOW ---
user_info = authenticator.login()

if not user_info:
    # Нэвтрээгүй үед харагдах төв хэсэг
    st.markdown(f"""
        <div style="text-align:center; margin-top:100px;">
            <h1 style="color:white; font-size:3.5rem; margin-bottom:10px;">ZeppFusion Pro</h1>
            <p style="color:#71717a; font-size:1.2rem; margin-bottom:40px;">Secure AI Intelligence Workspace</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# Файлыг устгах (Аюулгүй байдал)
if os.path.exists('client_secrets.json'):
    os.remove('client_secrets.json')

user_email = user_info.get('email')
user_name = user_info.get('name')
user_pic = user_info.get('picture', "")

# --- 5. SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 25px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 12px;">
            <img src="{user_pic}" style="width:42px; border-radius:50%; border: 1px solid #3f3f46;">
            <div style="overflow: hidden;">
                <p style="color:white; margin:0; font-weight:600; font-size:14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_name}</p>
                <p style="color:#71717a; margin:0; font-size:11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_email}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("＋ New Conversation", use_container_width=True, type="primary"):
        s_id = hashlib.md5(f"{user_email}{datetime.now()}".encode()).hexdigest()[:10]
        conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
        c.execute('INSERT INTO chat_sessions VALUES (?,?,?,?)', (s_id, user_email, f"Chat {datetime.now().strftime('%H:%M')}", datetime.now().isoformat()))
        conn.commit(); conn.close()
        st.session_state.current_session = s_id
        st.rerun()

    st.markdown("### Recent Chats")
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT session_id, title FROM chat_sessions WHERE username=? ORDER BY created_at DESC LIMIT 10', (user_email,))
    for sid, title in c.fetchall():
        if st.button(f"💬 {title}", key=sid, use_container_width=True):
            st.session_state.current_session = sid
            st.rerun()
    conn.close()
    
    st.markdown("---")
    authenticator.logout("Sign Out", "sidebar")

# --- 6. MAIN CHAT INTERFACE ---
if st.session_state.get("current_session"):
    # Өмнөх мессежүүдийг ачаалах
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT role, content, timestamp FROM messages WHERE session_id=? ORDER BY id ASC', (st.session_state.current_session,))
    messages = c.fetchall()
    conn.close()

    for r, cont, t in messages:
        with st.chat_message(r):
            st.markdown(cont)
            st.caption(t)

    # Шинэ мессеж оруулах
    if prompt := st.chat_input("Ask ZeppFusion anything..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        save_msg(st.session_state.current_session, "user", prompt)
        
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("Thinking..."):
                response = model.generate_content(prompt)
                
            with st.chat_message("assistant"):
                st.markdown(response.text)
            
            save_msg(st.session_state.current_session, "assistant", response.text)
            st.rerun()
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
else:
    st.info("Start a new conversation to begin chatting with ZeppFusion Pro.")

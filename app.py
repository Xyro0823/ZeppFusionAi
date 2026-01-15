import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- 1. APP CONFIG & SECRETS ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# Апп-ын хаягийг энд заавал зөв тохируулна (Google Cloud Console дээрх хаягтай ижил байх)
MY_APP_URL = "https://zeppfusionai.streamlit.app" 

# Google Credentials JSON бүтэц
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

# Authenticator-ийг үүсгэх (Бүх аргументыг зөв дамжуулсан)
try:
    authenticator = Authenticate(
        secret_credentials_path=google_secrets,
        cookie_name='zepp_session',
        cookie_key=st.secrets["COOKIE_KEY"],
        cookie_expiry_days=30,
        redirect_uri=MY_APP_URL  # <--- Энэ аргумент заавал байх ёстой
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
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTHENTICATION FLOW ---
authenticator.check_authenticity()

if not st.session_state.get('auth_status'):
    st.markdown("""
        <div style="text-align:center; margin-top:100px;">
            <img src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/69456a8a7026ba13461ef577/a8ac75228_Gemini_Generated_Image_c9qxrc9qxrc9qxrc1.png" width="100">
            <h1 style="color:white; font-size:3rem; margin-top:20px;">ZeppFusion Pro</h1>
            <p style="color:#71717a; font-size:1.2rem; margin-bottom:40px;">Next-Gen AI Workspace</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        authenticator.login()
    st.stop()

# --- 5. LOGGED IN AREA ---
user_email = st.session_state['email']
user_name = st.session_state['common_name']
user_pic = st.session_state.get('picture', "")

# Sidebar
with st.sidebar:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <img src="{user_pic}" style="width:40px; border-radius:50%;">
            <div>
                <p style="color:white; margin:0; font-weight:600; font-size:14px;">{user_name}</p>
                <p style="color:#71717a; margin:0; font-size:11px;">{user_email}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("＋ New Conversation", use_container_width=True):
        s_id = hashlib.md5(f"{user_email}{datetime.now()}".encode()).hexdigest()[:10]
        conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
        c.execute('INSERT INTO chat_sessions VALUES (?,?,?,?)', (s_id, user_email, f"Chat {datetime.now().strftime('%H:%M')}", datetime.now().isoformat()))
        conn.commit(); conn.close()
        st.session_state.current_session = s_id
        st.rerun()

    st.markdown("---")
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT session_id, title FROM chat_sessions WHERE username=? ORDER BY created_at DESC', (user_email,))
    for sid, title in c.fetchall():
        if st.button(f"💬 {title}", key=sid, use_container_width=True):
            st.session_state.current_session = sid
            st.rerun()
    conn.close()
    
    st.markdown("---")
    authenticator.logout("Logout", "sidebar")

# Main Chat
if st.session_state.get("current_session"):
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT role, content, timestamp FROM messages WHERE session_id=?', (st.session_state.current_session,))
    for r, cont, t in c.fetchall():
        with st.chat_message(r):
            st.markdown(cont)
            st.caption(t)
    conn.close()

    if prompt := st.chat_input("Message ZeppFusion..."):
        save_msg(st.session_state.current_session, "user", prompt)
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            save_msg(st.session_state.current_session, "assistant", response.text)
            st.rerun()
        except Exception as e:
            st.error(f"AI Error: {e}")
else:
    st.info("Select a chat or start a new one.")

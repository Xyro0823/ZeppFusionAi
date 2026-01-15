import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- 1. CONFIG & SECRETS ---
try:
    # Secrets-ээс бүх мэдээллээ авч байна
    CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    COOKIE_KEY = st.secrets["COOKIE_KEY"]
except KeyError as e:
    st.error(f"Missing secret in configuration: {e}")
    st.stop()

st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# Google Auth Setup
authenticator = Authenticate(
    secret_credentials_path=None,
    cookie_name='zepp_session',
    cookie_key=COOKIE_KEY,
    cookie_expiry_days=30,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

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

# --- 3. AUTHENTICATION FLOW ---
authenticator.check_authenticity()

if not st.session_state.get('auth_status'):
    # Login Screen UI
    st.markdown("""
        <div style="text-align:center; margin-top:100px;">
            <img src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/69456a8a7026ba13461ef577/a8ac75228_Gemini_Generated_Image_c9qxrc9qxrc9qxrc1.png" width="100">
            <h1 style="color:white; font-size:3rem; margin-top:20px;">ZeppFusion Pro</h1>
            <p style="color:#71717a; font-size:1.2rem; margin-bottom:40px;">Intelligent AI Workspace</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        authenticator.login()
    st.stop()

# --- 4. MAIN INTERFACE ---
user_email = st.session_state['email']
user_name = st.session_state['common_name']

# Sidebar
with st.sidebar:
    st.markdown(f"### ✨ ZeppFusion\n<p style='color:#a78bfa;'>Welcome, {user_name}</p>", unsafe_allow_html=True)
    
    if st.button("＋ New Conversation", use_container_width=True):
        s_id = hashlib.md5(f"{user_email}{datetime.now()}".encode()).hexdigest()[:10]
        conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
        c.execute('INSERT INTO chat_sessions VALUES (?,?,?,?)', (s_id, user_email, f"Chat {datetime.now().strftime('%H:%M')}", datetime.now().isoformat()))
        conn.commit(); conn.close()
        st.session_state.current_session = s_id
        st.rerun()

    st.markdown("---")
    # Load history
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT session_id, title FROM chat_sessions WHERE username=? ORDER BY created_at DESC', (user_email,))
    for sid, title in c.fetchall():
        if st.button(f"💬 {title}", key=sid, use_container_width=True):
            st.session_state.current_session = sid
            st.rerun()
    conn.close()
    
    st.markdown("---")
    authenticator.logout("Logout", "sidebar")

# Chat Area
if st.session_state.get("current_session"):
    # Display messages
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT role, content, timestamp FROM messages WHERE session_id=?', (st.session_state.current_session,))
    for r, cont, t in c.fetchall():
        with st.chat_message(r):
            st.markdown(cont)
            st.caption(t)
    conn.close()

    # Input & AI Logic
    if prompt := st.chat_input("Ask anything..."):
        st.chat_message("user").markdown(prompt)
        save_msg(st.session_state.current_session, "user", prompt)
        
        try:
            genai.configure(api_key=GEMINI_API_KEY) # Secrets-ээс уншиж байна
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            save_msg(st.session_state.current_session, "assistant", response.text)
            st.rerun()
        except Exception as e:
            st.error(f"AI Error: {e}")
else:
    st.info("Select a chat from sidebar or start a new one.")

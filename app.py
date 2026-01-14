import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from streamlit_google_auth import Authenticate

# --- 1. APP CONFIG ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# --- 2. GOOGLE AUTH SETUP (SECURE) ---
try:
    authenticator = Authenticate(
        secret_credentials_path=None,
        cookie_name='zepp_session',
        cookie_key=st.secrets["COOKIE_KEY"],
        cookie_expiry_days=30,
        client_id=st.secrets["GOOGLE_CLIENT_ID"],
        client_secret=st.secrets["GOOGLE_CLIENT_SECRET"]
    )
except Exception as e:
    st.error("Secrets are not configured! Please add Google Client ID and Secret to Streamlit Secrets.")
    st.stop()

# --- 3. DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('zepp_vault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions 
                 (session_id TEXT PRIMARY KEY, username TEXT, title TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)''')
    conn.commit(); conn.close()

def create_session(username, title):
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    s_id = hashlib.md5(f"{username}{datetime.now()}".encode()).hexdigest()[:10]
    c.execute('INSERT INTO chat_sessions VALUES (?,?,?,?)', (s_id, username, title, datetime.now().isoformat()))
    conn.commit(); conn.close()
    return s_id

def save_msg(s_id, role, content):
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('INSERT INTO messages (session_id, role, content, timestamp) VALUES (?,?,?,?)',
              (s_id, role, content, datetime.now().strftime("%I:%M %p")))
    conn.commit(); conn.close()

init_db()

# --- 4. CSS STYLING (React Inspired) ---
st.markdown("""
    <style>
    .stApp { background-color: #09090b !important; color: #d4d4d8; }
    section[data-testid="stSidebar"] { background-color: rgba(24, 24, 27, 0.95) !important; border-right: 1px solid #27272a; }
    .message-wrapper { display: flex; gap: 16px; padding: 24px; border-radius: 12px; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.02); }
    .bot-bg { background-color: rgba(124, 58, 237, 0.03); }
    .avatar { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
    .bot-avatar { background: linear-gradient(135deg, #7c3aed, #9333ea); }
    .user-avatar { background: #27272a; border: 1px solid #3f3f46; }
    .stChatInputContainer { padding-bottom: 30px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. AUTHENTICATION FLOW ---
authenticator.check_authenticity()

if not st.session_state.get('auth_status'):
    # Login Screen
    st.markdown("""
        <div style="text-align:center; margin-top:100px;">
            <img src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/69456a8a7026ba13461ef577/a8ac75228_Gemini_Generated_Image_c9qxrc9qxrc9qxrc1.png" width="100">
            <h1 style="color:white; font-size:3rem; margin-top:20px;">ZeppFusion Pro</h1>
            <p style="color:#71717a; font-size:1.2rem;">Next-gen AI Workspace for Creators</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        authenticator.login()
    st.stop()

# --- 6. LOGGED IN UI ---
user_email = st.session_state['email']
user_name = st.session_state['common_name']
user_pic = st.session_state.get('picture', "")

# Sidebar Logic
with st.sidebar:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 12px; margin-bottom: 20px;">
            <img src="{user_pic}" style="width:40px; border-radius:50%;">
            <div style="overflow: hidden;">
                <p style="color:white; margin:0; font-weight:600; font-size:14px; white-space:nowrap;">{user_name}</p>
                <p style="color:#71717a; margin:0; font-size:11px; white-space:nowrap;">{user_email}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("＋ New Conversation", use_container_width=True):
        new_id = create_session(user_email, f"Chat {datetime.now().strftime('%m/%d %H:%M')}")
        st.session_state.current_session = new_id
        st.rerun()

    st.markdown("---")
    st.markdown("<p style='font-size:10px; color:#52525b; letter-spacing:1px;'>RECENT CHATS</p>", unsafe_allow_html=True)
    
    # Load Sessions
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT session_id, title FROM chat_sessions WHERE username=? ORDER BY created_at DESC LIMIT 10', (user_email,))
    for s_id, title in c.fetchall():
        if st.button(f"💬 {title}", key=s_id, use_container_width=True):
            st.session_state.current_session = s_id
            st.rerun()
    conn.close()

    st.markdown("---")
    api_key = st.text_input("Gemini API Key", type="password")
    authenticator.logout("Logout", "sidebar")

# Main Chat Interface
if st.session_state.get("current_session"):
    # Display History
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT role, content, timestamp FROM messages WHERE session_id=?', (st.session_state.current_session,))
    for r, cont, t in c.fetchall():
        is_bot = r == "assistant"
        st.markdown(f"""
            <div class="message-wrapper {'bot-bg' if is_bot else ''}">
                <div class="avatar {'bot-avatar' if is_bot else 'user-avatar'}">{'✨' if is_bot else '👤'}</div>
                <div style="flex:1;">
                    <div style="font-size:13px; font-weight:600; color:{'#a78bfa' if is_bot else '#d4d4d8'};">{'ZeppFusion' if is_bot else user_name} <span style="font-size:10px; color:#3f3f46; margin-left:10px;">{t}</span></div>
                    <div style="color:#d4d4d8; margin-top:8px; line-height:1.6;">{cont}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    conn.close()

    # Chat Input
    if prompt := st.chat_input("Message ZeppFusion..."):
        save_msg(st.session_state.current_session, "user", prompt)
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                save_msg(st.session_state.current_session, "assistant", response.text)
            except Exception as e:
                st.error(f"AI Error: {e}")
        else:
            st.warning("Please provide a Gemini API Key in the sidebar.")
        st.rerun()
else:
    st.markdown("<div style='text-align:center; margin-top:20vh; opacity:0.3;'><h1>Select a chat or start a new one</h1></div>", unsafe_allow_html=True)


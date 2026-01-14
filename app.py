import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

# --- 1. PAGE CONFIG & CSS ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    .stApp { background-color: #09090b !important; font-family: 'Inter', sans-serif !important; }
    
    /* Sidebar React Style */
    section[data-testid="stSidebar"] {
        background-color: rgba(24, 24, 27, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px); width: 300px !important;
    }

    /* Auth Card Style */
    .auth-card {
        max-width: 420px; margin: 80px auto; padding: 40px;
        background: rgba(24, 24, 27, 0.9); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; text-align: center;
    }

    /* Message Bubbles */
    .message-wrapper { display: flex; gap: 16px; padding: 24px; border-radius: 12px; margin-bottom: 8px; }
    .bot-bg { background-color: rgba(255, 255, 255, 0.02); border-top: 1px solid rgba(255,255,255,0.03); }
    .avatar { width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 20px; }
    .bot-avatar { background: linear-gradient(135deg, #7c3aed, #9333ea); box-shadow: 0 8px 20px rgba(124, 58, 237, 0.3); }
    .user-avatar { background: #27272a; border: 1px solid #3f3f46; }
    
    /* Custom Session List */
    .session-item {
        padding: 10px; border-radius: 8px; margin-bottom: 5px; cursor: pointer;
        transition: all 0.2s; border: 1px solid transparent; color: #a1a1aa; font-size: 14px;
    }
    .session-item:hover { background: rgba(255,255,255,0.05); color: white; border: 1px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('zepp_vault.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions 
                 (session_id TEXT PRIMARY KEY, username TEXT, title TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def hash_pw(password): return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password):
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('INSERT INTO users VALUES (?,?)', (username, hash_pw(password)))
    conn.commit(); conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username=?', (username,))
    res = c.fetchone()
    conn.close()
    return res and res[0] == hash_pw(password)

def create_session(username, title):
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    s_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:10]
    c.execute('INSERT INTO chat_sessions VALUES (?,?,?,?)', (s_id, username, title, datetime.now().isoformat()))
    conn.commit(); conn.close()
    return s_id

def save_msg(s_id, role, content):
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('INSERT INTO messages (session_id, role, content, timestamp) VALUES (?,?,?,?)',
              (s_id, role, content, datetime.now().strftime("%I:%M %p")))
    conn.commit(); conn.close()

init_db()

# --- 3. SESSION MANAGEMENT ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_session" not in st.session_state: st.session_state.current_session = None

# --- 4. AUTH PAGE ---
def auth_page():
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.image("https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/69456a8a7026ba13461ef577/a8ac75228_Gemini_Generated_Image_c9qxrc9qxrc9qxrc1.png", width=70)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sign In", use_container_width=True):
            if verify_user(u, p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Invalid credentials")
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register", use_container_width=True):
            try:
                add_user(nu, np)
                st.success("Account created! Please Login.")
            except: st.error("User already exists")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. MAIN CHAT SYSTEM ---
if not st.session_state.logged_in:
    auth_page()
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### ✨ ZeppFusion\n<p style='color:#7c3aed;'>Logged as: {st.session_state.user}</p>", unsafe_allow_html=True)
        
        if st.button("＋ New Conversation", use_container_width=True):
            new_id = create_session(st.session_state.user, f"Chat {datetime.now().strftime('%m/%d %H:%M')}")
            st.session_state.current_session = new_id
            st.rerun()

        st.markdown("---")
        st.markdown("<p style='font-size:11px; color:#52525b;'>YOUR SESSIONS</p>", unsafe_allow_html=True)
        
        conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
        c.execute('SELECT session_id, title FROM chat_sessions WHERE username=? ORDER BY created_at DESC', (st.session_state.user,))
        sessions = c.fetchall()
        for s_id, title in sessions:
            if st.button(f"💬 {title}", key=s_id, use_container_width=True):
                st.session_state.current_session = s_id
                st.rerun()
        
        st.markdown("---")
        api_key = st.text_input("Gemini API Key", type="password")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # Chat Area
    if st.session_state.current_session:
        conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
        c.execute('SELECT role, content, timestamp FROM messages WHERE session_id=?', (st.session_state.current_session,))
        msgs = c.fetchall()
        
        for r, cont, t in msgs:
            is_bot = r == "assistant"
            st.markdown(f"""
                <div class="message-wrapper {'bot-bg' if is_bot else ''}">
                    <div class="avatar {'bot-avatar' if is_bot else 'user-avatar'}">{'✨' if is_bot else '👤'}</div>
                    <div style="flex:1;">
                        <div style="font-size:13px; font-weight:600; color:{'#a78bfa' if is_bot else '#d4d4d8'};">{'ZeppFusion' if is_bot else 'You'}</div>
                        <div style="color:#d4d4d8; line-height:1.6; margin-top:5px;">{cont}</div>
                        <div style="font-size:10px; color:#3f3f46; margin-top:8px;">{t} • ⏱ Expires in 7 days</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        if prompt := st.chat_input("Ask ZeppFusion..."):
            save_msg(st.session_state.current_session, "user", prompt)
            st.rerun()
            
            # AI Logic (Simplified for brevity)
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                save_msg(st.session_state.current_session, "assistant", response.text)
                st.rerun()
    else:
        st.markdown("<div style='text-align:center; margin-top:20vh; color:#3f3f46;'><h1>Start a new session to begin</h1><p>Your history will be saved here automatically.</p></div>", unsafe_allow_html=True)

import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import requests
from datetime import datetime

# --- 1. CONFIG & CREDENTIALS ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

CLIENT_ID = "660443807451-6pqd68e2arnnv87d948pa3cqorru5pu3.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://zeppfusionai-xyro.streamlit.app"

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('zepp_vault.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- 3. AUTHENTICATION LOGIC ---
def login_ui():
    st.markdown("<h1 style='text-align:center; margin-top:100px;'>ZeppFusion Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#71717a;'>Next-Gen AI Intelligence</p>", unsafe_allow_html=True)
    
    # Google Login URL үүсгэх
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code"
        f"&scope=openid%20email%20profile"
    )
    
    st.markdown(f"""
        <div style="text-align:center; margin-top:30px;">
            <a href="{auth_url}" target="_self" style="background-color:#4285F4; color:white; padding:12px 24px; text-decoration:none; border-radius:5px; font-weight:bold; display:inline-block;">
                Google-ээр нэвтрэх
            </a>
        </div>
    """, unsafe_allow_html=True)

# URL-аас Auth Code-г барьж авах
if "user" not in st.session_state:
    st.session_state.user = None

params = st.query_params
if "code" in params and not st.session_state.user:
    code = params["code"]
    # Code-г Token-оор солих
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    r = requests.post(token_url, data=data).json()
    
    if "access_token" in r:
        # Хэрэглэгчийн мэдээллийг авах
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {r['access_token']}"}
        ).json()
        st.session_state.user = user_info
        st.query_params.clear()
        st.rerun()

# --- 4. MAIN APP ---
if not st.session_state.user:
    login_ui()
    st.stop()

# Нэвтэрсэн хэрэглэгчийн UI
user = st.session_state.user

with st.sidebar:
    st.image(user.get("picture", ""), width=50)
    st.write(f"**{user.get('name')}**")
    st.caption(user.get("email"))
    
    if st.button("Гарах", use_container_width=True):
        st.session_state.user = None
        st.rerun()
    
    st.markdown("---")
    if st.button("＋ Шинэ чат", use_container_width=True, type="primary"):
        st.session_state.chat_id = hashlib.md5(f"{user['email']}{datetime.now()}".encode()).hexdigest()[:8]
        st.rerun()

# --- 5. CHAT AREA ---
if "chat_id" not in st.session_state:
    st.session_state.chat_id = "default_session"

chat_id = st.session_state.chat_id

# Чат харуулах
conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
c.execute('SELECT role, content FROM messages WHERE session_id=?', (chat_id,))
for r, cont in c.fetchall():
    with st.chat_message(r):
        st.write(cont)
conn.close()

# AI Хариулт
if prompt := st.chat_input("Message ZeppFusion..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('INSERT INTO messages (session_id, role, content) VALUES (?,?,?)', (chat_id, "user", prompt))
    
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        with st.chat_message("assistant"):
            st.write(response.text)
        
        c.execute('INSERT INTO messages (session_id, role, content) VALUES (?,?,?)', (chat_id, "assistant", response.text))
        conn.commit()
    except Exception as e:
        st.error(f"AI Error: {e}")
    conn.close()

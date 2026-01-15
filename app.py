import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
from PIL import Image
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ZeppFusion",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (GEMINI STYLE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    
    * { font-family: 'Google Sans', sans-serif; }
    .stApp { background-color: #131314; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1e1f20; border-right: 1px solid #2d2e2f; }
    
    /* Hide Default Headers */
    header, footer { visibility: hidden; }

    /* Chat Messages */
    .stChatMessage { background-color: transparent !important; border: none !important; }
    
    /* Chat Input Fixed at Bottom */
    div[data-testid="stChatInput"] {
        border-radius: 28px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
    }

    /* File Uploader Style */
    .stFileUploader section { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE FUNCTIONS ---
def init_db():
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_message(username, role, content):
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
              (username, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_chat_history(username):
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages WHERE username=? ORDER BY id ASC', (username,))
    history = c.fetchall()
    conn.close()
    return history

init_db()

# Session state
if "username" not in st.session_state:
    st.session_state.username = "User"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("# ⚡ ZeppFusion")
    if st.button("🗑️ Түүх устгах", use_container_width=True):
        conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
        c.execute('DELETE FROM messages WHERE username=?', (st.session_state.username,))
        conn.commit(); conn.close()
        st.rerun()
    st.markdown("---")
    st.markdown("**Model: Gemini 2.5 Flash**")

# --- MAIN CHAT AREA ---
db_history = get_chat_history(st.session_state.username)
for role, content in db_history:
    with st.chat_message(role):
        st.markdown(content)

# --- INPUT AREA (Gemini Layout) ---
col1, col2 = st.columns([0.07, 0.93])

with col1:
    # Нэмэх тэмдэг шиг харагдах файл оруулагч
    uploaded_file = st.file_uploader("➕", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

with col2:
    prompt = st.chat_input("ZeppFusion-д мессеж бичих...")

# --- HANDLE INPUT ---
if prompt:
    # Хэрэглэгчийн мессежийг харуулах
    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, width=250)
        st.markdown(prompt)
    
    save_message(st.session_state.username, "user", prompt)

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Хэрэв gemini-2.5-flash ажиллахгүй бол gemini-1.5-flash болгож солиорой
        model = genai.GenerativeModel('gemini-1.5-flash') 

        # Контекст бэлдэх
        gemini_history = []
        for role, content in db_history:
            gemini_history.append({"role": "model" if role == "assistant" else "user", "parts": [content]})

        with st.spinner("Бодож байна..."):
            if uploaded_file:
                img = Image.open(uploaded_file)
                response = model.generate_content([prompt, img])
            else:
                chat = model.start_chat(history=gemini_history)
                response = chat.send_message(prompt)

        # AI-ийн хариултыг харуулах
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        save_message(st.session_state.username, "assistant", response.text)
        st.rerun()

    except Exception as e:
        st.error(f"Алдаа: {str(e)}")

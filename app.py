import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image

# --- 1. CSS FOR MODERN LOOK (Gemini Style) ---
st.markdown("""
<style>
    /* Үндсэн фонт болон дэвсгэр */
    .stApp { background-color: #0e0e10; }
    
    /* Чатны оролтын хэсгийг Gemini шиг болгох */
    .stChatInputContainer {
        padding: 10px;
        background-color: #1e1e20 !important;
        border-radius: 28px !important;
        border: 1px solid #3c4043 !important;
    }
    
    /* Чатны бөмбөлөгүүд */
    section[data-testid="stChatMessageContainer"] {
        padding-bottom: 120px; /* Оролтын хэсэгт даруулахгүй байх */
    }
    
    /* Файл оруулах товчийг цэгцлэх */
    .stFileUploader section {
        padding: 0 ! IMPORTANT;
        border: none ! IMPORTANT;
        background: transparent ! IMPORTANT;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE & LOGIC (Өмнөх хэсгүүд хэвээр) ---
def init_db():
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, content TEXT, timestamp TEXT)')
    conn.commit(); conn.close()

init_db()

# --- 3. MAIN CHAT AREA ---
if "username" not in st.session_state:
    st.session_state.username = "User" # Туршилтын зориулалтаар

# Чатны түүхийг харуулах
conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
c.execute('SELECT role, content FROM messages WHERE username=? ORDER BY id ASC', (st.session_state.username,))
db_history = c.fetchall()
conn.close()

for role, content in db_history:
    with st.chat_message(role):
        st.markdown(content)

# --- 4. THE MODERN INPUT BAR (Gemini Style) ---
# Доор бэхлэгдсэн контейнер
input_container = st.container()

with input_container:
    # Доорх 2 багана нь Нэмэх тэмдэг болон Чатны талбарыг зэрэгцүүлнэ
    col1, col2 = st.columns([0.1, 0.9])
    
    with col1:
        # Нэмэх тэмдэг бүхий файл оруулагч
        uploaded_file = st.file_uploader("➕", type=['png', 'jpg', 'jpeg', 'pdf'], label_visibility="collapsed")
    
    with col2:
        prompt = st.chat_input("Message ZeppFusion...")

# --- 5. AI RESPONSE LOGIC ---
if prompt:
    # Хэрэглэгчийн мессежийг шууд харуулах
    with st.chat_message("user"):
        st.markdown(prompt)
    
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Таны хүссэн Gemini 2.5 Flash (эсвэл 2.0)
        model = genai.GenerativeModel('gemini-2.0-flash-exp') 
        
        # Санах ойг бэлдэх
        gemini_history = []
        for role, content in db_history:
            gemini_role = "model" if role == "assistant" else "user"
            gemini_history.append({"role": gemini_role, "parts": [content]})
        
        chat = model.start_chat(history=gemini_history)
        
        with st.spinner(""):
            if uploaded_file:
                img = Image.open(uploaded_file)
                response = model.generate_content([prompt, img])
            else:
                response = chat.send_message(prompt)
        
        # AI-ийн хариултыг харуулах
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # DB-д хадгалах
        conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
        c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
                  (st.session_state.username, "user", prompt, datetime.now().isoformat()))
        c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
                  (st.session_state.username, "assistant", response.text, datetime.now().isoformat()))
        conn.commit(); conn.close()
        
    except Exception as e:
        st.error(f"Error: {e}")

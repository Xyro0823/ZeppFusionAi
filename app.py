import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import re
from datetime import datetime
from PIL import Image

# --- 1. CONFIG & SYSTEM PROMPT ---
st.set_page_config(page_title="ZeppFusion", page_icon="⚡", layout="wide")

# AI-ийн зан төлөвийг тохируулах
SYSTEM_PROMPT = "Чи бол ZeppFusion нэртэй ухаалаг туслах. Хэрэглэгчийн асуултанд маш тодорхой, мэргэжлийн түвшинд хариулна."

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, full_name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, content TEXT, timestamp TEXT)')
    conn.commit(); conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

init_db()

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- 4. LOGIN / REGISTER UI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>⚡ ZeppFusion</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Нэвтрэх", "Бүртгүүлэх"])
    
    with tab1:
        user = st.text_input("И-мэйл", key="l_user")
        pwd = st.text_input("Нууц үг", type='password', key="l_pwd")
        if st.button("Нэвтрэх", use_container_width=True, type="primary"):
            conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
            c.execute('SELECT password FROM users WHERE username = ?', (user,))
            data = c.fetchone(); conn.close()
            if data and check_hashes(pwd, data[0]):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("И-мэйл эсвэл нууц үг буруу байна.")
                
    with tab2:
        new_name = st.text_input("Бүтэн нэр")
        new_user = st.text_input("Бүртгүүлэх и-мэйл")
        new_pwd = st.text_input("Шинэ нууц үг", type='password')
        if st.button("Бүртгүүлэх", use_container_width=True):
            if is_valid_email(new_user) and len(new_pwd) >= 6:
                conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
                try:
                    c.execute('INSERT INTO users VALUES (?,?,?)', (new_user, make_hashes(new_pwd), new_name))
                    conn.commit(); st.success("Бүртгэл амжилттай! Нэвтэрнэ үү.")
                except: st.warning("Энэ и-мэйл бүртгэлтэй байна.")
                conn.close()
            else:
                st.error("И-мэйл формат эсвэл нууц үгийн урт (6+) буруу байна.")
    st.stop()

# --- 5. SIDEBAR & FILE UPLOAD ---
with st.sidebar:
    st.title("⚡ ZeppFusion")
    st.write(f"👤 **{st.session_state.username}**")
    
    st.markdown("---")
    st.subheader("📁 Файл хавсаргах")
    uploaded_file = st.file_uploader("Зураг эсвэл файл сонгох", type=['png', 'jpg', 'jpeg', 'pdf'])
    if uploaded_file:
        st.info(f"Файл сонгогдлоо: {uploaded_file.name}")
    
    st.markdown("---")
    if st.button("Гарах", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    if st.button("🗑️ Түүх устгах", use_container_width=True):
        conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
        c.execute('DELETE FROM messages WHERE username=?', (st.session_state.username,))
        conn.commit(); conn.close(); st.rerun()

# --- 6. MAIN CHAT INTERFACE ---
st.markdown("""
<style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# DB-ээс түүх унших
conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
c.execute('SELECT role, content FROM messages WHERE username=? ORDER BY id ASC', (st.session_state.username,))
db_history = c.fetchall()
conn.close()

for role, content in db_history:
    with st.chat_message(role):
        st.markdown(content)

# Шинэ мессеж
if prompt := st.chat_input("ZeppFusion-ээс асуух эсвэл файл тайлбарлуулах..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Контекст бэлдэх
    gemini_history = []
    for role, content in db_history:
        gemini_history.append({"role": "model" if role == "assistant" else "user", "parts": [content]})

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)
        chat = model.start_chat(history=gemini_history)
        
        with st.spinner("ZeppFusion бодож байна..."):
            if uploaded_file:
                # Зураг болон текст хосолсон хүсэлт
                img = Image.open(uploaded_file)
                response = model.generate_content([prompt, img])
            else:
                # Зөвхөн текст хүсэлт
                response = chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Хадгалах
        conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
        c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
                  (st.session_state.username, "user", prompt, datetime.now().isoformat()))
        c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
                  (st.session_state.username, "assistant", response.text, datetime.now().isoformat()))
        conn.commit(); conn.close()
        
    except Exception as e:
        st.error(f"Алдаа гарлаа: {e}")

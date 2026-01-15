import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import re
from datetime import datetime

# --- 1. CONFIG ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

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

# --- 3. AUTH STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- 4. LOGIN / REGISTER UI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>ZeppFusion Pro</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Нэвтрэх", "Бүртгүүлэх"])
    
    with tab1:
        user = st.text_input("И-мэйл", key="l_user")
        pwd = st.text_input("Нууц үг", type='password', key="l_pwd")
        if st.button("Нэвтрэх", use_container_width=True):
            conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
            c.execute('SELECT password FROM users WHERE username = ?', (user,))
            data = c.fetchone(); conn.close()
            if data and check_hashes(pwd, data[0]):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("И-мэйл эсвэл нууц үг буруу")
                
    with tab2:
        new_name = st.text_input("Бүтэн нэр")
        new_user = st.text_input("И-мэйл хаяг бүртгүүлэх")
        new_pwd = st.text_input("Шинэ нууц үг", type='password')
        if st.button("Бүртгүүлэх", use_container_width=True):
            if not is_valid_email(new_user):
                st.error("Буруу и-мэйл формат!")
            else:
                conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
                try:
                    c.execute('INSERT INTO users VALUES (?,?,?)', (new_user, make_hashes(new_pwd), new_name))
                    conn.commit(); st.success("Амжилттай! Одоо нэвтэрнэ үү.")
                except:
                    st.warning("Бүртгэлтэй байна.")
                conn.close()
    st.stop()

# --- 5. CHAT WITH MEMORY LOGIC ---
with st.sidebar:
    st.title("⚡ ZeppFusion")
    st.write(f"👤 **{st.session_state.username}**")
    if st.button("Гарах", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    if st.button("🗑️ Түүх устгах", use_container_width=True):
        conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
        c.execute('DELETE FROM messages WHERE username=?', (st.session_state.username,))
        conn.commit(); conn.close(); st.rerun()

st.subheader("AI Assistant")

# Өгөгдлийн сангаас түүхийг унших
conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
c.execute('SELECT role, content FROM messages WHERE username=? ORDER BY id ASC', (st.session_state.username,))
history_data = c.fetchall()
conn.close()

# Дэлгэц дээр харуулах
for role, content in history_data:
    with st.chat_message(role):
        st.write(content)

if prompt := st.chat_input("Яриагаа үргэлжлүүлэх..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    # Gemini-д зориулж түүхийг бэлдэх (Энэ хэсэг санах ойг хариуцна)
    gemini_history = []
    for role, content in history_data:
        # Gemini-ийн 'assistant'-ыг 'model' гэж өөрчлөх шаардлагатай
        gemini_role = "model" if role == "assistant" else "user"
        gemini_history.append({"role": gemini_role, "parts": [content]})

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Санах ойтой чат эхлүүлэх
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.write(response.text)
        
        # DB-д хадгалах
        conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
        c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
                  (st.session_state.username, "user", prompt, datetime.now().isoformat()))
        c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
                  (st.session_state.username, "assistant", response.text, datetime.now().isoformat()))
        conn.commit(); conn.close()
    except Exception as e:
        st.error(f"Алдаа: {e}")

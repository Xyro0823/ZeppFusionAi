import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime

# --- 1. АПП-ЫН ТОХИРГОО ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# --- 2. ӨГӨГДЛИЙН САН (USER & CHAT) ---
def init_db():
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    # Хэрэглэгчдийн хүснэгт
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, full_name TEXT)''')
    # Мессежүүдийн хүснэгт
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, content TEXT, timestamp TEXT)''")
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

init_db()

# --- 3. AUTH LOGIC (LOGIN / REGISTER) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login_user(username, password):
    conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    data = c.fetchone()
    conn.close()
    if data:
        return check_hashes(password, data[0])
    return False

def add_user(username, password, full_name):
    conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
    try:
        c.execute('INSERT INTO users(username, password, full_name) VALUES (?,?,?)', 
                  (username, make_hashes(password), full_name))
        conn.commit(); conn.close()
        return True
    except:
        return False

# --- 4. LOGIN / REGISTER UI ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Нэвтрэх", "Бүртгүүлэх"])
    
    with tab1:
        st.subheader("ZeppFusion-д нэвтрэх")
        user = st.text_input("И-мэйл эсвэл Хэрэглэгчийн нэр", key="l_user")
        pwd = st.text_input("Нууц үг", type='password', key="l_pwd")
        if st.button("Нэвтрэх", use_container_width=True):
            if login_user(user, pwd):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.success(f"{user} амжилттай нэвтэрлээ")
                st.rerun()
            else:
                st.error("Нэр эсвэл нууц үг буруу байна")
                
    with tab2:
        st.subheader("Шинэ бүртгэл үүсгэх")
        new_name = st.text_input("Бүтэн нэр")
        new_user = st.text_input("И-мэйл (Хэрэглэгчийн нэр)")
        new_pwd = st.text_input("Нууц үг", type='password')
        if st.button("Бүртгүүлэх", use_container_width=True):
            if add_user(new_user, new_pwd, new_name):
                st.success("Амжилттай бүртгэгдлээ! Одоо нэвтрэх хэсэг рүү орно уу.")
            else:
                st.warning("Энэ хэрэглэгчийн нэр бүртгэлтэй байна.")
    st.stop()

# --- 5. MAIN APP (LOGGED IN) ---
with st.sidebar:
    st.title("⚡ ZeppFusion Pro")
    st.write(f"👤 Хэрэглэгч: **{st.session_state.username}**")
    
    if st.button("Гарах", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    
    st.markdown("---")
    if st.button("🗑️ Чат цэвэрлэх", use_container_width=True):
        conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
        c.execute('DELETE FROM messages WHERE username=?', (st.session_state.username,))
        conn.commit(); conn.close()
        st.rerun()

# --- 6. CHAT INTERFACE ---
st.title("AI Workspace")

# Өмнөх мессежүүдийг ачаалах
conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
c.execute('SELECT role, content FROM messages WHERE username=? ORDER BY id ASC', (st.session_state.username,))
for role, content in c.fetchall():
    with st.chat_message(role):
        st.write(content)
conn.close()

# AI Харилцаа
if prompt := st.chat_input("ZeppFusion-ээс асуух..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    # DB-д хадгалах
    conn = sqlite3.connect('zepp_fusion.db'); c = conn.cursor()
    c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
              (st.session_state.username, "user", prompt, datetime.now().isoformat()))
    
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        with st.chat_message("assistant"):
            st.write(response.text)
        
        c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
                  (st.session_state.username, "assistant", response.text, datetime.now().isoformat()))
        conn.commit()
    except Exception as e:
        st.error(f"AI Error: {e}")
    conn.close()

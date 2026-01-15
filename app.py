import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from oauthlib.oauth2 import WebApplicationClient
import requests
import json

# --- 1. APP CONFIG ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# Google Credentials
CLIENT_ID = "660443807451-6pqd68e2arnnv87d948pa3cqorru5pu3.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "https://zeppfusionai-xyro.streamlit.app"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

client = WebApplicationClient(CLIENT_ID)

# --- 2. DATABASE ---
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

# --- 3. AUTH LOGIC ---
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

if "user" not in st.session_state:
    st.session_state.user = None

# URL-аас код ирсэн эсэхийг шалгах
query_params = st.query_params
if "code" in query_params and st.session_state.user is None:
    code = query_params["code"]
    google_cfg = get_google_provider_cfg()
    token_endpoint = google_cfg["token_endpoint"]
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=st.context.headers.get("referer") or REDIRECT_URI,
        redirect_url=REDIRECT_URI,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get("email_verified"):
        st.session_state.user = userinfo_response.json()
        st.query_params.clear()
        st.rerun()

# --- 4. UI ---
if st.session_state.user is None:
    st.markdown("<h1 style='text-align:center;'>ZeppFusion Pro</h1>", unsafe_allow_html=True)
    
    google_cfg = get_google_provider_cfg()
    authorization_endpoint = google_cfg["authorization_endpoint"]
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"],
    )
    
    st.markdown(f'''
        <div style="text-align:center;">
            <a href="{request_uri}" target="_self" style="background-color: #4285F4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                Google-ээр нэвтрэх
            </a>
        </div>
    ''', unsafe_allow_html=True)
    st.stop()

# --- 5. LOGGED IN AREA ---
user = st.session_state.user

with st.sidebar:
    st.image(user["picture"], width=50)
    st.write(f"Сайн уу, {user['name']}")
    if st.button("Гарах"):
        st.session_state.user = None
        st.rerun()
    
    st.markdown("---")
    if st.button("＋ Шинэ чат"):
        s_id = hashlib.md5(f"{user['email']}{datetime.now()}".encode()).hexdigest()[:10]
        conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
        c.execute('INSERT INTO chat_sessions VALUES (?,?,?,?)', (s_id, user['email'], f"Чат {datetime.now().strftime('%H:%M')}", datetime.now().isoformat()))
        conn.commit(); conn.close()
        st.session_state.current_session = s_id
        st.rerun()

# --- 6. CHAT INTERFACE ---
if st.session_state.get("current_session"):
    s_id = st.session_state.current_session
    conn = sqlite3.connect('zepp_vault.db'); c = conn.cursor()
    c.execute('SELECT role, content, timestamp FROM messages WHERE session_id=?', (s_id,))
    for r, cont, t in c.fetchall():
        with st.chat_message(r):
            st.write(cont)
    conn.close()

    if prompt := st.chat_input("Асуултаа бичнэ үү..."):
        save_msg(s_id, "user", prompt)
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            save_msg(s_id, "assistant", response.text)
            st.rerun()
        except Exception as e:
            st.error(f"Алдаа: {e}")

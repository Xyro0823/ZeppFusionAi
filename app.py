import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Хуудасны үндсэн тохиргоо
st.set_page_config(
    page_title="ZeppFusion AI", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Шилдэг апп-уудын нууц CSS (Linear & v0 style)
st.markdown("""
    <style>
    /* Ерөнхий дэвсгэр - Гүн харанхуй, зөөлөн шилжилттэй */
    .stApp {
        background-color: #08090a !important;
        color: #f4f4f5 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Sidebar - Маш цэвэрхэн, Linear style */
    section[data-testid="stSidebar"] {
        background-color: #0c0d0e !important;
        border-right: 1px solid #1f2123 !important;
        width: 280px !important;
    }

    /* "New Chat" товчлуур - Apple style */
    div.stButton > button {
        background: #ffffff !important;
        color: #000000 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        width: 100% !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background: #e4e4e7 !important;
        transform: translateY(-1px);
    }

    /* Чатны талбарын төвлөрөл (Linear/v0 style) */
    .main .block-container {
        max-width: 900px !important;
        padding-top: 5rem !important;
        padding-bottom: 10rem !important;
    }

    /* Мэндчилгээний хэсэг - Typography focus */
    .hero-text {
        font-size: 48px !important;
        font-weight: 700 !important;
        letter-spacing: -1.2px !important;
        text-align: center;
        background: linear-gradient(180deg, #ffffff 0%, #a1a1aa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .sub-hero {
        color: #71717a !important;
        text-align: center;
        font-size: 18px !important;
        margin-bottom: 40px;
    }

    /* Чатны мессежүүд - Bubble-гүй, орчин үеийн цэвэрхэн харагдац */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 24px 0px !important;
        border-bottom: 1px solid #1f2123 !important;
    }

    /* Prompt Input - Floating Card style */
    .stChatInputContainer {
        padding: 20px !important;
        background: transparent !important;
        bottom: 20px !important;
    }
    .stChatInputContainer > div {
        background-color: #161718 !important;
        border: 1px solid #272a2d !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
    }

    /* Custom Cards for Welcome */
    .card {
        background: #111213;
        border: 1px solid #1f2123;
        padding: 20px;
        border-radius: 12px;
        transition: border 0.3s ease;
    }
    .card:hover {
        border-color: #3f3f46;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Linear Inspired)
with st.sidebar:
    st.markdown("<div style='padding: 10px 0px;'><h3 style='color: white;'>⚡ ZeppFusion</h3></div>", unsafe_allow_html=True)
    
    if st.button("＋ New Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br><p style='color:#52525b; font-size:11px; font-weight:600; letter-spacing:0.5px;'>ACCESS CONTROL</p>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", label_visibility="collapsed", placeholder="sk-...")

    st.markdown("<br><p style='color:#52525b; font-size:11px; font-weight:600; letter-spacing:0.5px;'>RESOURCES</p>", unsafe_allow_html=True)
    st.markdown("<small style='color:#a1a1aa;'>• Documentation</small>", unsafe_allow_html=True)
    st.markdown("<small style='color:#a1a1aa;'>• API Status</small>", unsafe_allow_html=True)

# 4. Үндсэн логик
if not api_key:
    # Шилдэг апп-уудын Welcome Screen
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-text'>What can I help you <br>ship today?</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-hero'>The next generation of ZeppFusion AI is at your service.</p>", unsafe_allow_html=True)
    
    # 3 Багана бүхий Card-ууд
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><b>💻 Code Genius</b><p style="font-size:13px; color:#71717a; margin-top:8px;">Generate, debug, and optimize complex functions.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><b>✍️ Creative Flow</b><p style="font-size:13px; color:#71717a; margin-top:8px;">Write articles, emails, and scripts in seconds.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><b>🔍 Deep Analysis</b><p style="font-size:13px; color:#71717a; margin-top:8px;">Summarize data and extract key insights.</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("⚠️ Please enter your API Key in the sidebar to begin.")

else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Чат харуулах (Clean & Spaced)
    for message in st.session_state.messages:
        avatar = "https://cdn-icons-png.flaticon.com/512/3293/3293466.png" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Чат бичих (Floating Input)
    if prompt := st.chat_input("Message ZeppFusion..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="https://cdn-icons-png.flaticon.com/512/3293/3293466.png"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Ой санамжтай чат
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                with st.spinner(""):
                    response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Execution Error: {e}")

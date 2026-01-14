import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="wide")

# 2. Pixel-Perfect CSS (Яг VOXA-ийн деталь бүрийг дуурайсан)
st.markdown("""
    <style>
    /* Үндсэн Background */
    .stApp {
        background-color: #0F1012 !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* Sidebar - VOXA-ийн гүн бараан өнгө болон нарийн зураас */
    section[data-testid="stSidebar"] {
        background-color: #080809 !important;
        border-right: 1px solid #1F2023 !important;
        width: 280px !important;
    }

    /* Лого хэсэг */
    .logo-container {
        padding: 20px 0px 30px 10px;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -1px;
        color: white;
    }

    /* Sidebar-ийн "Start New Project" товчлуур - VOXA-ийн Цагаан товч */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px !important;
        font-weight: 700 !important;
        width: 100% !important;
        margin-bottom: 20px !important;
        font-size: 14px !important;
    }

    /* Хайлтын хэсэг (Search) */
    .stTextInput input {
        background-color: #161719 !important;
        border: 1px solid #232528 !important;
        border-radius: 10px !important;
        color: white !important;
    }

    /* Sidebar Цэсний элементүүд */
    .nav-item {
        display: flex;
        align-items: center;
        padding: 12px;
        border-radius: 10px;
        color: #8E9196;
        font-size: 14px;
        margin-bottom: 4px;
        cursor: pointer;
        transition: 0.2s;
    }
    .nav-item:hover { background-color: #161719; color: white; }
    .nav-item.active { background-color: #1A1B1E; color: white; }
    .nav-icon { margin-right: 12px; font-size: 18px; }

    /* Чатны хэсэг - Пропорци */
    .main .block-container {
        max-width: 900px !important;
        padding-top: 3rem !important;
    }

    /* VOXA Chat Bubbles - Булцгар биш, цэвэрхэн line дизайн */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border-bottom: 1px solid #1A1B1E !important;
        padding: 30px 0 !important;
        border-radius: 0 !important;
    }

    /* --- INPUT BAR: VOXA-ИЙН ХАМГИЙН ЧУХАЛ ХЭСЭГ --- */
    .stChatInputContainer {
        padding: 20px !important;
        background: transparent !important;
        bottom: 10px !important;
    }
    .stChatInputContainer > div {
        background-color: #161719 !important;
        border: 1px solid #232528 !important;
        border-radius: 32px !important;
        padding: 6px 15px 6px 50px !important; /* (+) товчны зай */
        box-shadow: 0 10px 40px rgba(0,0,0,0.4) !important;
    }

    /* Зүүн талын (+) товч */
    .stChatInputContainer::before {
        content: '+';
        position: absolute;
        left: 40px;
        bottom: 37px;
        z-index: 1000;
        color: #8E9196;
        font-size: 24px;
        font-weight: 300;
    }

    /* Баруун талын Микрофон дүрс */
    .stChatInputContainer::after {
        content: '🎙️';
        position: absolute;
        right: 85px;
        bottom: 38px;
        z-index: 1000;
        font-size: 18px;
        opacity: 0.6;
    }

    /* Илгээх товчлуур - Нил ягаан */
    [data-testid="stChatInputSubmit"] {
        background-color: #7C3AED !important;
        border-radius: 50% !important;
        color: white !important;
    }

    /* Welcome Text */
    .hero-title {
        font-size: 56px !important;
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        margin-bottom: 0px !important;
    }
    .hero-subtitle {
        color: #4A4B50 !important;
        font-size: 24px !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Бүх товчлуур, цэсүүд орсон)
with st.sidebar:
    st.markdown('<div class="logo-container">ZeppFusion</div>', unsafe_allow_html=True)
    
    if st.button("＋ Start New Project"):
        st.session_state.messages = []
        st.rerun()

    st.text_input("Search", placeholder="Search project...", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Цэсний элементүүд (VOXA-ийн иконуудтай адилхан)
    st.markdown("""
        <div class="nav-item active"><span class="nav-icon">🏠</span> My Projects</div>
        <div class="nav-item"><span class="nav-icon">💬</span> Chats</div>
        <div class="nav-item"><span class="nav-icon">📄</span> Templates</div>
        <div class="nav-item"><span class="nav-icon">⚙️</span> Settings</div>
        <br>
        <p style='color:#4A4B50; font-size:11px; padding-left:12px; font-weight:700;'>CHATS</p>
        <div class="nav-item"><span class="nav-icon">✨</span> Startup Generator</div>
        <div class="nav-item"><span class="nav-icon">📊</span> Pitch Deck Structure</div>
        <div class="nav-item"><span class="nav-icon">💡</span> Future of AI</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter key to chat...")

# 4. Main UI & Chat Logic
if not "messages" in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    # Мэндчилгээний хэсэг
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>Hello, User</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='hero-subtitle'>How can I help you build today?</h2>", unsafe_allow_html=True)
    
    # Feature Cards (VOXA style)
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div style='background:#111214; padding:25px; border-radius:16px; border:1px solid #1F2023;'>
            <h4 style='margin:0;'>🚀 Templates</h4><p style='color:#8E9196; font-size:14px; margin-top:10px;'>Fast-track your workflow with professional AI setups.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div style='background:#111214; padding:25px; border-radius:16px; border:1px solid #1F2023;'>
            <h4 style='margin:0;'>🧠 Custom Tools</h4><p style='color:#8E9196; font-size:14px; margin-top:10px;'>Configure ZeppFusion for your specific industry needs.</p>
        </div>""", unsafe_allow_html=True)
else:
    # Чат харуулах
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Chat Input (Функциональ)
if prompt := st.chat_input("Ask me something or type '/' for commands..."):
    if not api_key:
        st.error("Please enter your API Key in the sidebar first!")
    else:
        # Хэрэглэгчийн мессеж
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # AI Response
        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Санах ойтой чатлах
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat_session = model.start_chat(history=history)
                
                with st.spinner("Thinking..."):
                    response = chat_session.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
        st.rerun()

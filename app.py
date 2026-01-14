import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="VOXA Pro", page_icon="⚡", layout="wide")

# 2. Pixel-Perfect VOXA CSS
st.markdown("""
    <style>
    /* Үндсэн Background */
    .stApp {
        background-color: #0F1012 !important;
        color: #E2E8F0 !important;
    }

    /* Sidebar - VOXA Dark */
    section[data-testid="stSidebar"] {
        background-color: #080809 !important;
        border-right: 1px solid #1F2023 !important;
    }

    /* ЧАТ БИЧИХ ХЭСЭГ - ЯГ ТЭР ДИЗАЙН */
    .stChatInputContainer {
        padding: 20px !important;
        background: transparent !important;
        bottom: 10px !important;
    }
    
    /* Input-ийн хүрээ */
    .stChatInputContainer > div {
        background-color: #161719 !important;
        border: 1px solid #232528 !important;
        border-radius: 30px !important; /* VOXA-ийн бөөрөнхий загвар */
        padding: 5px 15px 5px 45px !important; /* Зүүн талд товчлуурын зай авах */
        box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
    }

    /* Файл хавсаргах (+) товчлуур - Зүүн талд */
    .stChatInputContainer::before {
        content: '＋';
        position: absolute;
        left: 35px;
        bottom: 35px;
        z-index: 1000;
        color: #8E9196;
        font-size: 20px;
        cursor: pointer;
    }

    /* Microphone (Дуу) товчлуур - Баруун талд (Send товчны хажууд) */
    .stChatInputContainer::after {
        content: '🎤';
        position: absolute;
        right: 80px;
        bottom: 35px;
        z-index: 1000;
        color: #8E9196;
        font-size: 18px;
        cursor: pointer;
    }

    /* Send товчлуур - VOXA Purple */
    [data-testid="stChatInputSubmit"] {
        background-color: #7C3AED !important;
        border-radius: 50% !important;
        color: white !important;
        padding: 5px !important;
    }

    /* Чатны түүх - Bubble биш, Clean line design */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border-bottom: 1px solid #1A1B1E !important;
        padding: 30px 0px !important;
    }
    
    /* Sidebar-ийн "New Chat" товчлуур */
    div.stButton > button {
        background: white !important;
        color: black !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 12px !important;
        width: 100% !important;
    }

    /* Menu Items */
    .menu-item {
        display: flex; align-items: center; padding: 12px; margin: 4px 0;
        border-radius: 10px; color: #8E9196; font-size: 14px; cursor: pointer;
    }
    .active-menu { background-color: #1A1B1E; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.markdown("<h2 style='color:white; margin-bottom:20px;'>VOXA</h2>", unsafe_allow_html=True)
    if st.button("＋ Start New Project"):
        st.session_state.messages = []
        st.rerun()
    
    st.text_input("Search", placeholder="Search project...", label_visibility="collapsed")
    
    st.markdown("""
    <div class="menu-item active-menu">🏠 My Projects</div>
    <div class="menu-item">💬 Chats</div>
    <div class="menu-item">📄 Templates</div>
    <div class="menu-item">⚙️ Settings</div>
    <br>
    <p style='color:#4A4B50; font-size:10px; padding-left:12px;'>RECENT HISTORY</p>
    <div class="menu-item">✨ Startup Generator</div>
    <div class="menu-item">📊 Pitch Deck Structure</div>
    """, unsafe_allow_html=True)

# 4. Main Chat Logic
if not "messages" in st.session_state:
    st.session_state.messages = []

# Welcome Screen (Зураг дээрх шиг цэвэрхэн)
if not st.session_state.messages:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:56px; font-weight:800;'>Hello, <span style='color:#7C3AED;'>ZeppFusion</span></h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#4A4B50;'>How can I help you build today?</h3>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# --- VOXA Input Logic ---
if prompt := st.chat_input("Ask me something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# AI Response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="⚡"):
        # Энд та өөрийн API логикоо нэмээрэй
        st.write("ZeppFusion Pro is processing your request...")

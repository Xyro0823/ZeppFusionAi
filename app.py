import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="ZeppFusion VOXA", page_icon="⚡", layout="wide")

# 2. Advanced CSS - VOXA Premium Dark UI
st.markdown("""
    <style>
    /* Үндсэн Background */
    .stApp {
        background-color: #0B0C0E !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar - VOXA Style */
    section[data-testid="stSidebar"] {
        background-color: #111214 !important;
        border-right: 1px solid #1F2023 !important;
        width: 280px !important;
    }

    /* Sidebar доторх хайлтын хэсэг */
    .stTextInput input {
        background-color: #1A1B1E !important;
        border: 1px solid #2D2E32 !important;
        border-radius: 8px !important;
        color: white !important;
    }

    /* Чатны хэсгийг голлуулах */
    .main .block-container {
        max-width: 850px !important;
        padding-top: 3rem !important;
        padding-bottom: 8rem !important;
    }

    /* VOXA Chat Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #16171B !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        border: 1px solid #232428 !important;
    }

    /* Input Box - Floating ChatGPT Style */
    .stChatInputContainer {
        background-color: transparent !important;
        padding: 20px !important;
        bottom: 20px !important;
    }
    .stChatInputContainer > div {
        background-color: #1A1B1E !important;
        border: 1px solid #2D2E32 !important;
        border-radius: 12px !important;
        padding: 8px !important;
    }

    /* Custom Sidebar Menu Items */
    .menu-item {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 5px;
        color: #94A3B8;
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
    }
    .menu-item:hover {
        background-color: #1F2023;
        color: white;
    }
    .active-menu {
        background-color: #2D2E32;
        color: white;
    }

    /* Logo Gradient */
    .logo-text {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(to right, #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (VOXA Navigation)
with st.sidebar:
    st.markdown('<p class="logo-text">VOXA AI</p>', unsafe_allow_html=True)
    
    # New Chat Button
    if st.button("＋ New Project", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.text_input("Search chats...", placeholder="Find anything...", label_visibility="collapsed")
    
    # Mock Menu
    st.markdown("""
        <div class="menu-item active-menu">🏠 My Projects</div>
        <div class="menu-item">💬 Recent Chats</div>
        <div class="menu-item">🎨 Templates</div>
        <div class="menu-item">⚙️ Settings</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your key...")

# 4. Main UI & Logic
if not api_key:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:48px; font-weight:800;'>Welcome back, User</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748B; font-size:18px;'>Ready to build something amazing today?</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Please enter your API Key in the sidebar to unlock ZeppFusion VOXA.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input Box
    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Context Memory
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                with st.spinner("Analyzing..."):
                    response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"System Error: {e}")
            

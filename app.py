import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="VOXA AI", page_icon="⚡", layout="wide")

# 2. VOXA-ийн нарийн деталуудыг тусгасан CSS
st.markdown("""
    <style>
    /* Ерөнхий дэвсгэр - VOXA Dark */
    .stApp {
        background-color: #0F1012 !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar - Нарийн деталь: Гүн хар, нарийн хүрээтэй */
    section[data-testid="stSidebar"] {
        background-color: #080809 !important;
        border-right: 1px solid #1F2023 !important;
        width: 280px !important;
    }
    
    /* Sidebar-ийн Search Bar */
    .stTextInput input {
        background-color: #161719 !important;
        border: 1px solid #232528 !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
    }

    /* Цэсний элементүүд - VOXA Icons & Spacing */
    .menu-item {
        display: flex;
        align-items: center;
        padding: 10px 12px;
        margin: 4px 0;
        border-radius: 10px;
        color: #8E9196;
        font-size: 14px;
        font-weight: 500;
        transition: 0.2s;
        cursor: pointer;
    }
    .menu-item:hover {
        background-color: #161719;
        color: #FFFFFF;
    }
    .active-menu {
        background-color: #1A1B1E;
        color: #FFFFFF !important;
    }
    .menu-icon {
        margin-right: 12px;
        width: 18px;
        opacity: 0.7;
    }

    /* Чатны хэсэг - Пропорци */
    .main .block-container {
        max-width: 950px !important;
        padding-top: 2rem !important;
    }

    /* Мессежүүд - VOXA Bubble Design */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border-bottom: 1px solid #1A1B1E !important;
        padding: 24px 0 !important;
        border-radius: 0px !important;
    }
    
    /* "Start New Project" товч - VOXA style */
    div.stButton > button {
        background: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        height: 45px !important;
        margin-bottom: 20px !important;
    }

    /* Доод талын Input - Floating Card */
    .stChatInputContainer {
        padding: 20px 0 !important;
        background: transparent !important;
        bottom: 20px !important;
    }
    .stChatInputContainer > div {
        background-color: #161719 !important;
        border: 1px solid #232528 !important;
        border-radius: 16px !important;
        padding: 10px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
    }

    /* Welcome Grid */
    .welcome-card {
        background: #111214;
        border: 1px solid #1F2023;
        padding: 24px;
        border-radius: 16px;
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (VOXA True Structure)
with st.sidebar:
    st.markdown("<h2 style='color:white; padding: 10px 0;'>VOXA</h2>", unsafe_allow_html=True)
    
    if st.button("＋ Start New Project"):
        st.session_state.messages = []
        st.rerun()

    st.text_input("Search", placeholder="Search project...", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # VOXA Menu Items
    menu_html = """
    <div class="menu-item active-menu"><span class="menu-icon">📁</span> My Projects</div>
    <div class="menu-item"><span class="menu-icon">💬</span> Chats</div>
    <div class="menu-item"><span class="menu-icon">📄</span> Templates</div>
    <div class="menu-item"><span class="menu-icon">⚙️</span> Settings</div>
    <br>
    <p style='color:#4A4B50; font-size:11px; padding-left:12px; letter-spacing:1px;'>CHATS</p>
    <div class="menu-item"><span class="menu-icon">✨</span> Startup Generator</div>
    <div class="menu-item"><span class="menu-icon">📅</span> Weekend Ideas</div>
    <div class="menu-item"><span class="menu-icon">📊</span> Pitch Deck Structure</div>
    """
    st.markdown(menu_html, unsafe_allow_html=True)

    st.markdown("---")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your key...")

# 4. Main Chat Engine
if not api_key:
    # VOXA Dashboard Style
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:52px; font-weight:800; letter-spacing:-2px;'>VOXA Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8E9196; font-size:18px;'>Select a template or start a new project to begin.</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="welcome-card"><h3>🚀 Templates</h3><p style="color:#64748B">Fast-track your workflow with AI templates.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="welcome-card"><h3>🛠️ Custom Tools</h3><p style="color:#64748B">Configure AI models for specific tasks.</p></div>', unsafe_allow_html=True)
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # VOXA Style Prompt Input
    if prompt := st.chat_input("Ask me something or type '/' for commands..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Memory
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                with st.spinner("Processing..."):
                    response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")

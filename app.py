import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="ZeppFusion", page_icon="⚡", layout="wide")

# 2. Custom CSS - Icons-гүй, Баруун/Зүүн байрлалтай дизайн
st.markdown("""
    <style>
    /* Стандарт элементүүдийг устгах */
    header, footer, .stDeployButton, [data-testid="stToolbar"] { display: none !important; }
    
    .stApp {
        background-color: #0B0B0C !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    /* --- SIDEBAR DESIGN --- */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #1A1A1C !important;
        width: 260px !important;
    }
    
    .sidebar-title {
        color: white; font-size: 20px; font-weight: 700; 
        padding: 20px 10px; letter-spacing: -0.5px;
    }

    /* --- CHAT BUBBLES - NO ICONS --- */
    /* Нийт чатны контейнер */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 10px 0 !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* Стандарт икон болон аватарыг устгах */
    [data-testid="stChatMessageAvatarUser"], 
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stAvatar"] {
        display: none !important;
    }

    /* Хэрэглэгчийн мессеж - Баруун талд */
    [data-testid="stChatMessageContent"]:has(p:only-child) {
        width: 100% !important;
    }

    /* Хэрэглэгчийн мессежийг баруун тийш шахах */
    .st-emotion-cache-janbn0 { 
        flex-direction: row-reverse !important;
    }

    /* Message Bubble Styles */
    .user-bubble {
        background-color: #2F2F32;
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 4px 20px;
        max-width: 70%;
        margin-left: auto; /* Баруун талд */
        font-size: 15px;
    }

    .bot-bubble {
        background-color: #1A1A1C;
        color: #E2E2E6;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 4px;
        max-width: 85%;
        margin-right: auto; /* Зүүн талд */
        border: 1px solid #27272A;
        font-size: 15px;
        line-height: 1.6;
    }

    /* --- INPUT BAR --- */
    .stChatInputContainer {
        background-color: transparent !important;
        padding: 20px 15% !important;
    }
    .stChatInputContainer > div {
        background-color: #1A1A1C !important;
        border: 1px solid #27272A !important;
        border-radius: 24px !important;
    }

    /* Main Container Padding */
    .main .block-container {
        max-width: 900px !important;
        padding-bottom: 150px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Navigation
with st.sidebar:
    st.markdown('<div class="sidebar-title">ZeppFusion</div>', unsafe_allow_html=True)
    
    if st.button("＋ New Project", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='color:#666; font-size:12px; font-weight:600; padding:10px;'>RECENT</div>
        <div style='color:#999; font-size:14px; padding:8px 10px; cursor:pointer;'>• Design System</div>
        <div style='color:#999; font-size:14px; padding:8px 10px; cursor:pointer;'>• Market Analysis</div>
    """, unsafe_allow_html=True)

    # API Key Input
    st.markdown("<div style='position:fixed; bottom:20px; width:220px;'>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API", type="password", placeholder="Enter Key")
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Chat Engine Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# Empty State
if not st.session_state.messages:
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:white; font-size:32px; font-weight:600; opacity:0.8;'>What's on your mind?</h1>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-bubble">{message["content"]}</div>', unsafe_allow_html=True)

# 5. Input Functionality
if prompt := st.chat_input("Ask ZeppFusion..."):
    if not api_key:
        st.error("Please add API Key.")
    else:
        # Хэрэглэгчийн мессежийг шууд харуулах
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # AI-ийн хариултыг авах
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat = model.start_chat(history=history)
            
            response = chat.send_message(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

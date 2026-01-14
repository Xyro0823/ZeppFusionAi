import streamlit as st
import google.generativeai as genai

# 1. Page Config - Бүх зүйлийг ChatGPT шиг цэвэрхэн болгох
st.set_page_config(page_title="ZeppFusion", page_icon="⚡", layout="wide")

# 2. Extreme CSS Clean-up (ChatGPT 2026 Style)
st.markdown("""
    <style>
    /* 1. Бүх стандарт Streamlit элементүүдийг устгах */
    header, footer, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. Үндсэн Background - ChatGPT Dark */
    .stApp {
        background-color: #212121 !important;
        font-family: -apple-system, system-ui, "Segoe UI", Roboto, sans-serif !important;
    }

    /* 3. Sidebar - Нарийн деталь */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 0.5px solid #333 !important;
        width: 260px !important;
    }
    
    /* "New Chat" товч */
    .stButton > button {
        background-color: #171717 !important;
        color: #ececf1 !important;
        border: 1px solid #4d4d4d !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        margin-top: 10px !important;
    }

    /* 4. Чатны хэсэг - ChatGPT-ийн яг тэр голлуулсан зай */
    .main .block-container {
        max-width: 800px !important;
        padding-top: 2rem !important;
        padding-bottom: 150px !important;
    }

    /* 5. Мессежүүд - Bubble-гүй, Цэвэрхэн (ChatGPT Style) */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 2rem 0 !important;
        border-bottom: none !important;
    }
    
    /* Markdown текстийн өнгө, фонт */
    .stMarkdown p, .stMarkdown li {
        color: #e3e3e3 !important;
        font-size: 16px !important;
        line-height: 1.7 !important;
    }

    /* 6. FLOATING INPUT BOX - ХАМГИЙН ЧУХАЛ */
    .stChatInputContainer {
        padding: 20px 0 !important;
        background-color: transparent !important;
        bottom: 30px !important;
    }
    .stChatInputContainer > div {
        background-color: #2f2f2f !important;
        border: 1px solid #444 !important;
        border-radius: 30px !important; /* Маш бөөрөнхий */
        padding: 10px 18px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
    }
    
    /* Input доторх бичвэр */
    .stChatInputContainer textarea {
        color: white !important;
        font-size: 16px !important;
    }

    /* Send товч */
    [data-testid="stChatInputSubmit"] {
        background-color: white !important;
        color: black !important;
        border-radius: 50% !important;
        padding: 8px !important;
    }

    /* 7. Аватар зурагнууд */
    [data-testid="stChatMessage"] [data-testid="stAvatar"] {
        width: 32px !important;
        height: 32px !important;
        border-radius: 50% !important;
        border: 1px solid #444 !important;
    }

    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Implementation
with st.sidebar:
    st.markdown("<h3 style='color:white; padding:10px 0; font-weight:500;'>ZeppFusion</h3>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br><p style='color:#666; font-size:12px; font-weight:700; padding-left:10px;'>RECENT HISTORY</p>", unsafe_allow_html=True)
    st.caption("• Business Strategy Chat")
    st.caption("• Python Bug Fixes")
    
    # API Key Input - Хамгийн доор
    st.markdown("<div style='position:fixed; bottom:20px; width:220px;'>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your key...")
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Chat Engine
if "messages" not in st.session_state:
    st.session_state.messages = []

# Мэндчилгээ (Empty State)
if not st.session_state.messages:
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:36px; font-weight:600; color:white;'>What can I help with?</h1>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        # ChatGPT Avatar URL (AI тал)
        avatar = "https://cdn.oaistatic.com/_next/static/media/apple-touch-icon.59f2e89e.png" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# 5. Chat Input Logic
if prompt := st.chat_input("Message ZeppFusion..."):
    if not api_key:
        st.error("👈 Please enter your Gemini API Key in the sidebar.")
    else:
        # User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Response
        with st.chat_message("assistant", avatar="https://cdn.oaistatic.com/_next/static/media/apple-touch-icon.59f2e89e.png"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Context Memory
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat_session = model.start_chat(history=history)
                
                with st.spinner(""):
                    response = chat_session.send_message(prompt)
                    full_text = response.text
                
                st.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
            except Exception as e:
                st.error(f"Error: {e}")

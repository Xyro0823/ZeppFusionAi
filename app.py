import streamlit as st
import google.generativeai as genai

# 1. Page Config - Бүх зүйлийг ChatGPT шиг болгох
st.set_page_config(page_title="ZeppFusion", page_icon="🤖", layout="wide")

# 2. ChatGPT True Clone CSS
st.markdown("""
    <style>
    /* 1. Үндсэн фонт болон Background */
    @import url('https://fonts.googleapis.com/css2?family=SNE:wght@400;500;600&display=swap');
    
    .stApp {
        background-color: #212121 !important;
        font-family: 'SNE', -apple-system, sans-serif !important;
    }

    /* 2. Sidebar - ChatGPT-ийн зөөлөн хар */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: none !important;
        width: 260px !important;
    }

    /* 3. "New Chat" товчийг цэвэрхэн болгох */
    .stButton > button {
        background-color: transparent !important;
        color: #ececf1 !important;
        border: 1px solid #4d4d4d !important;
        border-radius: 8px !important;
        text-align: left !important;
        padding: 10px 15px !important;
        width: 100% !important;
        font-weight: 500 !important;
    }
    .stButton > button:hover {
        background-color: #2f2f2f !important;
        border-color: #4d4d4d !important;
    }

    /* 4. Чатны хэсэг - ChatGPT-ийн яг тэр өргөн */
    .main .block-container {
        max-width: 780px !important;
        padding-top: 1rem !important;
        padding-bottom: 150px !important;
    }

    /* 5. Чатны мессежүүд - Bubble биш, "Clean Line" */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border-bottom: none !important;
        margin-bottom: 10px !important;
        padding: 1.5rem 0 !important;
    }
    
    /* Аватар зурагны хэмжээ */
    [data-testid="stChatMessage"] img {
        border-radius: 4px !important;
        width: 30px !important;
        height: 30px !important;
    }

    /* 6. INPUT BOX - Хөвдөг, бөөрөнхий (Яг ChatGPT) */
    .stChatInputContainer {
        padding: 20px 0 !important;
        background-color: transparent !important;
        bottom: 30px !important;
    }
    .stChatInputContainer > div {
        background-color: #2f2f2f !important;
        border: 1px solid #4d4d4d !important;
        border-radius: 26px !important; /* ChatGPT-ийн бөөрөнхий хүрээ */
        padding: 8px 12px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }
    
    /* Input доторх "Clip" (Файл хавсаргах) дүрсийг дуурайх */
    .stChatInputContainer::before {
        content: '📎';
        position: absolute;
        left: 20px;
        bottom: 45px;
        z-index: 100;
        font-size: 18px;
        opacity: 0.5;
        cursor: pointer;
    }

    /* 7. Дээд талын Header-ийг нуух */
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* 8. Markdown текстийн харагдац */
    .stMarkdown p {
        color: #d1d1d1 !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Chat History)
with st.sidebar:
    st.markdown("<h3 style='color:white; margin:10px 0 20px 5px; font-weight:600;'>ZeppFusion</h3>", unsafe_allow_html=True)
    
    if st.button("＋ New chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br><p style='color:#8e8e93; font-size:11px; font-weight:700; padding-left:10px; letter-spacing:0.5px;'>TODAY</p>", unsafe_allow_html=True)
    st.caption("• Project idea brainstorm")
    st.caption("• Coding bug fix")

    # API Key-г доор нь нуух
    st.markdown("<div style='position:fixed; bottom:20px; width:220px;'>", unsafe_allow_html=True)
    api_key = st.text_input("API Key", type="password", placeholder="Enter key...")
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Main Engine
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome Screen (ChatGPT Logo Style)
if not st.session_state.messages:
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:32px; font-weight:600;'>What can I help with?</h1>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        # ChatGPT-ийн AI аватар зураг (ногоон дүрс)
        avatar = "https://cdn.oaistatic.com/_next/static/media/apple-touch-icon.59f2e89e.png" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# 5. Chat Input
if prompt := st.chat_input("Message ZeppFusion..."):
    if not api_key:
        st.error("Please enter your API Key in the sidebar.")
    else:
        # User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Assistant Response
        with st.chat_message("assistant", avatar="https://cdn.oaistatic.com/_next/static/media/apple-touch-icon.59f2e89e.png"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Context Management
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat_session = model.start_chat(history=history)
                
                with st.spinner(""):
                    response = chat_session.send_message(prompt)
                    full_response = response.text
                
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"System Error: {e}")

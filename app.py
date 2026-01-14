import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="ZeppFusion", page_icon="🤖", layout="wide")

# 2. ChatGPT Pixel-Perfect CSS
st.markdown("""
    <style>
    /* Үндсэн Background */
    .stApp {
        background-color: #212121 !important;
        color: #ececf1 !important;
        font-family: 'SNE', -apple-system, system-ui, sans-serif !important;
    }

    /* Sidebar - Яг ChatGPT-ийн өнгө */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        width: 260px !important;
    }

    /* Sidebar-ийн "New Chat" товчлуур */
    .stButton > button {
        background-color: transparent !important;
        color: white !important;
        border: 1px solid #4d4d4d !important;
        border-radius: 8px !important;
        width: 100% !important;
        padding: 10px !important;
        text-align: left !important;
        font-size: 14px !important;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #2f2f2f !important;
    }

    /* Чатны хэсгийг ChatGPT шиг голлуулах */
    .main .block-container {
        max-width: 760px !important;
        padding-top: 2rem !important;
        padding-bottom: 8rem !important;
    }

    /* ChatGPT Message Style (No bubbles, just lines) */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border-bottom: none !important;
        padding: 1rem 0 !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }

    /* AI-ийн мессежийг ялгах зөөлөн дэвсгэр (хүсвэл) */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: transparent !important;
    }

    /* ChatGPT Input Bar - Floating & Rounded */
    .stChatInputContainer {
        background-color: transparent !important;
        padding-bottom: 30px !important;
    }
    .stChatInputContainer > div {
        background-color: #2f2f2f !important;
        border: 1px solid #4d4d4d !important;
        border-radius: 20px !important;
        padding: 5px 10px !important;
    }
    
    /* Зүүн талын (+) дүрсний simulation */
    .stChatInputContainer::before {
        content: '📎';
        position: absolute;
        left: 25px;
        bottom: 45px;
        z-index: 100;
        font-size: 20px;
        opacity: 0.5;
    }

    /* Header - ChatGPT Style "ZeppFusion 2.5" */
    .chat-header {
        position: sticky;
        top: 0;
        background-color: rgba(33, 33, 33, 0.8);
        padding: 10px 0;
        text-align: center;
        font-weight: 600;
        font-size: 18px;
        z-index: 999;
    }

    /* Markdown Code Block Style */
    code {
        background-color: #0d0d0d !important;
        color: #f8f8f2 !important;
        padding: 2px 5px !important;
        border-radius: 4px !important;
    }
    </style>
    <div class="chat-header">ZeppFusion 2.5 ✨</div>
    """, unsafe_allow_html=True)

# 3. Sidebar (History & Auth)
with st.sidebar:
    if st.button("＋ New chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8e8e93; font-size:12px; font-weight:600;'>HISTORY</p>", unsafe_allow_html=True)
    st.caption("• Startup Strategy session")
    st.caption("• Python Code optimization")
    
    st.markdown("<div style='position:fixed; bottom:20px; width:220px;'>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your key...")
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Chat Engine
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome State (ChatGPT Center Logo)
if not st.session_state.messages:
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:32px; font-weight:600;'>How can I help you today?</h1>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        # ChatGPT Avatar simulation
        avatar = "https://cdn.oaistatic.com/_next/static/media/apple-touch-icon.59f2e89e.png" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# 5. Input Functionality
if prompt := st.chat_input("Message ZeppFusion..."):
    if not api_key:
        st.error("Please enter your API Key in the sidebar.")
    else:
        # Add User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Response
        with st.chat_message("assistant", avatar="https://cdn.oaistatic.com/_next/static/media/apple-touch-icon.59f2e89e.png"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Context Management
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                response_placeholder = st.empty()
                full_response = ""
                
                # Typing effect simulation
                with st.spinner(""):
                    response = chat.send_message(prompt)
                    full_response = response.text
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Error: {e}")

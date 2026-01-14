import streamlit as st
import google.generativeai as genai
import time

# 1. Page Config
st.set_page_config(page_title="ZeppFusion", page_icon="⚡", layout="wide")

# 2. Advanced CSS (Бичлэг дээрх дизайныг 100% дуурайсан)
st.markdown("""
    <style>
    /* Үндсэн Background */
    .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Sidebar - Бичлэг дээрх шиг цэвэрхэн */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #1A1A1A !important;
        width: 260px !important;
    }

    /* Sidebar Profile - Хамгийн доор байрлах хэсэг */
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        width: 220px;
        padding: 15px;
        background: #0A0A0A;
        border: 1px solid #1A1A1A;
        border-radius: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Input Bar - Яг бичлэг дээрх шиг бөөрөнхий */
    .stChatInputContainer {
        padding: 20px 10% !important;
        background: transparent !important;
    }
    .stChatInputContainer > div {
        background-color: #0A0A0A !important;
        border: 1px solid #1A1A1A !important;
        border-radius: 35px !important;
        padding-left: 45px !important;
        height: 55px;
    }

    /* [+] Товчлуур */
    .stChatInputContainer::before {
        content: '+';
        position: absolute;
        left: 8.5%;
        bottom: 42px;
        z-index: 100;
        color: #8E8E93;
        font-size: 24px;
        cursor: pointer;
    }

    /* Микрофон дүрс */
    .stChatInputContainer::after {
        content: '🎙️';
        position: absolute;
        right: 13.5%;
        bottom: 42px;
        z-index: 100;
        opacity: 0.5;
    }

    /* Илгээх товч - Нил ягаан */
    [data-testid="stChatInputSubmit"] {
        background-color: #6366F1 !important;
        border-radius: 50% !important;
        padding: 6px !important;
        margin-right: 5px;
    }

    /* Мессежүүд гарч ирэх эффект */
    .chat-msg {
        animation: fadeIn 0.5s ease-in;
        border-bottom: 1px solid #111111;
        padding: 25px 0;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Sidebar Menu */
    .nav-link {
        padding: 12px;
        margin: 4px 0;
        border-radius: 12px;
        color: #8E8E93;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: 0.3s;
    }
    .nav-link:hover { background: #111111; color: white; }
    .active-nav { background: #111111; color: white !important; }

    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Layout
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:30px; letter-spacing:-1px;'>ZeppFusion</h2>", unsafe_allow_html=True)
    
    if st.button("＋ Start New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="nav-link active-nav">🏠 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-link">💬 Chat History</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-link">🎨 Design Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-link">⚙️ Settings</div>', unsafe_allow_html=True)

    # Sidebar Profile (Бичлэг дээрх шиг доор нь)
    st.markdown("""
        <div class="sidebar-footer">
            <div style="width:35px; height:35px; background:linear-gradient(45deg, #6366F1, #A855F7); border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold;">U</div>
            <div>
                <div style="font-size:14px; font-weight:600;">User Name</div>
                <div style="font-size:11px; color:#8E8E93;">Personal Account</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 4. Main Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome Screen (Бичлэг дээрх шиг)
if not st.session_state.messages:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:64px; font-weight:800; text-align:center;'>What can I help <br>you build?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8E8E93; font-size:20px;'>ZeppFusion AI is ready for your command.</p>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.container():
            st.markdown(f'<div class="chat-msg">', unsafe_allow_html=True)
            avatar = "👤" if message["role"] == "user" else "⚡"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
            st.markdown('</div>', unsafe_allow_html=True)

# 5. API Logic
with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini Key", type="password", placeholder="Enter key...")

# Chat Input
if prompt := st.chat_input("Ask anything..."):
    if not api_key:
        st.info("👈 Please enter your Gemini API Key in the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Context Memory
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                response = chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
        st.rerun()

import streamlit as st
import google.generativeai as genai

# 1. Page Config - Бүх зүйлийг цэвэрлэх
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# 2. Super UI Design - CSS Injection
st.markdown("""
    <style>
    /* Стандарт элементүүдийг устгах */
    header, footer, .stDeployButton, [data-testid="stToolbar"] { display: none !important; }

    /* Background & Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    .stApp {
        background-color: #0d0d0f !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar - Minimalist & Glass style */
    section[data-testid="stSidebar"] {
        background-color: #080809 !important;
        border-right: 1px solid #1f1f23 !important;
        width: 260px !important;
    }

    /* Sidebar Menu */
    .nav-item {
        display: flex; align-items: center; padding: 10px 14px;
        margin: 4px 10px; border-radius: 8px; color: #94949e;
        font-size: 14px; transition: 0.2s; cursor: pointer;
    }
    .nav-item:hover { background: #1a1a1e; color: white; }
    .nav-item.active { background: #1a1a1e; color: white; font-weight: 500; }

    /* Main Content Area */
    .main .block-container {
        max-width: 900px !important;
        padding-top: 4rem !important;
        padding-bottom: 180px !important;
    }

    /* Messages - Modern Claude Style */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 1.5rem 0 !important;
    }
    .stMarkdown p {
        color: #e2e2e6 !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }

    /* --- THE ULTIMATE INPUT BAR --- */
    .stChatInputContainer {
        background-color: transparent !important;
        bottom: 40px !important;
    }
    .stChatInputContainer > div {
        background-color: #161618 !important;
        border: 1px solid #27272a !important;
        border-radius: 20px !important;
        padding: 12px 20px 12px 50px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5) !important;
    }

    /* Floating Toolbar Icons (Decoration) */
    .stChatInputContainer::before {
        content: '⊕'; position: absolute; left: 15px; bottom: 15px;
        z-index: 100; color: #a1a1aa; font-size: 24px; cursor: pointer;
    }
    
    /* Send Button Style */
    [data-testid="stChatInputSubmit"] {
        background-color: #ffffff !important;
        border-radius: 50% !important;
        padding: 8px !important;
        box-shadow: 0 4px 10px rgba(255,255,255,0.2);
    }

    /* Welcome Title - Moving Gradient */
    .hero-text {
        background: linear-gradient(to right, #fff, #71717a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 48px; font-weight: 600; text-align: center;
        letter-spacing: -1.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Modern Navigation)
with st.sidebar:
    st.markdown("<div style='padding: 20px 15px;'><h2 style='color:white; font-size:22px; letter-spacing:-1px;'>ZeppFusion</h2></div>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="nav-item active">🏠 Workspace</div>
        <div class="nav-item">🌐 Web Search</div>
        <div class="nav-item">📁 Files & Data</div>
        <div class="nav-item">⚙️ Settings</div>
    """, unsafe_allow_html=True)

    # Sidebar Bottom - User Account
    st.markdown("<div style='position:fixed; bottom:20px; width:220px; padding:15px; border-top:1px solid #1f1f23; display:flex; align-items:center; gap:10px;'>", unsafe_allow_html=True)
    st.markdown("<div style='width:32px; height:32px; background:#3f3f46; border-radius:50%;'></div><div style='color:white; font-size:13px;'>Pro Member</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Chat logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome State
if not st.session_state.messages:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-text'>How can I assist you?</h1>", unsafe_allow_html=True)
    
    # Quick Actions Grid
    cols = st.columns(3)
    with cols[0]: st.markdown("<div style='background:#161618; padding:20px; border-radius:15px; border:1px solid #27272a; color:#a1a1aa; font-size:14px; text-align:center;'>Brainstorm<br>ideas</div>", unsafe_allow_html=True)
    with cols[1]: st.markdown("<div style='background:#161618; padding:20px; border-radius:15px; border:1px solid #27272a; color:#a1a1aa; font-size:14px; text-align:center;'>Write<br>code</div>", unsafe_allow_html=True)
    with cols[2]: st.markdown("<div style='background:#161618; padding:20px; border-radius:15px; border:1px solid #27272a; color:#a1a1aa; font-size:14px; text-align:center;'>Analyze<br>data</div>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. API Key & Input
with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your key...")

if prompt := st.chat_input("Type your message here..."):
    if not api_key:
        st.error("Please add your API Key in settings.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Context Memory
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                response = chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")

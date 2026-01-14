import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta

# 1. Page Config
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# 2. Super Advanced CSS (React Component-ыг 100% дуурайлгасан)
st.markdown("""
    <style>
    /* Үндсэн тохиргоо */
    header, footer, .stDeployButton, [data-testid="stToolbar"] { display: none !important; }
    .stApp { background-color: #09090b !important; font-family: 'Inter', sans-serif !important; }

    /* --- SIDEBAR (React Sidebar-тай ижил) --- */
    section[data-testid="stSidebar"] {
        background-color: rgba(24, 24, 27, 0.9) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px); width: 280px !important;
    }

    /* --- MESSAGE CONTAINER (React ChatMessage-ийн CSS) --- */
    .message-wrapper {
        display: flex; gap: 16px; padding: 24px 16px; border-radius: 12px;
        transition: background 0.3s; margin-bottom: 8px;
    }
    .bot-bg { background-color: rgba(255, 255, 255, 0.02); }
    .user-bg { background-color: transparent; }

    /* Avatar Logic */
    .avatar {
        width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
    }
    .user-avatar { background: linear-gradient(135deg, #3f3f46, #27272a); border: 1px solid #3f3f46; }
    .bot-avatar { background: linear-gradient(135deg, #7c3aed, #9333ea); box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.2); }

    /* Typography & Markdown (React prose-invert overrides) */
    .content-area { flex: 1; min-width: 0; }
    .sender-name { font-size: 14px; font-weight: 500; margin-bottom: 8px; display: block; }
    .user-text { color: #d4d4d8; }
    .bot-text { color: #a78bfa; }
    
    .message-body {
        color: #d4d4d8; line-height: 1.7; font-size: 15px;
    }
    
    /* Code Blocks */
    pre {
        background: #18181b !important; border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important; padding: 16px !important; margin: 16px 0 !important;
    }
    code { color: #c4b5fd !important; background: rgba(124, 58, 237, 0.1) !important; padding: 2px 6px !important; border-radius: 4px !important; }

    /* Actions (Copy/Clock) */
    .actions-row { display: flex; align-items: center; gap: 12px; margin-top: 12px; }
    .expiry-tag {
        display: flex; align-items: center; gap: 6px; padding: 4px 10px;
        background: rgba(39, 39, 42, 0.5); border: 1px solid rgba(63, 63, 70, 0.5);
        border-radius: 8px; font-size: 11px; color: #71717a;
    }

    /* Float Input */
    .stChatInputContainer { padding: 30px 10% !important; background: transparent !important; }
    .stChatInputContainer > div {
        background-color: rgba(24, 24, 27, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important; backdrop-filter: blur(15px);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Component Rendering Function
def render_message(role, content, timestamp, image=None):
    is_user = role == "user"
    bg_class = "user-bg" if is_user else "bot-bg"
    avatar_class = "user-avatar" if is_user else "bot-avatar"
    name_class = "user-text" if is_user else "bot-text"
    name = "You" if is_user else "ZeppFusion"
    avatar_icon = "👤" if is_user else "✨"
    
    expiry_time = (datetime.now() + timedelta(days=7)).strftime("%H:%M %p")
    
    st.markdown(f"""
        <div class="message-wrapper {bg_class}">
            <div class="avatar {avatar_class}">{avatar_icon}</div>
            <div class="content-area">
                <div class="sender-name {name_class}">{name}</div>
                <div class="message-body">{content}</div>
                <div class="actions-row">
                    <div class="expiry-tag">⏱ Expires in 7 days</div>
                    <div style="font-size: 11px; color: #3f3f46;">{timestamp}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 4. Sidebar (React Inspired)
with st.sidebar:
    st.image("https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/69456a8a7026ba13461ef577/a8ac75228_Gemini_Generated_Image_c9qxrc9qxrc9qxrc1.png", width=60)
    st.markdown("<h2 style='color:white; margin-top:0;'>ZeppFusion</h2>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br><div style='color:#71717a; font-size:11px; font-weight:600;'>RECENT CHATS</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#a1a1aa; font-size:13px; padding:10px 0;'>• Project Architecture</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#a1a1aa; font-size:13px; padding:10px 0;'>• UI Style Guide</div>", unsafe_allow_html=True)

    api_key = st.text_input("Gemini API Key", type="password")

# 5. Chat History & Execution
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show history
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"], msg["time"])

# Input logic
if prompt := st.chat_input("Ask ZeppFusion anything..."):
    now = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "user", "content": prompt, "time": now})
    st.rerun()

# API Interaction
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    if not api_key:
        st.warning("Please enter API Key in sidebar")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Streaming effect simulation for UI
            with st.spinner("ZeppFusion is thinking..."):
                response = model.generate_content(st.session_state.messages[-1]["content"])
                bot_now = datetime.now().strftime("%I:%M %p")
                st.session_state.messages.append({"role": "assistant", "content": response.text, "time": bot_now})
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

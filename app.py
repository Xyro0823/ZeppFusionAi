import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="wide")

# 2. Modern UI CSS (Яг таны зураг шиг дизайн)
st.markdown("""
    <style>
    /* Ерөнхий дэвсгэр */
    .stApp {
        background-color: #0D0E10 !important;
        color: #FFFFFF !important;
    }

    /* Sidebar - Зүүн тал */
    [data-testid="stSidebar"] {
        background-color: #121316 !important;
        border-right: 1px solid #232429 !important;
    }

    /* "New Chat" товчлуур - Нил ягаан */
    div.stButton > button {
        background-color: #7C3AED !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }

    /* Төв хэсэг - Мэндчилгээ */
    .welcome-container {
        text-align: center;
        padding: 50px 0 20px 0;
    }
    .welcome-title {
        font-size: 52px !important;
        font-weight: 800 !important;
    }

    /* Feature Cards - 3 том блок */
    .card-grid {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 30px;
    }
    .card-item {
        background: #18191C;
        border: 1px solid #27282B;
        padding: 25px;
        border-radius: 20px;
        flex: 1;
        max-width: 250px;
        text-align: center;
    }

    /* Action Chips - Доод талын жижиг товчлуурууд */
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        margin-top: 40px;
    }
    .chip {
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
        border: 1px solid #27282B;
    }

    /* Prompt Box */
    .stChatInputContainer {
        border-radius: 20px !important;
        background-color: #18191C !important;
        border: 1px solid #27282B !important;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.markdown("<h2 style='color: #7C3AED;'>⚡ ZeppFusion</h2>", unsafe_allow_html=True)
    if st.button("＋ New Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br><b>API Settings</b>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", label_visibility="collapsed", placeholder="Enter Key Here")
    
    st.markdown("<br><b>Vision Tool</b>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

# 4. Main UI Logic
if not api_key:
    # Welcome Screen
    st.markdown("""
        <div class="welcome-container">
            <div style="font-size: 50px;">✨</div>
            <h1 class="welcome-title">Welcome to <span style="color:#7C3AED">ZeppFusion</span></h1>
            <p style="color:#9CA3AF; font-size:18px;">Your intelligent assistant for any question, task, or creative challenge</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 3 Том карт
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card-item"><div style="font-size:24px;">⚡</div><b>Lightning Fast</b><br><small style="color:#6B7280">Get instant responses</small></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card-item"><div style="font-size:24px;">🛡️</div><b>Private & Secure</b><br><small style="color:#6B7280">Your data is safe</small></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card-item"><div style="font-size:24px;">🎨</div><b>Creative Mode</b><br><small style="color:#6B7280">Generate ideas</small></div>', unsafe_allow_html=True)

    # Доод талын "Action Chips" (Зурган дээр байсан товчлуурууд)
    st.markdown("""
        <div class="chip-container">
            <div class="chip" style="color: #60A5FA;">📄 Summarize</div>
            <div class="chip" style="color: #FBBF24;">💡 Explain</div>
            <div class="chip" style="color: #34D399;">💻 Write Code</div>
            <div class="chip" style="color: #F87171;">🌍 Translate</div>
            <div class="chip" style="color: #A78BFA;">🖋️ Rewrite</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("👈 Please enter your Gemini API Key in the sidebar to start.")

else:
    # Чатлах хэсэг
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask ZeppFusion anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Ой санамжтай хариулах
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")

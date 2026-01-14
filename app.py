import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="wide")

# 2. Ultra Modern CSS (Base44 / Vercel Style)
st.markdown("""
    <style>
    /* Үндсэн фон */
    .stApp {
        background-color: #0B0C0E !important;
        color: #FFFFFF !important;
    }

    /* Зүүн талын цэс (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #111214 !important;
        border-right: 1px solid #1F2023 !important;
        width: 320px !important;
    }

    /* Шинэ чат товчлуур - Нил ягаан */
    div.stButton > button {
        background-color: #7C3AED !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #6D28D9 !important;
        transform: translateY(-1px);
    }

    /* Төв хэсгийн Welcome дизайн */
    .main .block-container {
        max-width: 1000px !important;
        padding-top: 2rem !important;
    }

    .welcome-container {
        text-align: center;
        padding: 40px 0;
    }

    .welcome-title {
        font-size: 48px !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
    }

    .welcome-subtitle {
        color: #9CA3AF !important;
        font-size: 18px !important;
        margin-bottom: 40px !important;
    }

    /* Карт хэлбэртэй хэсгүүд */
    .feature-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
        margin-bottom: 40px;
    }

    .feature-card {
        background-color: #18191C;
        border: 1px solid #27282B;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
    }

    .feature-icon {
        font-size: 24px;
        margin-bottom: 12px;
        color: #A78BFA;
    }

    /* Доод талын Input Box */
    .stChatInputContainer {
        background-color: transparent !important;
        bottom: 30px !important;
    }
    .stChatInputContainer > div {
        background-color: #18191C !important;
        border: 1px solid #27282B !important;
        border-radius: 16px !important;
        padding: 8px !important;
    }

    /* Sidebar Input fields */
    .stTextInput input {
        background-color: #18191C !important;
        border: 1px solid #27282B !important;
        border-radius: 10px !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # Лого ба Нэр
    col1, col2 = st.columns([1, 4])
    with col1:
        try: st.image("logo.png", width=40)
        except: st.write("⚡")
    with col2:
        st.markdown("### ZeppFusion")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋ New Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br><p style='color:#6B7280; font-size:12px;'>SETTINGS</p>", unsafe_allow_html=True)
    api_key = st.text_input("API Key", type="password", label_visibility="collapsed", placeholder="Enter your key...")
    
    st.markdown("<br><p style='color:#6B7280; font-size:12px;'>TOOLS</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    st.markdown("<br><br>")
    st.caption("© 2026 ZeppFusion AI")

# 4. Main UI Logic
if not api_key:
    # Скриншот дээрх шиг Welcome Screen
    st.markdown(f"""
        <div class="welcome-container">
            <div style="font-size: 60px; margin-bottom: 20px;">✨</div>
            <h1 class="welcome-title">Welcome to <span style="color: #7C3AED;">ZeppFusion</span></h1>
            <p class="welcome-subtitle">Your intelligent assistant for any question, task, or creative challenge</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature Cards (3 багана)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="feature-card"><div class="feature-icon">⚡</div><b>Lightning Fast</b><br><small style='color:#6B7280'>Get instant intelligent responses</small></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="feature-card"><div class="feature-icon">🛡️</div><b>Private & Secure</b><br><small style='color:#6B7280'>Your chats are protected</small></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="feature-card"><div class="feature-icon">🌐</div><b>Multimodal AI</b><br><small style='color:#6B7280'>Analyze images and text together</small></div>""", unsafe_allow_html=True)

    st.info("👈 Please enter your Gemini API Key in the sidebar to start chatting.")

else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat History
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Input Area
    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            if uploaded_file:
                st.image(uploaded_file, width=300)

        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner(""):
                    if uploaded_file:
                        img = Image.open(uploaded_file)
                        response = model.generate_content([f"Чи бол ZeppFusion AI. Монголоор хариул: {prompt}", img])
                    else:
                        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat = model.start_chat(history=history)
                        response = chat.send_message(prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")

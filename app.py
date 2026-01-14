import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="wide")

# 2. Gemini Official UI/UX Style CSS
st.markdown("""
    <style>
    /* Үндсэн фон болон өнгө */
    .stApp {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }

    /* Зүүн талын цэс (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-right: 1px solid #333537 !important;
        width: 280px !important;
    }

    /* Sidebar доторх New Chat товчлуур */
    .stButton > button {
        border-radius: 20px !important;
        background-color: #1a1c1e !important;
        border: 1px solid #444746 !important;
        color: #e3e3e3 !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #2d2f31 !important;
        border-color: #5f6368 !important;
    }

    /* Чатны талбарыг Gemini шиг голд нь төвлөрүүлэх */
    .main .block-container {
        max-width: 820px !important; /* Нарийн төвлөрсөн чат */
        padding-top: 4rem !important;
        padding-bottom: 8rem !important;
    }

    /* Мэндчилгээний хэсэг */
    .welcome-text {
        font-size: 56px !important;
        font-weight: 500 !important;
        letter-spacing: -1px !important;
        margin-bottom: 0px !important;
    }
    .gradient-text {
        background: linear-gradient(to right, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Асуулт бичих хэсэг (Floating Prompt Bar) */
    .stChatInputContainer {
        padding: 0 !important;
        bottom: 30px !important;
    }
    .stChatInputContainer > div {
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        border-radius: 32px !important;
        padding: 5px 10px !important;
    }

    /* Чатны мессежүүдийн фонт болон зай */
    [data-testid="stChatMessage"] {
        padding: 1.5rem 0rem !important;
        border-bottom: 0px !important;
        background-color: transparent !important;
    }
    .stMarkdown p {
        font-size: 16px !important;
        line-height: 1.6 !important;
    }

    /* Sidebar-ийн гарчигнууд */
    .sidebar-label {
        color: #8e918f !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        margin: 20px 0 10px 0 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Left Menu)
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # Лого
    try:
        st.image("logo.png", width=36)
    except:
        st.markdown("<h3 style='color:#a78bfa'>⚡</h3>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # New Chat
    if st.button("＋ Шинэ чат", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<p class='sidebar-label'>Тохиргоо</p>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", label_visibility="collapsed", placeholder="API түлхүүр...")

    st.markdown("<p class='sidebar-label'>Хэрэгслүүд</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Зураг шинжлэх", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📥 Чатыг татах", chat_text, file_name="zeppfusion_chat.txt", use_container_width=True)

# 4. Main UI Logic
if not api_key:
    # Gemini Home Screen
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='welcome-text gradient-text'>Сайн байна уу?</h1>", unsafe_allow_html=True)
    st.markdown("<h1 class='welcome-text' style='color: #444746;'>Би ZeppFusion байна.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8e918f; font-size: 18px; margin-top: 20px;'>Өнөөдөр танд юугаар туслах вэ?</p>", unsafe_allow_html=True)
    st.info("👈 Үргэлжлүүлэхийн тулд зүүн талын цэсэнд API Key-ээ оруулна уу.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        # Надтай (Gemini) адилхан аватар ашиглах
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Floating Chat Input
    if prompt := st.chat_input("Эндээс асуу..."):
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            if uploaded_file:
                st.image(uploaded_file, width=280)

        # AI Assistant Response
        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner(""):
                    if uploaded_file:
                        img = Image.open(uploaded_file)
                        response = model.generate_content([f"Чи бол ZeppFusion AI. Монголоор хариул: {prompt}", img])
                    else:
                        # Memory chat
                        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat = model.start_chat(history=history)
                        response = chat.send_message(prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Алдаа: {e}")

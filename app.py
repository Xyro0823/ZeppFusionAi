import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="wide")

# 2. Ultra-Clean CSS (Gemini-тэй 99% ижил)
st.markdown("""
    <style>
    .stApp {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }
    /* Sidebar-ыг зөвхөн цэс болгох */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        width: 260px !important;
        border-right: 1px solid #333 !important;
    }
    /* Чатны хэсэг голдоо */
    .main .block-container {
        max-width: 850px !important;
        padding-top: 4rem !important;
    }
    /* Асуулт бичих хэсэг доор бөөрөнхий харагдах */
    .stChatInputContainer {
        bottom: 40px !important;
    }
    .stChatInputContainer > div {
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        border-radius: 28px !important;
    }
    /* Sidebar доторх New Chat товч */
    div.stButton > button {
        border-radius: 24px !important;
        background-color: #1a1c1e !important;
        border: 1px solid #444746 !important;
        color: #e3e3e3 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Одоо энд файл хуулах хэсэг байхгүй)
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚡ ZeppFusion")
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("⚙️ **Settings**")
    api_key = st.text_input("API Key", type="password", placeholder="Paste key...")

# 4. Main Chat UI
if not api_key:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 56px; background: linear-gradient(to right, #4285f4, #9b72cb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Сайн байна уу?</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 56px; color: #444746; margin-top: -20px;'>Би ZeppFusion байна.</h1>", unsafe_allow_html=True)
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Чат харуулах
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"]=="user" else "⚡"):
            st.markdown(message["content"])

    # Чат бичих хэсэг (Файл хуулах хэсгийг энд гарч ирэхээр тохируулж болно)
    if prompt := st.chat_input("Эндээс асуу..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Ой санамжтай чатлах
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")

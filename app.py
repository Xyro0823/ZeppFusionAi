import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Хуудасны тохиргоо - Gemini шиг Wide layout
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="wide")

# 2. ШИНЭЧЛЭГДСЭН CSS - Gemini-ийн дизайныг хүчээр (Force) тулгах
st.markdown("""
    <style>
    /* Үндсэн дэвсгэр өнгө */
    .stApp {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
    }

    /* Sidebar - Зүүн талын цэс */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        width: 260px !important;
    }

    /* Sidebar доторх текстүүд */
    section[data-testid="stSidebar"] .stText, section[data-testid="stSidebar"] label {
        color: #e3e3e3 !important;
    }

    /* Чатны хэсэгт илүү том зай авах */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 6rem;
        max-width: 850px; /* Gemini шиг төвлөрсөн нарийн чат */
    }

    /* Gemini-ийн бөөрөнхий асуулт бичих талбар */
    .stChatInputContainer {
        bottom: 20px !important;
        padding: 0 !important;
    }
    
    .stChatInputContainer > div {
        background-color: #1e1f20 !important;
        border: 1px solid #444746 !important;
        border-radius: 32px !important;
        padding: 5px 15px !important;
    }

    .stChatInputContainer textarea {
        color: #e3e3e3 !important;
    }

    /* Мессежүүдийн дизайн */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border-bottom: 0px solid #333 !important;
        margin-bottom: 20px !important;
    }

    /* Хэрэгслүүдийн товчлуурыг гоё болгох */
    div.stButton > button {
        border-radius: 20px !important;
        background-color: #333537 !important;
        border: none !important;
        color: white !important;
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #444746 !important;
    }

    /* Файл хуулах хэсгийг sidebar-т тааруулах */
    .stFileUploader {
        padding: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar - Gemini Sidebar Style
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        st.image("logo.png", width=50)
    except:
        st.markdown("### ⚡ ZeppFusion")
    
    st.markdown("---")
    
    # Шинэ чат эхлүүлэх (Gemini-ийн "+" товч шиг)
    if st.button("➕ Шинэ чат", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br><b>⚙️ Тохиргоо</b>", unsafe_allow_html=True)
    api_key = st.text_input("API Key:", type="password", label_visibility="collapsed")
    
    st.markdown("<br><b>🛠️ Хэрэгслүүд</b>", unsafe_allow_html=True)
    # Зураг унших хэрэгсэл
    uploaded_file = st.file_uploader("Зураг шинжлэх", type=["jpg", "png", "jpeg"])
    
    # Чат татах хэрэгсэл
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📥 Чатыг татах", chat_text, file_name="chat.txt", use_container_width=True)

# 4. Main Chat Interface
if not api_key:
    # Мэндчилгээний хэсэг (Gemini Style)
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 50px; background: -webkit-linear-gradient(#4285f4, #9b72cb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Сайн байна уу?</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 50px; color: #444746; margin-top: -30px;'>Би ZeppFusion байна.</h1>", unsafe_allow_html=True)
    st.info("👈 Үргэлжлүүлэхийн тулд зүүн талын цэсэнд API Key-ээ оруулна уу.")
else:
    # Ой санамж үүсгэх
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Хуучин яриаг харуулах
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Асуулт бичих хэсэг
    if prompt := st.chat_input("ZeppFusion-ээс асуу..."):
        # Хэрэглэгчийн тал
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            if uploaded_file:
                st.image(uploaded_file, width=300)

        # AI-ийн тал
        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner(""):
                    if uploaded_file:
                        img = Image.open(uploaded_file)
                        response = model.generate_content([f"Чи бол ZeppFusion AI. Монголоор хариул: {prompt}", img])
                    else:
                        # Ой санамжтай чатлах
                        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat = model.start_chat(history=history)
                        response = chat.send_message(prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Алдаа: {e}")

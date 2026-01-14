import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="wide")

# 2. Advanced CSS for True Gemini UI
st.markdown("""
    <style>
    /* Үндсэн фон болон текст */
    .stApp {
        background-color: #131314 !important;
        color: #E3E3E3 !important;
        font-family: 'Google Sans', Arial, sans-serif !important;
    }

    /* Sidebar - Зүүн талын нарийн цэс */
    section[data-testid="stSidebar"] {
        background-color: #1E1F20 !important;
        width: 300px !important;
        border-right: 1px solid #333 !important;
    }

    /* Sidebar доторх элементүүд */
    .st-emotion-cache-6qob1r {
        background-color: #1E1F20 !important;
    }
    
    /* Шинэ чат товчлуур */
    div.stButton > button {
        border-radius: 24px !important;
        background-color: #1A1C1E !important;
        color: #E3E3E3 !important;
        border: 1px solid #444746 !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #2D2F31 !important;
        border-color: #5F6368 !important;
    }

    /* Чатны талбарын хэмжээг Gemini шиг төвлөрүүлэх */
    .main .block-container {
        max-width: 900px !important;
        padding-top: 5rem !important;
    }

    /* Мэндчилгээний текст */
    .gemini-title {
        font-size: 44px !important;
        font-weight: 500 !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 0px !important;
    }
    .gemini-subtitle {
        font-size: 44px !important;
        color: #444746 !important;
        font-weight: 500 !important;
        margin-top: -15px !important;
    }

    /* Input Box (Prompt Bar) */
    .stChatInputContainer {
        padding-bottom: 30px !important;
    }
    .stChatInputContainer > div {
        background-color: #1E1F20 !important;
        border: 1px solid #444746 !important;
        border-radius: 32px !important;
    }

    /* Чатны мессежүүд */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    
    /* Зураг хуулах хэсэг (Sidebar Tool) */
    .stFileUploader section {
        background-color: #1A1C1E !important;
        border: 1px dashed #444746 !important;
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Implementation
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # Логог жижиг бөгөөд цэвэрхэн харуулах
    try:
        st.image("logo.png", width=40)
    except:
        st.markdown("<h2 style='color:#A78BFA'>⚡</h2>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋ Шинэ чат", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br><p style='color:#8E918F; font-size:14px; font-weight:500;'>Тохиргоо</p>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", label_visibility="collapsed", placeholder="API Key оруулна уу")
    
    st.markdown("<br><p style='color:#8E918F; font-size:14px; font-weight:500;'>Хэрэгслүүд</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Зураг шинжлэх", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📥 Чатыг татах", chat_text, file_name="chat_history.txt", use_container_width=True)

# 4. Main Chat Logic
if not api_key:
    # Gemini Welcome Screen
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='gemini-title' style='background: -webkit-linear-gradient(#4285f4, #9b72cb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Сайн байна уу?</h1>", unsafe_allow_html=True)
    st.markdown("<h1 class='gemini-subtitle'>Би ZeppFusion байна.</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Эхлэхийн тулд зүүн талын цэсэнд API Key-ээ оруулна уу.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "⚡"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Эндээс асуу..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            if uploaded_file:
                st.image(uploaded_file, width=300)

        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)
                # Таны ашиглаж буй Gemini 2.5 Flash
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
                st.error(f"Алдаа: {e}")

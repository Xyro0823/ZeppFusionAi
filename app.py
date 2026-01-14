import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Апп-ны үндсэн тохиргоо
st.set_page_config(
    page_title="ZeppFusion AI", 
    page_icon="⚡", 
    layout="wide"
)

# 2. Gemini-ийн "Look and Feel" дизайн (CSS)
st.markdown("""
    <style>
    /* Үндсэн фон болон текст */
    .stApp {
        background-color: #131314;
        color: #E3E3E3;
    }
    
    /* Sidebar дизайн */
    [data-testid="stSidebar"] {
        background-color: #1E1F20;
        border-right: 1px solid #333;
    }
    
    /* Chat input-ийг доор байрлуулж Gemini шиг болгох */
    .stChatInputContainer {
        padding-bottom: 20px;
        background-color: transparent !important;
    }
    
    .stChatInputContainer > div {
        background-color: #1E1F20 !important;
        border: 1px solid #444746 !important;
        border-radius: 28px !important;
    }

    /* Мессежүүдийн харагдац */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        font-family: 'Google Sans', sans-serif;
    }
    
    /* Товчлууруудын дизайн */
    div.stButton > button {
        border-radius: 20px;
        background-color: #333;
        color: white;
        border: 1px solid #444;
    }
    
    /* Гарчиг болон бусад */
    h1, h2, h3 {
        color: #E3E3E3;
        font-weight: 500;
    }
    
    /* Sidebar доторх хэрэгслүүд */
    .sidebar-tool-card {
        background-color: #28292A;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Gemini-ийн зүүн талын цэс шиг)
with st.sidebar:
    try:
        st.image("logo.png", width=60)
    except:
        st.title("⚡")
        
    st.markdown("### ⚙️ Тохиргоо")
    api_key = st.text_input("Gemini API Key:", type="password")
    
    st.markdown("---")
    st.markdown("### 🛠️ Хэрэгслүүд")
    
    # Tool: Vision (Зураг шинжлэх)
    uploaded_file = st.file_uploader("Зураг оруулах", type=["jpg", "png", "jpeg"])
    
    st.markdown("---")
    # Tool: Export
    if "messages" in st.session_state and st.session_state.messages:
        chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📥 Чатыг татах", chat_text, file_name="zeppfusion_history.txt")

    if st.button("➕ Шинэ чат"):
        st.session_state.messages = []
        st.rerun()

# 4. Үндсэн хуудас
if not api_key:
    # Нүүр хуудасны мэндчилгээ (Gemini шиг)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 56px; color: #4B90FF;'>Сайн байна уу?</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 56px; color: #444746;'>Би ZeppFusion AI байна.</h1>", unsafe_allow_html=True)
    st.info("👈 Эхлэхийн тулд зүүн талын цэсэнд API Key-ээ оруулна уу.")
else:
    # AI Logic
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Чат харуулах хэсэг (Layout-ийг Gemini шиг цэвэрхэн болгох)
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                avatar = "👤" if message["role"] == "user" else "⚡"
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

        # Chat Input (Prompt)
        if prompt := st.chat_input("Эндээс асуу..."):
            # Хэрэглэгчийн мессеж
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
                if uploaded_file:
                    st.image(uploaded_file, width=250)

            # AI-ийн хариулт
            with st.chat_message("assistant", avatar="⚡"):
                with st.spinner(""):
                    if uploaded_file:
                        img = Image.open(uploaded_file)
                        response = model.generate_content([f"Чи бол ZeppFusion. Зургийг шинжлээд монголоор хариул: {prompt}", img])
                    else:
                        # Ой санамжтай чат
                        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat_session = model.start_chat(history=history)
                        response = chat_session.send_message(prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Алдаа: {e}")

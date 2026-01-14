import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Апп-ны үндсэн тохиргоо
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="centered")

# 2. Sidebar - Нэмэлт хэрэгслүүд
with st.sidebar:
    st.image("logo.png", width=100)
    st.title("🛠️ Хэрэгслүүд")
    api_key = st.text_input("Gemini API Key:", type="password")
    
    st.markdown("---")
    # TOOL 1: Зураг оруулах хэсэг
    uploaded_file = st.file_uploader("Зураг шинжлэх (Vision)", type=["jpg", "png", "jpeg"])
    
    st.markdown("---")
    # TOOL 2: Чат устгах
    if st.button("🗑️ Чат цэвэрлэх"):
        st.session_state.messages = []
        st.rerun()

    # TOOL 3: Чат татаж авах (Export)
    if "messages" in st.session_state and st.session_state.messages:
        chat_text = ""
        for m in st.session_state.messages:
            chat_text += f"{m['role']}: {m['content']}\n\n"
        st.download_button("📥 Чатыг татах", chat_text, file_name="zeppfusion_chat.txt")

# 3. Үндсэн Logic
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash') # Таны дуртай хувилбар

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Түүх харуулах
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # TOOL 1 Logic: Зурагтай асуулт асуух
        if prompt := st.chat_input("Асуултаа бичнэ үү..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                if uploaded_file:
                    st.image(uploaded_file, caption="Илгээсэн зураг", width=200)

            with st.chat_message("assistant"):
                with st.spinner("ZeppFusion бодож байна..."):
                    if uploaded_file:
                        # Зураг + Текст хосолсон асуулт
                        img = Image.open(uploaded_file)
                        response = model.generate_content([f"Чи бол ZeppFusion. Зургийг шинжлээд монголоор хариул: {prompt}", img])
                    else:
                        # Зөвхөн текст
                        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat = model.start_chat(history=history)
                        response = chat.send_message(prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Алдаа: {e}")
else:
    st.info("👈 Эхлэхийн тулд API Key оруулна уу.")

import streamlit as st
import google.generativeai as genai
from PIL import Image  # Зураг нээхэд ашиглана

# Апп-ны үндсэн тохиргоо
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="centered")

# --- ЛОГО ОРУУЛАХ ХЭСЭГ ---
try:
    image = Image.open('logo.png') # Таны логоны файлын нэр
    # Зургийг төвд нь байрлуулахын тулд багана ашиглана
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(image, width=150) # Өргөнийг нь 150px болгож тохируулав
except:
    st.write("⚡") # Хэрэв лого олдохгүй бол аянга харуулна

st.markdown("<h1 style='text-align: center;'>ZeppFusion AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Монгол хэлээр харилцах ухаалаг туслах</p>", unsafe_allow_html=True)

# Хажуугийн цэс
with st.sidebar:
    st.title("⚙️ Тохиргоо")
    api_key = st.text_input("Google Gemini API Key:", type="password")
    if st.button("Чат цэвэрлэх"):
        st.session_state.messages = []
        st.rerun()

# API Key шалгах ба AI ажиллуулах хэсэг (таны өмнөх код...)
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Энд асуултаа бичнэ үү..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = model.generate_content(f"Чи бол ZeppFusion. Монголоор хариул: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Алдаа: {e}")
else:
    st.info("Үргэлжлүүлэхийн тулд API Key-ээ оруулна уу.")

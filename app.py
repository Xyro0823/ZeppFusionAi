import streamlit as st
import google.generativeai as genai

# Апп-ны үндсэн тохиргоо
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡", layout="centered")

# Хажуугийн цэс
with st.sidebar:
    st.title("⚙️ Тохиргоо")
    api_key = st.text_input("Google Gemini API Key оруулна уу:", type="password")
    st.info("API Key-ээ https://aistudio.google.com/ хуудаснаас үнэгүй авна уу.")
    
    if st.button("Чат цэвэрлэх"):
        st.session_state.messages = []
        st.rerun()

st.title("⚡ ZeppFusion AI")
st.caption("Монгол хэлээр харилцах ухаалаг туслах")

# API Key шалгах
if not api_key:
    st.warning("Үргэлжлүүлэхийн тулд API Key-ээ оруулна уу.")
    st.stop()

# AI тохиргоо
try:
    genai.configure(api_key=api_key)
    
    # Хамгийн тогтвортой ажиллах загварыг сонгох
    # Хэрэв gemini-1.5-flash ажиллахгүй бол gemini-pro руу шилжинэ
    model_name = 'gemini-1.5-flash'
    model = genai.GenerativeModel(model_name)
    
    # Чатны түүхийг хадгалах хэсэг
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Хуучин мессежүүдийг дэлгэцэнд харуулах
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Хэрэглэгчийн оролт (Prompt)
    if prompt := st.chat_input("Энд асуултаа бичнэ үү..."):
        # Хэрэглэгчийн мессежийг харуулах
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI-аас хариулт авах
        with st.chat_message("assistant"):
            with st.spinner("Бодож байна..."):
                try:
                    # ZeppFusion-д зориулсан тусгай зааварчилгаа (System Instruction)
                    full_instruction = f"Чиний нэр ZeppFusion. Чи бол монгол хэлний мэргэжилтэн, туслах AI юм. Хэрэглэгчийн асуултад монгол хэлээр маш ойлгомжтой, найрсаг хариул: {prompt}"
                    
                    response = model.generate_content(full_instruction)
                    
                    if response.text:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.error("AI хариулт өгсөнгүй. Дахин оролдоно уу.")
                except Exception as e:
                    st.error(f"Алдаа гарлаа: {str(e)}")
                    st.info("Зөвлөмж: API Key-ээ шинээр үүсгэж эсвэл VPN ашиглаад үзээрэй.")

except Exception as e:
    st.error(f"Тохиргооны алдаа: {str(e)}")

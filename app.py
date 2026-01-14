import streamlit as st
import google.generativeai as genai

# Апп-ны толгой хэсэг
st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡")
st.title("⚡ ZeppFusion - Монгол AI")

# API түлхүүрээ тохируулах (Нууцлалтай хадгалах хэсэг)
api_key = st.sidebar.text_input("Gemini API Key оруулна уу:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Чатны түүхийг хадгалах
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Хуучин мессежүүдийг харуулах
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Хэрэглэгчийн асуулт авах
    if prompt := st.chat_input("Юу туслах вэ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI хариулт өгөх хэсэг
        with st.chat_message("assistant"):
            # Монгол хэлний зааварчилгааг эхэнд нь нэмж өгөх
            full_prompt = f"Чи бол ZeppFusion нэртэй монгол хэлний AI туслах юм. Дараах асуултанд монголоор хариул: {prompt}"
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
else:

    st.info("Ашиглахын тулд зүүн талын цэсэнд API Key-ээ оруулна уу.")

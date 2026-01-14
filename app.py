import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="ZeppFusion AI", page_icon="⚡")
st.title("⚡ ZeppFusion - Монгол AI")

# API Key-ийг sidebar-аас авах
api_key = st.sidebar.text_input("Gemini API Key оруулна уу:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Энд 'gemini-1.5-flash-latest' гэж бичсэнээр хамгийн шинэ хувилбарыг нь авна
        model = genai.GenerativeModel('models/gemini-1.5-flash')

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Юу туслах вэ?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # System instructions-ийг энд илүү тодорхой болгов
                full_prompt = f"Чи бол ZeppFusion. Монголоор хариул: {prompt}"
                response = model.generate_content(full_prompt)
                
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error("AI хариулт өгч чадсангүй. Дахин оролдоно уу.")

    except Exception as e:
        st.error(f"Алдаа гарлаа: {e}")
else:
    st.info("Ашиглахын тулд API Key-ээ оруулна уу.")


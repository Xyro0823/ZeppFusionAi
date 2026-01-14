import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Апп-ны үндсэн тохиргоо
st.set_page_config(
    page_title="ZeppFusion AI", 
    page_icon="⚡", 
    layout="centered"
)

# 2. Custom CSS - Апп-ыг илүү гоё харагдуулах дизайн
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    .st-emotion-cache-16idsys p {
        font-size: 1.1rem;
    }
    /* Sidebar-ийг гоё болгох */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(#2E1065, #0E1117);
        color: white;
    }
    /* Товчлуурыг логоны өнгөтэй ижил болгох */
    div.stButton > button:first-child {
        background-color: #7C3AED;
        color: white;
        border-radius: 10px;
        border: none;
        width: 100%;
    }
    /* Чатны хөөснүүдийг засах */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar хэсэг
with st.sidebar:
    st.image("logo.png", width=100)
    st.title("⚙️ Тохиргоо")
    api_key = st.text_input("Google Gemini API Key:", type="password", help="AI Studio-оос авсан түлхүүрээ энд хийнэ үү.")
    
    st.markdown("---")
    if st.button("🗑️ Чат цэвэрлэх"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("Version 1.0.2 | Powered by Gemini 2.5 Flash")

# 4. Үндсэн нүүр (Header)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        image = Image.open('logo.png')
        st.image(image, use_container_width=True)
    except:
        st.write("⚡")

st.markdown("<h1 style='text-align: center; color: #A78BFA;'>ZeppFusion AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8; font-style: italic;'>Монгол хэлээр харилцах ухаалаг туслах</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Чатны ой санамжийг ажиллуулах хэсэг ---
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 1. Gemini-ийн чат түүхийг бэлдэх (Ой санамж үүсгэх)
    # Өмнөх мессежүүдийг Gemini-ийн ойлгох форматад оруулна
    history = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in st.session_state.messages
    ]
    
    # Чат сессийг эхлүүлэх
    chat_session = model.start_chat(history=history)

    # Хуучин мессежүүдийг харуулах
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Шинэ асуулт авах
    if prompt := st.chat_input("ZeppFusion-ээс юу ч хамаагүй асуу..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Бодож байна..."):
                # start_chat ашиглаж байгаа тул 'full_instruction' хэрэггүй, 
                # учир нь тэр өмнөх бүх зүйлийг санаж байгаа.
                response = chat_session.send_message(prompt)
                
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.warning("Хариулт ирсэнгүй, дахин оролдоно уу.")
except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
else:
    st.info("👈 Үргэлжлүүлэхийн тулд зүүн талын цэсэнд API Key-ээ оруулна уу.")






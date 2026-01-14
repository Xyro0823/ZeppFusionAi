import streamlit as st
import google.generativeai as genai

# 1. Хуудасны тохиргоо
st.set_page_config(page_title="ZeppFusion AI", page_icon="💬", layout="wide")

# 2. ChatGPT загварын CSS
st.markdown("""
    <style>
    /* Үндсэн дэвсгэр өнгө */
    .stApp {
        background-color: #212121 !important;
        color: #ececf1 !important;
    }

    /* Sidebar - ChatGPT Dark Style */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        width: 260px !important;
        border-right: none !important;
    }

    /* New Chat товчлуур */
    div.stButton > button {
        background-color: transparent !important;
        color: white !important;
        border: 1px solid #4d4d4d !important;
        border-radius: 5px !important;
        width: 100% !important;
        text-align: left !important;
        padding: 10px !important;
    }
    div.stButton > button:hover {
        background-color: #2d2d2d !important;
        border-color: #4d4d4d !important;
    }

    /* Чатны хэсэг (Төвлөрсөн) */
    .main .block-container {
        max-width: 800px !important;
        padding-top: 3rem !important;
        padding-bottom: 6rem !important;
    }

    /* Чатны мессежүүд */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border-bottom: 0.1px solid #3d3d3d !important;
        padding: 1.5rem 1rem !important;
    }
    
    /* Хэрэглэгчийн мессеж болон AI-ийн мессежийг ялгах (Optional) */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #212121 !important;
    }

    /* Input Box - ChatGPT Style */
    .stChatInputContainer {
        padding: 20px !important;
        background-color: transparent !important;
    }
    .stChatInputContainer > div {
        background-color: #2f2f2f !important;
        border: 1px solid #4d4d4d !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* Нуух элементүүд */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (History & Settings)
with st.sidebar:
    st.markdown("<h3 style='color:white; padding:10px;'>ZeppFusion</h3>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8e8e93; font-size:12px; padding-left:10px;'>SETTINGS</p>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste key here...")

# 4. Main UI Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# Мэндчилгээний хэсэг (Чат хоосон үед)
if not st.session_state.messages:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:40px; color:white;'>ZeppFusion</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#c5c5d2; font-size:18px;'>How can I help you today?</p>", unsafe_allow_html=True)

# Мессежүүдийг харуулах
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Чат бичих хэсэг
if prompt := st.chat_input("Message ZeppFusion..."):
    if not api_key:
        st.error("Please enter your API Key in the sidebar first!")
    else:
        # Хэрэглэгчийн мессеж
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI-ийн хариулт
        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash') # Эсвэл өөрийн хүссэн хувилбар
                
                # Context-той чатлах
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat_session = model.start_chat(history=history)
                
                with st.spinner(""):
                    response = chat_session.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")

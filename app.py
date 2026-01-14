import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Page Config
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# 2. Enhanced CSS (ChatGPT Style Input Tools)
st.markdown("""
    <style>
    .stApp { background-color: #08090a !important; color: #f4f4f5 !important; }
    section[data-testid="stSidebar"] { background-color: #0c0d0e !important; border-right: 1px solid #1f2123 !important; }
    
    /* Чатны талбарын зай */
    .main .block-container { max-width: 850px !important; padding-bottom: 12rem !important; }

    /* ChatGPT-ийнх шиг "Paperclip" болон "Image" товчлуурын дизайн */
    .stFileUploader {
        margin-bottom: -45px;
        margin-left: 10px;
        width: 40px !important;
        overflow: hidden;
        z-index: 100;
    }
    
    /* Файл хуулах хэсгийг жижиг товч шиг харагдуулах */
    [data-testid="stFileUploaderDropzone"] {
        padding: 0px !important;
        border: none !important;
        background: transparent !important;
    }
    [data-testid="stFileUploaderDropzone"] > div > small { display: none; }
    [data-testid="stFileUploaderDropzone"] svg { fill: #a1a1aa !important; width: 24px; height: 24px; }

    /* Input Box-ийн дизайн */
    .stChatInputContainer {
        padding: 24px !important;
        bottom: 24px !important;
    }
    .stChatInputContainer > div {
        background-color: #161718 !important;
        border: 1px solid #272a2d !important;
        border-radius: 14px !important;
        padding-left: 45px !important; /* Файл хавсаргах товчны зай */
    }

    /* Message Styling */
    [data-testid="stChatMessage"] { border-bottom: 1px solid #1f2123 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.markdown("<h2 style='color: white;'>⚡ ZeppFusion</h2>", unsafe_allow_html=True)
    if st.button("＋ New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br><p style='color:#52525b; font-size:11px; font-weight:700;'>ACCESS Control</p>", unsafe_allow_html=True)
    api_key = st.text_input("API Key", type="password", label_visibility="collapsed", placeholder="sk-...")

# 4. Main Chat Interface
if not api_key:
    st.markdown("<br><br><h1 style='text-align:center; font-size:52px; font-weight:800;'>How can I assist you?</h1>", unsafe_allow_html=True)
    st.info("👈 Please enter your Gemini API Key to unlock the tools.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Чатны түүх
    for message in st.session_state.messages:
        avatar = "⚡" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if "image" in message:
                st.image(message["image"], width=300)

    # --- INPUT AREA (ChatGPT style with attachment) ---
    
    # ChatGPT шиг файл хавсаргах хэсэг (Зүүн талд нь)
    with st.container():
        uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg", "pdf"], label_visibility="collapsed")
        
        if prompt := st.chat_input("Message ZeppFusion..."):
            # Хэрэглэгчийн мессеж
            new_message = {"role": "user", "content": prompt}
            
            # Хэрэв зураг хавсаргасан бол
            img_to_send = None
            if uploaded_file:
                if uploaded_file.type.startswith("image/"):
                    img_to_send = Image.open(uploaded_file)
                    new_message["image"] = img_to_send
            
            st.session_state.messages.append(new_message)
            st.rerun()

    # AI-ийн хариулт өгөх логик (Хамгийн сүүлийн мессеж хэрэглэгчийнх бол)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                last_msg = st.session_state.messages[-1]
                
                with st.spinner("Thinking..."):
                    if "image" in last_msg:
                        # Зураг + Текст
                        response = model.generate_content([f"Explain this image and answer: {last_msg['content']}", last_msg["image"]])
                    else:
                        # Ой санамжтай чат
                        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat = model.start_chat(history=history)
                        response = chat.send_message(last_msg["content"])
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")

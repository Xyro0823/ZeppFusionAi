import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Page Config
st.set_page_config(page_title="ZeppFusion Ultra", page_icon="⚡", layout="wide")

# 2. Шилдэг апп-уудын дизайныг нэгтгэсэн CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d0e10 !important; color: #ececed !important; }
    
    /* Linear & Claude Style Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111214 !important;
        border-right: 1px solid #272a2d !important;
        width: 300px !important;
    }

    /* Floating Toolbar (ChatGPT Style) */
    .stChatInputContainer {
        padding: 20px 100px !important;
        bottom: 20px !important;
    }
    .stChatInputContainer > div {
        background-color: #1a1b1e !important;
        border: 1px solid #33363a !important;
        border-radius: 16px !important;
        padding-left: 50px !important;
    }

    /* Файл хавсаргах товчны дизайн */
    .stFileUploader {
        position: absolute;
        bottom: 42px;
        left: 115px;
        z-index: 1000;
        width: 45px;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: #272a2d !important;
        border-radius: 50% !important;
        border: none !important;
        padding: 5px !important;
        width: 35px; height: 35px;
    }
    [data-testid="stFileUploaderDropzone"] svg { fill: #a1a1aa !important; }
    div[data-testid="stFileUploaderDropzone"] div { display: none; }

    /* Message Bubbles - Minimalist */
    [data-testid="stChatMessage"] {
        padding: 2rem 5rem !important;
        border-bottom: 1px solid #1f2123 !important;
    }

    /* Shildeg app-uud shig "Gradient" title */
    .ultra-title {
        background: linear-gradient(to right, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 50px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar - Tools & History
with st.sidebar:
    st.markdown("<h2 style='color: white; letter-spacing: -1px;'>⚡ ZeppFusion</h2>", unsafe_allow_html=True)
    
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br><b>⚙️ API CONFIG</b>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your key...", label_visibility="collapsed")
    
    st.markdown("<br><b>🛠️ POWER TOOLS</b>", unsafe_allow_html=True)
    tool_search = st.checkbox("🌐 Web Search (Simulation)", value=True)
    tool_vision = st.checkbox("👁️ Vision Analysis", value=True)
    tool_code = st.checkbox("💻 Code Interpreter", value=True)

    st.markdown("---")
    st.caption("v2.5 Pro - Enterprise Edition")

# 4. Main Chat Interface Logic
if not api_key:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='ultra-title'>ZeppFusion Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8; font-size:18px;'>The ultimate workspace for AI-powered productivity.</p>", unsafe_allow_html=True)
    
    # Feature Showcase
    cols = st.columns(3)
    with cols[0]: st.info("**Analyze** complex files & images.")
    with cols[1]: st.success("**Build** high-quality code instantly.")
    with cols[2]: st.warning("**Write** world-class narratives.")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Чатны түүхийг харуулах
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "⚡"):
            st.markdown(message["content"])
            if "image" in message:
                st.image(message["image"], caption="Attached Content", width=400)

    # --- TOOLS IN THE INPUT BAR ---
    # Чат бичих хэсгийн зүүн талд байрлах файл хавсаргагч
    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

    if prompt := st.chat_input("ZeppFusion-ээс юу ч хамаагүй асуу..."):
        # Хэрэглэгчийн мессежийг хадгалах
        user_msg = {"role": "user", "content": prompt}
        
        if uploaded_file and tool_vision:
            img = Image.open(uploaded_file)
            user_msg["image"] = img
        
        st.session_state.messages.append(user_msg)
        st.rerun()

    # AI Response Engine
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                last_msg = st.session_state.messages[-1]
                
                with st.spinner("Processing with Pro Tools..."):
                    if "image" in last_msg:
                        # VISION TOOL
                        response = model.generate_content([f"System: You are ZeppFusion Pro. Analyzing image and text: {last_msg['content']}", last_msg["image"]])
                    else:
                        # CONTEXTUAL CHAT
                        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                        chat = model.start_chat(history=history)
                        response = chat.send_message(last_msg["content"])
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Tool Error: {e}")

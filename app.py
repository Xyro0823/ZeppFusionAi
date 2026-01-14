import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64

# 1. Page Configuration
st.set_page_config(page_title="ZeppFusion Ultra", page_icon="💎", layout="wide")

# 2. Advanced CSS - Хаана ч байхгүй шилдэг дизайн
st.markdown("""
    <style>
    /* Хөдөлгөөнтэй арын фон (Animated Gradient) */
    .stApp {
        background: radial-gradient(circle at top left, #1e1b4b, #0f172a, #000000);
        color: #f8fafc;
    }

    /* Sidebar-ыг Glassmorphism болгох */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        width: 320px !important;
    }

    /* "New Chat" товчлуурыг Glow эффекттэй болгох */
    div.stButton > button {
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        transition: 0.3s all ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.6);
    }

    /* Чатны талбарын төвлөрөл */
    .main .block-container {
        max-width: 950px !important;
        padding-top: 3rem !important;
    }

    /* Welcome гарчиг - Neon эффект */
    .hero-title {
        font-size: 64px !important;
        font-weight: 800 !important;
        background: linear-gradient(to right, #818cf8, #c084fc, #fb7185);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }

    /* Feature Cards - Шилэн картууд */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 24px;
        text-align: center;
        transition: 0.3s;
    }
    .glass-card:hover {
        background: rgba(255, 255, 255, 0.07);
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-5px);
    }

    /* Prompt Box дизайн */
    .stChatInputContainer {
        border-radius: 20px !important;
        background-color: rgba(30, 41, 59, 0.5) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Implementation
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>💎 ZeppFusion</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋ Start New Journey"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔐 Security & Access")
    api_key = st.text_input("Gemini Pro API Key", type="password", placeholder="Paste your key here...")
    
    st.markdown("### 📷 Vision Intel")
    uploaded_file = st.file_uploader("Drop an image to analyze", type=["jpg", "png", "jpeg"])
    
    st.markdown("<br><br><br>")
    st.markdown("<p style='text-align:center; color:gray; font-size:12px;'>Powered by ZeppFusion Core 2.5</p>", unsafe_allow_html=True)

# 4. Core Logic & UI
if not api_key:
    # Шилдэг Welcome Screen
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>Experience the Future.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:20px; color:#94a3b8;'>ZeppFusion is your next-generation AI companion.</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="glass-card"><h3 style="color:#818cf8">🧠</h3><b>Smart Logic</b><br><p style="color:#64748b; font-size:14px;">Powered by the latest LLM tech.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card"><h3 style="color:#c084fc">⚡</h3><b>Instant Response</b><br><p style="color:#64748b; font-size:14px;">Real-time interaction flow.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-card"><h3 style="color:#fb7185">🛡️</h3><b>Encrypted</b><br><p style="color:#64748b; font-size:14px;">Your data is never stored.</p></div>', unsafe_allow_html=True)

    st.info("👈 Enter your secret API Key in the sidebar to unlock ZeppFusion.")

else:
    # Memory & Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat with custom avatars
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input Box
    if prompt := st.chat_input("Command ZeppFusion..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Chat with history (Memory)
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                with st.spinner("Processing..."):
                    if uploaded_file:
                        img = Image.open(uploaded_file)
                        response = model.generate_content([f"System: You are ZeppFusion. {prompt}", img])
                    else:
                        response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"System Error: {e}")

import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
from io import BytesIO
from fpdf import FPDF

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="ZeppFusion Pro", page_icon="⚡", layout="wide")

# --- 2. ADVANCED CSS (React Styling) ---
st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    .stApp { background-color: #09090b !important; font-family: 'Inter', sans-serif !important; }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(24, 24, 27, 0.9) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px); width: 280px !important;
    }

    /* Custom Toggle Button (React style) */
    [data-testid="collapsedControl"] {
        background-color: #7c3aed !important;
        border-radius: 10px !important;
        padding: 5px !important;
        left: 10px !important;
        top: 10px !important;
    }

    /* Message Bubbles */
    .message-wrapper { display: flex; gap: 16px; padding: 24px; border-radius: 12px; margin-bottom: 8px; }
    .bot-bg { background-color: rgba(255, 255, 255, 0.02); border-top: 1px solid rgba(255,255,255,0.03); }
    .user-bg { background-color: transparent; }

    .avatar { width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 20px; }
    .user-avatar { background: #27272a; border: 1px solid #3f3f46; }
    .bot-avatar { background: linear-gradient(135deg, #7c3aed, #9333ea); box-shadow: 0 8px 20px rgba(124, 58, 237, 0.3); }

    .sender-name { font-size: 14px; font-weight: 500; margin-bottom: 4px; }
    .user-text { color: #d4d4d8; }
    .bot-text { color: #a78bfa; }

    /* Code Blocks */
    pre { background: #18181b !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; padding: 16px !important; }
    code { color: #c4b5fd !important; background: rgba(124, 58, 237, 0.1) !important; padding: 2px 5px !important; border-radius: 4px !important; }

    /* New Chat Button */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #7c3aed, #9333ea) !important;
        color: white !important; border: none !important; border-radius: 12px !important; height: 45px !important;
        font-weight: 500 !important; width: 100% !important;
    }
    
    /* Input Box */
    .stChatInputContainer { background: transparent !important; padding: 20px 8% !important; }
    .stChatInputContainer > div { background: #18181b !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXPORT LOGIC ---
def get_pdf_bytes(messages):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "ZeppFusion Chat Export", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(10)
    for m in messages:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 7, f"{'You' if m['role']=='user' else 'ZeppFusion'}:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, m['content'].encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SIDEBAR IMPLEMENTATION ---
with st.sidebar:
    # Header
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <img src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/69456a8a7026ba13461ef577/a8ac75228_Gemini_Generated_Image_c9qxrc9qxrc9qxrc1.png" width="50">
            <div><h2 style="color:white; margin:0; font-size:20px;">ZeppFusion</h2><p style="color:#71717a; font-size:11px; margin:0;">Intelligent Workspace</p></div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("＋ New Chat Session"):
        st.session_state.messages = []
        st.rerun()

    # Search (UI only)
    st.text_input("", placeholder="Search chats...", label_visibility="collapsed")

    # History Groups
    st.markdown("<p style='color:#71717a; font-size:10px; font-weight:600; margin-top:20px;'>TODAY</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#d4d4d8; font-size:13px; cursor:pointer;'>• React & Streamlit Integration</p>", unsafe_allow_html=True)

    # Export Section
    st.markdown("---")
    st.markdown("### 📥 Export")
    if st.session_state.get("messages"):
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("TXT", " ".join([m['content'] for m in st.session_state.messages]), "chat.txt", use_container_width=True)
        with col2:
            pdf_data = get_pdf_bytes(st.session_state.messages)
            st.download_button("PDF", pdf_data, "chat.pdf", use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password")

# --- 5. CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Welcome message if empty
if not st.session_state.messages:
    st.markdown("<div style='text-align:center; margin-top:15vh;'><h1 style='color:white; font-size:48px; font-weight:800; opacity:0.9;'>How can I assist you?</h1><p style='color:#71717a;'>Your intelligent AI partner for coding and analysis.</p></div>", unsafe_allow_html=True)

# Display Messages
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    st.markdown(f"""
        <div class="message-wrapper {'user-bg' if is_user else 'bot-bg'}">
            <div class="avatar {'user-avatar' if is_user else 'bot-avatar'}">{'👤' if is_user else '✨'}</div>
            <div class="content-area">
                <div class="sender-name {'user-text' if is_user else 'bot-text'}">{'You' if is_user else 'ZeppFusion'}</div>
                <div class="message-body">{msg['content']}</div>
                <div style="display:flex; gap:10px; margin-top:12px;">
                    <div style="font-size:10px; color:#52525b; border:1px solid #27272a; padding:2px 8px; border-radius:5px;">⏱ Expires in 7 days</div>
                    <div style="font-size:10px; color:#3f3f46;">{msg['time']}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. CHAT INPUT & AI LOGIC ---
if prompt := st.chat_input("Message ZeppFusion..."):
    time_now = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "user", "content": prompt, "time": time_now})
    
    if not api_key:
        st.error("Please provide an API Key in the sidebar.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response.text, 
                "time": datetime.now().strftime("%I:%M %p")
            })
            st.rerun()
        except Exception as e:
            st.error(f"AI Error: {e}")


import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ChatGPT",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (CHATGPT STYLE) ---
st.markdown("""
<style>
    /* Import Söhne Font Alternative */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main App Background - ChatGPT Light Gray */
    .stApp {
        background-color: #f7f7f8;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar Styling - ChatGPT Dark Sidebar */
    [data-testid="stSidebar"] {
        background-color: #171717;
        border-right: none;
    }
    
    [data-testid="stSidebar"] * {
        color: #ececec !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1 {
        color: #ececec;
        font-size: 16px;
        font-weight: 600;
        padding: 20px 16px 10px 16px;
    }
    
    [data-testid="stSidebar"] button {
        background-color: transparent !important;
        border: 1px solid #565869 !important;
        color: #ececec !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: background-color 0.2s !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #2a2b32 !important;
    }
    
    /* Container Padding */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 10rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 48rem;
        margin: 0 auto;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background-color: transparent !important;
        padding: 1.5rem 0 !important;
        border: none !important;
    }
    
    /* User Message Background */
    [data-testid="stChatMessage-user"] {
        background-color: #f7f7f8 !important;
    }
    
    /* Assistant Message Background - Alternating */
    [data-testid="stChatMessage-assistant"] {
        background-color: #ffffff !important;
    }
    
    /* Message Content */
    [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        border: none !important;
        color: #2e3338 !important;
        padding: 0 !important;
        font-size: 16px !important;
        line-height: 1.7 !important;
    }
    
    /* Avatar Styling - ChatGPT Style */
    .stChatMessage [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, #19c37d 0%, #0fa37f 100%) !important;
        border-radius: 4px !important;
    }
    
    .stChatMessage [data-testid="chatAvatarIcon-assistant"] {
        background-color: #19c37d !important;
        border-radius: 4px !important;
    }
    
    /* Chat Input Container - Fixed Bottom */
    .stChatInputContainer {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: linear-gradient(180deg, rgba(247,247,248,0) 0%, rgba(247,247,248,1) 20%) !important;
        padding: 20px !important;
        padding-bottom: 40px !important;
        border: none !important;
        z-index: 999 !important;
    }
    
    /* Chat Input Field - ChatGPT Style */
    .stChatInput {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        color: #2e3338 !important;
        max-width: 48rem !important;
        margin: 0 auto !important;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.1) !important;
    }
    
    .stChatInput input {
        background-color: transparent !important;
        color: #2e3338 !important;
        border: none !important;
        font-size: 16px !important;
        padding: 12px 16px !important;
    }
    
    .stChatInput input::placeholder {
        color: #8e8ea0 !important;
    }
    
    .stChatInput:focus-within {
        border-color: #19c37d !important;
        box-shadow: 0 0 0 2px rgba(25, 195, 125, 0.2) !important;
    }
    
    /* File Uploader - Hidden but functional */
    [data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 8px !important;
    }
    
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
        border: none !important;
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        color: #2e3338 !important;
        font-size: 14px !important;
        padding: 8px 16px !important;
        transition: all 0.2s !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background-color: #f7f7f8 !important;
        border-color: #19c37d !important;
    }
    
    /* Spinner - ChatGPT Green */
    .stSpinner > div {
        border-top-color: #19c37d !important;
    }
    
    /* Error Messages - ChatGPT Style */
    .stAlert {
        background-color: #fee !important;
        color: #d00 !important;
        border: 1px solid #fcc !important;
        border-radius: 8px !important;
    }
    
    /* Success Messages */
    .stSuccess {
        background-color: #d4f4dd !important;
        color: #0d5028 !important;
        border: 1px solid #b7e4c7 !important;
        border-radius: 8px !important;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d1d5db;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #9ca3af;
    }
    
    /* Code Blocks - ChatGPT Style */
    code {
        background-color: #f3f4f6 !important;
        color: #1f2937 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-size: 14px !important;
    }
    
    pre {
        background-color: #000000 !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }
    
    pre code {
        background-color: transparent !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE FUNCTIONS ---
def init_db():
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  role TEXT, 
                  content TEXT, 
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_message(username, role, content):
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages(username, role, content, timestamp) VALUES (?,?,?,?)',
              (username, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_chat_history(username):
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages WHERE username=? ORDER BY id ASC', (username,))
    history = c.fetchall()
    conn.close()
    return history

def clear_chat_history(username):
    conn = sqlite3.connect('zepp_fusion.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE username=?', (username,))
    conn.commit()
    conn.close()

# --- INITIALIZE ---
init_db()

# Initialize session state
if "username" not in st.session_state:
    st.session_state.username = "User"

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("# 💬 ChatGPT")
    st.markdown("")
    
    if st.button("➕ New chat", use_container_width=True):
        clear_chat_history(st.session_state.username)
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📜 Recent Chats")
    st.markdown("*Chat history appears here*")
    
    st.markdown("---")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    
    st.markdown("**Powered by Gemini 2.5 Flash**")
    st.caption("UI styled like ChatGPT")

# --- MAIN CHAT AREA ---
# Display chat history
db_history = get_chat_history(st.session_state.username)

if not db_history:
    # Welcome message when no chat history
    st.markdown("""
    <div style='text-align: center; padding: 60px 20px;'>
        <h1 style='color: #2e3338; font-size: 32px; font-weight: 600; margin-bottom: 40px;'>
            How can I help you today?
        </h1>
    </div>
    """, unsafe_allow_html=True)

for role, content in db_history:
    with st.chat_message(role):
        st.markdown(content)

# --- FILE UPLOAD (Optional) ---
with st.expander("📎 Upload Image/PDF (optional)"):
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=['png', 'jpg', 'jpeg', 'pdf'],
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.session_state.uploaded_image = uploaded_file
        st.success(f"✓ Uploaded: {uploaded_file.name}")

# --- CHAT INPUT ---
prompt = st.chat_input("Message ChatGPT...")

# --- HANDLE USER INPUT ---
if prompt:
    # Display user message
    with st.chat_message("user"):
        if st.session_state.uploaded_image:
            st.image(st.session_state.uploaded_image, width=300)
        st.markdown(prompt)
    
    # Save user message
    save_message(st.session_state.username, "user", prompt)
    
    try:
        # Configure Gemini API
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Use Gemini 2.5 Flash
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Prepare chat history
        gemini_history = []
        for role, content in db_history:
            gemini_role = "model" if role == "assistant" else "user"
            gemini_history.append({"role": gemini_role, "parts": [content]})
        
        # Generate response
        with st.spinner(""):
            if st.session_state.uploaded_image:
                # Handle image input
                img = Image.open(st.session_state.uploaded_image)
                response = model.generate_content([prompt, img])
                st.session_state.uploaded_image = None  # Clear after use
            else:
                # Text-only chat
                chat = model.start_chat(history=gemini_history)
                response = chat.send_message(prompt)
        
        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Save AI response
        save_message(st.session_state.username, "assistant", response.text)
        
        # Rerun to update chat
        st.rerun()
        
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        st.info("💡 Please check your API key or try again.")

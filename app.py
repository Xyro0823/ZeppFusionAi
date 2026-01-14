import streamlit as st
import google.generativeai as genai

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="ZeppFusion",
    page_icon="⚡",
    layout="wide"
)

# ===============================
# CSS (ChatGPT-style Minimal Dark)
# ===============================
st.markdown("""
<style>
:root {
  --bg: #0b0b0d;
  --panel: #111113;
  --border: #1f1f23;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --accent: #6366f1;
}

/* App */
.stApp {
  background: var(--bg);
  color: var(--text);
  font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--bg);
  border-right: 1px solid var(--border);
}

/* Sidebar buttons */
.stSidebar button {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  color: var(--text);
}
.stSidebar button:hover {
  background: #18181b;
}

/* Chat messages */
[data-testid="stChatMessage"] {
  background: transparent;
  padding-left: 0;
  padding-right: 0;
}

[data-testid="stChatMessageContent"] {
  font-size: 15px;
  line-height: 1.65;
  max-width: 720px;
}

/* Assistant subtle bg */
[data-testid="stChatMessage"][aria-label="assistant"] {
  background: linear-gradient(180deg, rgba(99,102,241,0.03), transparent);
}

/* Chat input */
.stChatInputContainer {
  padding: 16px 18%;
  background: linear-gradient(to top, var(--bg) 60%, transparent);
}

.stChatInputContainer > div {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 999px;
  height: 52px;
}

[data-testid="stChatInputSubmit"] {
  background: var(--accent);
  border-radius: 50%;
}

/* Welcome */
.welcome {
  text-align: center;
  margin-top: 120px;
}
.welcome h1 {
  font-size: 44px;
  font-weight: 700;
  letter-spacing: -1px;
}
.welcome p {
  color: var(--muted);
  font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown("## ⚡ ZeppFusion")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔑 Gemini API Key")
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="AIza..."
    )

    st.markdown("---")
    st.markdown("""
    <div style="position:fixed; bottom:20px; left:20px; right:20px;
    background:#111113; border:1px solid #1f1f23;
    border-radius:14px; padding:12px; display:flex; gap:10px;">
      <div style="width:32px;height:32px;border-radius:50%;
      background:linear-gradient(45deg,#6366f1,#a855f7);
      display:flex;align-items:center;justify-content:center;font-weight:600;">U</div>
      <div>
        <div style="font-size:13px;">User</div>
        <div style="font-size:11px;color:#9ca3af;">Personal</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# SESSION STATE
# ===============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===============================
# WELCOME SCREEN
# ===============================
if not st.session_state.messages:
    st.markdown("""
    <div c

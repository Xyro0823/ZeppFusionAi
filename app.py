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
# CSS
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

.stApp {
  background: var(--bg);
  color: var(--text);
  font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
}

section[data-testid="stSidebar"] {
  background: var(--bg);
  border-right: 1px solid var(--border);
}

.stSidebar button {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  color: var(--text);
}

.stSidebar button:hover {
  background: #18181b;
}

[data-testid="stChatMessageContent"] {
  font-size: 15px;
  line-height: 1.65;
  max-width: 720px;
}

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

.welcome {
  text-align: center;
  margin-top: 120px;
}

.welcome h1 {
  font-size: 44px;
  font-weight: 700;
}

.welcome p {
  color: var(--muted);
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

# ===============================
# SESSION STATE
# ===============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===============================
# WELCOME
# ===============================
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <h1>What can I help you build?</h1>
        <p>ZeppFusion AI is ready.</p>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# CHAT HISTORY
# ===============================
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "⚡"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ===============================
# CHAT INPUT
# ===============================
prompt = st.chat_input("Ask anything...")

if prompt:
    if not api_key:
        st.warning("Sidebar дээр Gemini API key оруулна уу.")
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("assistant", avatar="⚡"):
            try:
                genai.configure(api_key=api_key)

                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash",
                    system_instruction=(
                        "Чи ZeppFusion нэртэй Монгол хэлний AI. "
                        "Монгол хэлээр товч, ойлгомжтой хариул."
                    )
                )

                history = []
                for m in st.session_state.messages[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({
                        "role": role,
                        "parts": [m["content"]]
                    })

                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)

                st.markdown(response.text)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.text
                })

            except Exception as e:
                st.error(f"Алдаа: {e}")

        st.rerun()

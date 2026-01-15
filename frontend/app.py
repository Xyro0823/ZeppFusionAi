import streamlit as st
import requests
import jwt

BACKEND = "https://YOUR-BACKEND.onrender.com"
JWT_SECRET = "supersecret"  # зөвхөн decode-д (optional)

st.set_page_config(page_title="ZeppFusion", page_icon="⚡")

# ===== TOKEN BARих =====
if "token" not in st.session_state:
    params = st.query_params
    if "token" in params:
        st.session_state.token = params["token"]
        st.query_params.clear()
        st.rerun()

# ===== LOGIN UI =====
if "token" not in st.session_state:
    st.markdown("## ⚡ ZeppFusion")
    st.markdown(
        f"<a href='{BACKEND}/login'>Google-ээр нэвтрэх</a>",
        unsafe_allow_html=True
    )
    st.stop()

# ===== USER INFO =====
payload = jwt.decode(
    st.session_state.token,
    JWT_SECRET,
    algorithms=["HS256"],
    options={"verify_signature": False}
)

st.sidebar.write(payload["name"])
st.sidebar.caption(payload["email"])

# ===== CHAT =====
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Message ZeppFusion..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        r = requests.post(
            f"{BACKEND}/chat",
            json={"message": prompt},
            params={"token": st.session_state.token}
        ).json()
        st.write(r["reply"])
        st.session_state.messages.append(
            {"role": "assistant", "content": r["reply"]}
        )

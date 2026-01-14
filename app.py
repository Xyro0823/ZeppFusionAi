import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(page_title="ZeppFusion VOXA", page_icon="⚡", layout="wide")

# 2. VOXA Inspired CSS (Нарийвчилсан загварчлал)
st.markdown("""
    <style>
    /* Үндсэн Background */
    .stApp {
        background-color: #17181c !important; /* Гүн бараан дэвсгэр */
        color: #e0e0e0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar - VOXA-ийн цэс */
    section[data-testid="stSidebar"] {
        background-color: #0d0e10 !important; /* Sidebar-ийн илүү бараан өнгө */
        border-right: 1px solid #282a2e !important;
        width: 300px !important;
    }

    /* Sidebar-ийн лого */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 20px 0 30px 20px;
    }

    /* Search Input (Sidebar дотор) */
    .stTextInput label { display: none; } /* Search-ийн label-ийг нуух */
    .stTextInput div[data-baseweb="input"] {
        background-color: #1f2024 !important;
        border: 1px solid #33363b !important;
        border-radius: 8px !important;
        padding: 5px 10px !important;
        margin-bottom: 20px;
    }
    .stTextInput input {
        color: #e0e0e0 !important;
    }
    .stTextInput .st-cf { /* Search icon */
        margin-right: 5px;
        color: #888;
    }

    /* Sidebar-ийн навигацийн товчлуурууд */
    div[data-testid="stSidebarNav"] li {
        margin-bottom: 5px;
    }
    div[data-testid="stSidebarNav"] li a {
        background-color: transparent !important;
        color: #a0a2a8 !important;
        font-weight: 500;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stSidebarNav"] li a:hover {
        background-color: #1f2024 !important;
        color: #e0e0e0 !important;
    }
    div[data-testid="stSidebarNav"] li a.current-page { /* Сонгогдсон хуудас */
        background-color: #282a2e !important;
        color: #e0e0e0 !important;
    }

    /* Main Chat Area - Төвлөрөл */
    .main .block-container {
        max-width: 900px !important;
        padding-top: 2rem !important;
        padding-bottom: 10rem !important;
    }

    /* Чатны хөөсөнцөр (Chat Bubbles) */
    [data-testid="stChatMessage"] {
        background-color: #2

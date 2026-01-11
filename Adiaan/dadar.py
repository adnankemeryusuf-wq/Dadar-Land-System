import streamlit as st
import os
import requests
import qrcode
import openpyxl
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- QINDAA'INA (CONFIG) ---
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8586015354:AAEliISf-RtoeJ8anbVLapY3NBm7hz8dZWI"
CHAT_ID_MANAGER = "568248052"
DATA_FILE = "dadar_final_report.txt"

# --- LOGO BARBAADU ---
# Maqaa faayila keetii lamaan iyyuu ni barbaada
logo_options = ["Adiaan/logo.png", "Adiaan/logo.png.png", "logo.png"]
LOGO_PATH = None
for path in logo_options:
    if os.path.exists(path):
        LOGO_PATH = path
        break

# --- WEB UI CONFIG ---
st.set_page_config(page_title="Dadar Land System", page_icon=LOGO_PATH if LOGO_PATH else "🏢")

# --- LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    if LOGO_PATH:
        st.image(LOGO_PATH, width=150)
    st.title("W/Bulchiinsa Lafaa Magaalaa Dadar")
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Login Dogoggora!")
else:
    # Sidebar Logo
    if LOGO_PATH:
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    
    menu = ["Galmee Haaraa", "Gabaasa Excel (Telegram)", "Logout"]
    choice = st.sidebar.selectbox("Filannoo", menu)

    # Header Logo
    col1, col2 = st.columns([1, 5])
    with col1:
        if LOGO_PATH:
            st.image(LOGO_PATH, width=80)
    with col2:
        st.title("W/Bulchiinsa Lafaa Magaalaa Dadar")

    if choice == "Galmee Haaraa":
        st.subheader("📝 Galmee Haaraa Galchi")
        # ... (koodii galmee kee itti fufa)

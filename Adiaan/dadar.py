import streamlit as st
import os
import requests
import qrcode
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
logo_options = ["Adiaan/logo.png", "Adiaan/logo.png.png", "logo.png", "logo.png.png"]
LOGO_PATH = next((p for p in logo_options if os.path.exists(p)), None)

# --- WEB UI CONFIG ---
st.set_page_config(
    page_title="Dadar Land Administration", 
    page_icon=LOGO_PATH if LOGO_PATH else "🏢",
    layout="wide"
)

# --- CUSTOM CSS (Style Login fi Header) ---
st.markdown("""
    <style>
    /* Bakka Login gidduu qabachiisuuf */
    .login-box {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 50px;
    }
    .stButton>button {
        width: 100%;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        height: 3em;
        border-radius: 8px;
    }
    .main { background-color: #f0f2f5; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Fuula Login Gidduu Qabachiisuu
    _, col2, _ = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if LOGO_PATH:
            st.image(LOGO_PATH, width=150)
        
        st.markdown("<h2 style='color: #1f4e78;'>Dadar Land System Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6c757d;'>Maaloo ragaa kee galchi</p>", unsafe_allow_html=True)
        
        with st.form("Login"):
            u = st.text_input("Username", placeholder="Username kee galchi")
            p = st.text_input("Password", type="password", placeholder="Password kee galchi")
            
            submit = st.form_submit_button("SEENI (LOGIN)")
            
            if submit:
                if u == USER_NAME and p == PASS_WORD:
                    st.session_state.logged_in = True
                    st.success("Milkiin seenteetta!")
                    st.rerun()
                else:
                    st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- DASHBOARD (ERGA SEENTEE BOODA) ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.title("Main Menu")
        choice = st.radio("Filannoo:", ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa", "🚪 Logout"])

    # Header Gidduutti
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if LOGO_PATH: st.image(LOGO_PATH, width=100)
    st.markdown("<h1 style='color: #1f4e78;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("---")

    if choice == "🏠 Dashboard":
        st.subheader("Baga Nagaan Dhufte!")
        # Dashboard ragaa asitti itti fufa...
        
    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

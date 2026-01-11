import streamlit as st
import os
import requests
import qrcode
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- 1. CONFIG ---
st.set_page_config(
    page_title="Dadar Land Administration System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATA CONFIG ---
USER_NAME = "admin"; PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = next((p for p in ["Adiaan/logo.png", "logo.png"] if os.path.exists(p)), None)

# --- 2. CUSTOM CSS (LOGO FI HEADER BAREEDSUUF) ---
st.markdown("""
    <style>
    /* Header Box - Logo fi Barreeffama gidduu qabachiisuuf */
    .header-style {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #ffffff 0%, #f0f2f5 100%);
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        border-bottom: 4px solid #007bff;
    }
    .main-title {
        color: #1f4e78;
        font-size: 38px !important;
        font-weight: 800;
        margin-top: 15px;
        margin-bottom: 5px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .sub-title {
        color: #555;
        font-size: 20px;
        font-weight: 400;
    }
    /* PC Login Box */
    .login-card {
        background: white;
        padding: 50px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN PAGE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=150)
        st.markdown("<h2 style='color: #1f4e78;'>Dadar Land System</h2>", unsafe_allow_html=True)
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("LOG IN"):
                if u == USER_NAME and p == PASS_WORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 4. MAIN DASHBOARD ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.markdown("---")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa Excel", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)

    # --- CENTERED LOGO & TEXT (Gama Gubbaa) ---
    st.markdown('<div class="header-style">', unsafe_allow_html=True)
    if LOGO_PATH:
        # Logo gidduu qabachiisuu
        st.image(LOGO_PATH, width=130)
    st.markdown("""
        <div class="main-title">Waajjira Lafaa Bulchiinsa Magaalaa Dadar</div>
        <div class="sub-title">Customer Registration & Management System</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 5. DASHBOARD CONTENT ---
    if choice == "🏠 Dashboard":
        # Metrics PC irratti
        m1, m2, m3 = st.columns(3)
        m1.metric("Today's Customers", "24", delta="12%")
        m2.metric("Total Revenue", "15,400 ETB", delta="800")
        m3.metric("System Status", "Connected ✅")
        
        st.write("### 🕒 Recent Entries")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("No data yet.")

    elif choice == "📝 Galmee Haaraa":
        # Form-ichi itti fufa...
        st.subheader("Add New Customer")
        with st.form("Entry"):
            c1, c2 = st.columns(2)
            c1.text_input("Customer Name")
            c2.text_input("Phone Number")
            if st.form_submit_button("Register"):
                st.success("Registered!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

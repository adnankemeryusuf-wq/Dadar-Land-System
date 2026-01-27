import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# --- CSS: Fuula hunda qulqullu gochuuf ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    div.stButton > button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE LOGIC =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)

df = load_data()

# ================= 3. SIDEBAR (WANTOOTA HUNDA ASITTI DHOKSI) =================
with st.sidebar:
    st.title("🗂 Menu")
    menu = st.radio("Hojii Filadhu:", ["📊 Dashboard", "📝 Galmee", "📈 Gabaasa", "🏆 Badhaasa"])
    st.divider()
    st.info("Systemii Bulchiinsa Lafaa Dadar v2.0")

# ================= 4. MAIN AREA (BAKKA MUL'ATU) =================

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.subheader("📊 Haala Waliigalaa")
    # Expander keessatti dhoksuu
    with st.expander("📈 Maandhee Galii Ilaali", expanded=True):
        c1, c2 = st.columns(2)
        c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Baay'ina Galmee", len(df))

# --- GALMEE HAARAA ---
elif menu == "📝 Galmee":
    st.subheader("📝 Galmee Haaraa")
    # Form keessatti dhoksuu
    with st.expander("➕ Formii Galmee Bani"):
        with st.form("my_form", clear_on_submit=True):
            name = st.text_input("Maqaa Abbaa Dhimmaa")
            area = st.text_input("Araddaa")
            service = st.multiselect("Tajaajila", ["Gibira", "Liizii", "Kaartaa"])
            fee = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                st.success("Galmeen kuufameera!")

# --- GABAASA (EXCEL & TELEGRAM) ---
elif menu == "📈 Gabaasa":
    st.subheader("📈 Gabaasa Bal'aa")
    # Wantoota baay'ee expander keessa kaayyuu
    with st.expander("📅 Gabaasa Kurmaanaatti Jijjiiri"):
        st.write("Kurmaana 1ffaa - 4ffaa asitti addaan ba'ee jira.")
        st.dataframe(df)
        
    with st.expander("🚀 Gabaasa Excel Gara Telegram-itti Ergi"):
        if st.button("Ergi"):
            st.info("Gabaasni Formata qaxaxee qabateen ergamaa jira...")

# --- BADHAASA ---
elif menu == "🏆 Badhaasa":
    st.subheader("🏆 Badhaasa Ogeeyyii")
    with st.expander("🎖 Sartifiikeeta Ogeeyyii Top 3"):
        st.write("Ogeeyyii qaxaree filataman asitti mul'atu.")
        # Bakka Logo itti fe'an (dhokfamee jira)
        l1 = st.file_uploader("Logo Bitaa", key="l1")
        l2 = st.file_uploader("Logo Mirgaa", key="l2")

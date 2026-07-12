import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIG & DATA =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

# ================= 2. AUTH =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Username ykn Password sirrii miti!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        menu = st.radio("Filannoo", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🚪 Logout"])

    # ================= 3. APP LOGIC (Sirreessaa kana) =================
    if menu == "📊 Dashboard":
        st.title("Dadar Land Analytics")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Tajaajilamtoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Tajaajilaa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        # [Harka kee irraa GATII_DICT asitti dabali]
        GATII_DICT = {"🏷 Gibira": ["Gibira Baaxii", "TOT"], "📂 Biroo": ["Clearance"]}
        sel_main = st.multiselect("Ramaddii Tajaajilaa", list(GATII_DICT.keys()))
        
        # Form keessa kaayi
        with st.form("main_form"):
            c1, c2 = st.columns(2)
            name_f = c1.text_input("Maqaa Maamilaa")
            ogeessa = c2.text_input("Ogeessa")
            total_sum = st.number_input("Kafaltii", min_value=0.0)
            
            if st.form_submit_button("💾 GALMEESSI"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), name_f, "Araddaa", "Qaxana", "Tajaajila", ogeessa, total_sum]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success("Galmeeffameera!")

    elif menu == "📈 Gabaasa Galii":
        st.title("📈 Gabaasa Waliigalaa")
        st.dataframe(df, use_container_width=True)

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

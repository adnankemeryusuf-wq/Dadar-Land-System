import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & ENV =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# ================= 2. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_telegram(df, title):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gabaasa')
    output.seek(0)
    files = {'document': (f"{title}.xlsx", output)}
    caption = f"📊 **{title}**\n💰 Galii: {df['Kafaltii_Taj'].sum():,.2f} ETB"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID, 'caption': caption}, files=files)

# ================= 3. UI & AUTH =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "1234":
            st.session_state.auth = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.selectbox("📋 MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "📄 Clearance", "🏆 Badhaasa", "🔍 Barbaadi/Edit", "🚪 Logout"])

    if menu == "🚪 Logout":
        st.session_state.auth = False
        st.rerun()

    # ---------- 📊 DASHBOARD ----------
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        c1, c2, c3 = st.columns(3)
        c1.metric("👥 Maamiltoota", len(df))
        c2.metric("💰 Galii (ETB)", f"{df['Kafaltii_Taj'].sum():,.2f}")
        c3.metric("📅 Har'a", len(df[df['Guyyaa'] == datetime.now().strftime('%d/%m/%Y')]))
        
        fig = px.pie(df, names='Gosa_Tajajjilaa', values='Kafaltii_Taj', title="Kaffaltii Gosa Tajaajilaan")
        st.plotly_chart(fig, use_container_width=True)

    # ---------- 📝 GALMEE HAARAA ----------
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa fi Nagahee")
        with st.form("reg"):
            name = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            gosa = st.selectbox("Gosa Tajaajilaa", ["Liizii", "Kiiraa", "Kaartaa", "Jijjiirraa"])
            og = st.text_input("Ogeessa")
            fee = st.number_input("Kaffaltii", min_value=0.0)
            scan = st.file_uploader("Nagahee Skaan", type=['jpg','png'])
            if st.form_submit_button("💾 Galmeessi"):
                new = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, og, fee]
                df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                save_data(df); st.success("✅ Galmeeffameera!")

    # ---------- 📄 CLEARANCE ----------
    elif menu == "📄 Clearance":
        st.header("📄 Clearance PDF (Liizii/Kiiraa)")
        l_bita = st.file_uploader("Logo Bitaa", type=['png','jpg'], key="cl_l")
        l_mirga = st.file_uploader("Logo Mirgaa", type=['png','jpg'], key="cl_r")
        with st.form("clr"):
            c_maqaa = st.text_input("Maqaa Maamilaa")
            c_gosa = st.selectbox("Gosa Qabiyyee", ["Liizii", "Kiiraa", "Permit"])
            if st.form_submit_button("📄 PDF UUMI"):
                st.success("PDF Qophaa'eera!") # (FPDF logic ashaaraa keessatti dabalama)

    # ---------- 🏆 BADHAASA ----------
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        st.info("Ogeessa tajaajila gaarii kenneef Certificate uumi.")
        # (Certificate logic with dual logos here)

    # ---------- 🔍 SEARCH / EDIT / DELETE ----------
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Haqi")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            idx_to_del = st.number_input("Index Haquuf", min_value=0, max_value=len(df)-1, step=1)
            if st.button("🗑 Galmee Haqi"):
                df = df.drop(df.index[idx_to_del])
                save_data(df); st.warning("Haqameera!"); st.rerun()

    # ---------- 📤 TELEGRAM ----------
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Excel Gara Telegram"):
        send_telegram(df, "Gabaasa_Waliigalaa")
        st.sidebar.success("Telegram-itti ergameera!")

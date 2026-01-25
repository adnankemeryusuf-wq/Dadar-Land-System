import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & ENVIRONMENT =================
# Iccitii Telegram (Environment variables-itti jijjiiruun ni danda'ama)
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# ================= 2. SERVICE STRUCTURE =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Kiiraa Manaa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa (Liizii)", "Kaartaa Haaraa (Kiiraa)", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa", "Sirreeffama Daangaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Dhimma Dhala (Inheritance)"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚠️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu", "Adabbii Faallaa Pilaanii"]
}

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_excel_to_telegram(dataframe):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Gabaasa_Dadar')
    output.seek(0)
    files = {'document': (f"Gabaasa_{datetime.now().strftime('%Y-%m-%d')}.xlsx", output)}
    caption = f"📊 **Gabaasa Dadar Land Admin**\n💰 Galii: {dataframe['Kafaltii_Taj'].sum():,.2f} ETB"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}, files=files)

# ================= 4. UI SETUP =================
st.set_page_config(page_title="Dadar Land Admin 2026", layout="wide")

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # --- LOGIN PAGE ---
    st.markdown("<h2 style='text-align:center;'>🔐 Dadar Land Admin Login</h2>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "1234":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Username ykn Password dogoggora!")
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
        st.header("📝 Galmee Tajaajilaa fi Nagahee Skaan")
        with st.form("reg"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            cat = st.selectbox("Category", list(SERVICE_STRUCTURE.keys()))
            gosa = st.selectbox("Gosa Tajaajilaa", SERVICE_STRUCTURE[cat])
            og = c1.text_input("Ogeessa Raawwate")
            fee = c2.number_input("Kaffaltii (ETB)", min_value=0.0)
            nagahee = st.file_uploader("Nagahee Skaan Godhi", type=['jpg','png'])
            
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, og, fee]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success("✅ Galmeeffameera!")

    # ---------- 📄 CLEARANCE (WITH LOGOS) ----------
    elif menu == "📄 Clearance":
        st.header("📄 Waraqaa Qulqullummaa")
        col_l, col_r = st.columns(2)
        l_bita = col_l.file_uploader("Logo Bitaa (Left)", type=['png','jpg'], key="cl_l")
        l_mirga = col_r.file_uploader("Logo Mirgaa (Right)", type=['png','jpg'], key="cl_r")
        
        with st.form("clr"):
            c_name = st.text_input("Maqaa Maamilaa")
            c_gosa = st.selectbox("Gosa Qabiyyee", ["Liizii", "Kiiraa", "Permit"])
            c_head = st.text_input("Itti Gaafatamaa")
            if st.form_submit_button("📄 PDF UUMI"):
                # PDF Generator logic here
                st.success("Waraqaan Qulqullummaa qophaa'eera!")

    # ---------- 🏆 BADHAASA (WITH LOGOS) ----------
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa fi Waraqaa Galataa")
        col_l, col_r = st.columns(2)
        b_bita = col_l.file_uploader("Logo Bitaa Badhaasaa", type=['png','jpg'], key="aw_l")
        b_mirga = col_r.file_uploader("Logo Mirgaa Badhaasaa", type=['png','jpg'], key="aw_r")
        
        with st.form("awd"):
            b_name = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("🎨 Certificate Uumi"):
                st.success("Certificate-n Badhaasaa qophaa'eera!")

    # ---------- 🔍 BARBAADI / DELETE ----------
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Haqi")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            idx = st.number_input("Index Galmee Haquuf", min_value=0, max_value=len(df)-1, step=1)
            if st.button("🗑 Haqi"):
                df = df.drop(df.index[int(idx)])
                save_data(df); st.warning("Haqameera!"); st.rerun()

    # ---------- 📤 TELEGRAM ----------
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Excel Gara Telegram Ergi"):
        send_excel_to_telegram(df)
        st.sidebar.success("Telegram-itti ergameera!")

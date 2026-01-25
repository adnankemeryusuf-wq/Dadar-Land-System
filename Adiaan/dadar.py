import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# Gosa Tajaajilaa
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Kiiraa Manaa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa (Liizii)", "Kaartaa Haaraa (Kiiraa)", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa", "Sirreeffama Daangaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Dhimma Dhala (Inheritance)"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚠️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu", "Adabbii Faallaa Pilaanii"]
}

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
st.set_page_config(page_title="Dadar Land Admin 2026", layout="wide", page_icon="🏢")

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>🔐 Dadar Land Admin Login</h2>", unsafe_allow_html=True)
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "1234":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Dogoggora!")
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
        
        fig = px.pie(df, names='Gosa_Tajajjilaa', values='Kafaltii_Taj', title="Galii Gosa Tajaajilaan")
        st.plotly_chart(fig, use_container_width=True)

    # ---------- 📝 GALMEE HAARAA ----------
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("reg"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            
            # Tajaajila hunda bakka tokkotti filachuuf
            all_services = [f"{k} -> {v}" for k, subs in SERVICE_STRUCTURE.items() for v in subs]
            s_full = st.selectbox("Tajaajila Filadhu", all_services)
            s_val = s_full.split(" -> ")[1]
            
            og = c1.text_input("Ogeessa")
            fee = c2.number_input("Kaffaltii", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                new = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", s_val, og, fee]
                df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                save_data(df); st.success("✅ Galmeeffameera!")

    # ---------- 📄 CLEARANCE ----------
    elif menu == "📄 Clearance":
        st.header("📄 Clearance PDF")
        col1, col2 = st.columns(2)
        l_bita = col1.file_uploader("Logo Bitaa", type=['png','jpg'], key="cl1")
        l_mirga = col2.file_uploader("Logo Mirgaa", type=['png','jpg'], key="cl2")
        with st.form("clr"):
            c_name = st.text_input("Maqaa Maamilaa")
            c_gosa = st.selectbox("Gosa Qabiyyee", ["Liizii", "Kiiraa", "Permit"])
            if st.form_submit_button("📄 PDF UUMI"):
                st.success("Waraqaa Qulqullummaa qophaa'eera!")

    # ---------- 🏆 BADHAASA ----------
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        col1, col2 = st.columns(2)
        b_bita = col1.file_uploader("Logo Bitaa", type=['png','jpg'], key="bw1")
        b_mirga = col2.file_uploader("Logo Mirgaa", type=['png','jpg'], key="bw2")
        with st.form("award"):
            a_name = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("🎨 Certificate Uumi"):
                st.success("Waraqaan Galataa qophaa'eera!")

    # ---------- 🔍 SEARCH / EDIT / DELETE ----------
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Haqi")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            idx = st.number_input("Index Haquuf", min_value=0, max_value=len(df)-1, step=1)
            if st.button("🗑 Haqi"):
                df = df.drop(df.index[int(idx)])
                save_data(df); st.warning("Haqameera!"); st.rerun()

    # ---------- 📤 TELEGRAM ----------
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Excel Gara Telegram"):
        send_telegram(df, "Gabaasa_Dadar_2026")
        st.sidebar.success("Telegram-itti ergameera!")

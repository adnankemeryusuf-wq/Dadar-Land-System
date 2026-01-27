import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & LOGO =================
LOGO_PATH = "Adiaan/logo.png"  # Maqaa logo keetii kanaan save godhi
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# Folder nagahee fi kkf uumuu
if not os.path.exists("nagahee_scan"):
    os.makedirs("nagahee_scan")

# ================= 2. FUNCTIONS =================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"}
        requests.get(url, params=params)
    except: pass

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. UI STYLE & LOGO DISPLAY =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f8fafc; }
    .login-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-top: 10px solid #2e7d32; text-align: center; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# ================= 4. LOGIN SYSTEM =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=130)
        st.header("Wajjira Lafa Magaalaa Dadar")
        st.subheader("Sirna Galmee Maamiltootaa")
        with st.form("Login"):
            u = st.text_input("Fayyadamaa (Username)")
            p = st.text_input("Sanyi-darbituu (Password)", type="password")
            if st.form_submit_button("SEENI", use_container_width=True):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora! Maaloo irra deebi'ii yaali.")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= 5. MAIN APP =================
else:
    df = load_data()
    
    # Sidebar Logo
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, width=100)
    st.sidebar.title("Main Menu")
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=80)
            
        today = datetime.now().strftime('%d/%m/%Y')
        today_df = df[df['Guyyaa'] == today]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Har'aa", f"{today_df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota Har'aa", len(today_df))
        c3.metric("👷 Ogeeyyii", today_df['Maqaa_Ogeessa'].nunique())

        st.subheader("Gabaasa Guyyaa Telegramitti Ergi")
        if st.button("🚀 Gabaasa Har'aa Telegramitti Ergi"):
            if not today_df.empty:
                msg = f"📅 *GABAASA GUYYAA: {today}*\n\n💰 Galii: {today_df['Kafaltii_Taj'].sum():,.2f} ETB\n👥 Maamiltoota: {len(today_df)}\n👷 Ogeeyyii: {today_df['Maqaa_Ogeessa'].nunique()}\n\n🏢 *Wajjira Lafa Dadar*"
                send_telegram(msg)
                st.success("Gabaasni ergameera!")

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            og = c1.text_input("Maqaa Ogeessaa")
            gosa = c2.selectbox("Gosa Tajaajilaa", ["Gibira", "Kaartaa", "Clearance", "Liizii"])
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, og, fee]
                    df = pd.concat([df, pd.DataFrame([row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    send_telegram(f"🆕 *Galmee Haaraa*\n👤: {name}\n🛠: {gosa}\n💰: {fee} ETB")
                    st.success("Galmeeffameera!")

    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Hojii")
        st.dataframe(df, use_container_width=True)

# ================= 4. SERVICE LIST =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
}

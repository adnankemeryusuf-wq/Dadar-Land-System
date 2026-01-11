import streamlit as st
import os
import requests
import pandas as pd
import openpyxl
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
import plotly.express as px

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System V9", layout="wide", page_icon="🏢")

USER_NAME, PASS_WORD = "admin", "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send" # IP Gateway kee
DEVICE_ID = "1" 
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "logo.png"

# --- 2. FUNKSHIINIIWWAN GARGAARTUU ---

def to_eth_date(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def send_sms(phone, message):
    try:
        if phone.startswith('0'): phone = "+251" + phone[1:]
        payload = {'token': SMS_TOKEN, 'device': DEVICE_ID, 'to': phone, 'message': message}
        res = requests.post(SMS_URL, data=payload, timeout=7)
        return res.status_code == 200
    except: return False

def send_telegram_file(file_data, file_name, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, 
                      files={'document': (file_name, file_data)}, timeout=15)
    except: st.error("Telegram erguu hin danda'amne!")

def generate_award_pdf(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(31, 78, 120); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    pdf.set_font('Arial', 'B', 30); pdf.ln(50)
    pdf.cell(0, 20, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 15, f"Ogeessa Kabajamaa: {name.upper()}", ln=True, align='C')
    pdf.multi_cell(0, 12, f"Waggaa {year} keessa tajaajila quubsaa fi amanamummaa qabuun tajaajilaa waan turaniif badhaasa {rank}ffaa ta'uun qophaa'eef.", align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box { text-align: center; padding: 25px; background: linear-gradient(90deg, #1f4e78, #2e75b6); color: white; border-radius: 15px; margin-bottom: 20px; }
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #1f4e78; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1.2,1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.subheader("Login - Dadar Land System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username/Password dogoggora!")
else:
    # Sidebar
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = st.radio("MENU", ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa & Sartifiketii", "🚪 Logout"])
        st.divider()
        st.write(f"📅 **Guyyaa:** {to_eth_date(datetime.now())}")

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    # Load Data
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, sep="|", header=None, on_bad_lines='skip')
        df.columns = ["Yeroo", "Maqaa", "Araddaa", "Wirtuu", "Bilbila", "Dhimma", "Ogeessa", "B_Ogeessa", "Beellama", "Kartaa", "Lizi", "TOT", "Waligala"]
    else: df = pd.DataFrame()

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card">👤 Galmee Waliigalaa<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card">💰 Galii Waliigalaa<br><h2>{df["Waligala"].sum():,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card">🛠️ Tajaajila Baay\'ee<br><h2>{df["Dhimma"].mode()[0]}</h2></div>', unsafe_allow_html=True)
            
            st.write("---")
            fig = px.bar(df, x="Dhimma", y="Waligala", color="Araddaa", title="Galii Gosa Tajaajilaatiin")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Ragaan galmaa'e hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        with st.form("RegForm", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                bad = st.text_input("Bilbila AD (09...)")
                ar = st.text_input("Araddaa")
                wi = st.text_input("Wirtuu")
            with col2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Lizi", "Jijjiirraa Maqaa", "Safara", "Gibira"])
                og = st.text_input("Maqaa Ogeessaa")
                bog = st.text_input("Bilbila Ogeessaa")
                beellama = st.text_input("Guyyaa & Sa'aatii Beellamaa (Fkn: 2026-02-10 09:00)")

            st.write("💰 **Kafaltiiwwan**")
            k1, k2, k3 = st.columns(3)
            v_kartaa = k1.number_input("Kartaa", value=0.0)
            v_lizi = k2.number_

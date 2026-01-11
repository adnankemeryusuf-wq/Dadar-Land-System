import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System V6", layout="wide", page_icon="🏢")

# Akkaatatti seenamu
USER_NAME = "admin"
PASS_WORD = "1234"

# Telegram & SMS Config
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "logo.png"

# --- 2. FUNKSHIINIIWWAN GARGAARTUU ---

def to_ethiopian_str(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def send_sms(phone, message):
    try:
        if phone.startswith('0'): phone = "+251" + phone[1:]
        payload = {'token': SMS_TOKEN, 'to': phone, 'message': message}
        res = requests.post(SMS_URL, data=payload, timeout=5)
        return res.status_code == 200
    except: return False

def send_telegram_file(file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, files={'document': f})
    except: pass

def generate_award_pdf(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(31, 78, 120); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, x=130, y=15, w=35)
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 25); pdf.cell(0, 15, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', '', 18); pdf.cell(0, 15, f"Ogeessa Kabajamaa: {name.upper()}", ln=True, align='C')
    pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 10, f"Bara {year} tajaajila quubsaa kennaa turaniif badhaasa {rank}ffaa ta'uun isiniif qophaa'e.", align='C')
    pdf.ln(20); pdf.cell(0, 10, "Obbo Aqiil Abdujaalil - Itti Gaafatamaa Waajjiraa", ln=True, align='C')
    f_name = f"Award_{name}.pdf"
    pdf.output(f_name)
    return f_name

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .header-style { background: #1f4e78; color: white; padding: 20px; border-radius: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1.2,1])
    with col:
        st.info("System Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogooggora!")
else:
    # Sidebar
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        menu = st.radio("MENU", ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Excel", "📜 Sartifiketii", "🚪 Logout"])

    st.markdown('<div class="header-style"><h1>Bulchiinsa Lafaa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)
    st.write(f"📅 Guyyaa (E.C): **{to_ethiopian_str(datetime.now())}**")

    if menu == "🏠 Dashboard":
        st.subheader("Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("Galmee Har'aa", "15", "+3")
        c2.metric("Ogeessota Online", "8", "Active")
        c3.metric("Kafaltii Waligala", "45,000 ETB", "Today")

    elif menu == "📝 Galmee Haaraa":
        st.subheader("Galmee Abbaa Dhimmaa Fi Ogeessaa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ad_name = st.text_input("Maqaa Abbaa Dhimmaa")
                ad_phone = st.text_input("Bilbila AD (09...)")
                araddaa = st.text_input("Araddaa")
            with col2:
                service = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Lizi", "Jijjiirraa Maqaa", "Gibira"])
                og_name = st.text_input("Maqaa Ogeessaa")
                og_phone = st.text_input("Bilbila Ogeessaa (09...)")
            
            pay = st.number_input("Waliigala Kafaltii", min_value=0.0)
            beellama = st.date_input("Guyyaa Beellamaa")
            
            if st.form_submit_button("Galmeessi & SMS Ergi"):
                if ad_name and ad_phone:
                    # Save Data
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    data = f"{now}|{ad_name}|{ad_phone}|{araddaa}|{service}|{og_name}|{og_phone}|{beellama}|{pay}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(data)
                    
                    # SMS Notification
                    msg_ad = f"Kabajamaa {ad_name}, tajaajila {service}af galmeeffamtaniittu. Beellama: {beellama}. Dadar Land."
                    msg_og = f"Ogeessa {og_name}, tajaajilli {service} (AD: {ad_name}) isiniif kennameera."
                    send_sms(ad_phone, msg_ad)
                    send_sms(og_phone, msg_og)
                    
                    # Telegram Manager
                    tel_txt = f"✅ Galmee Haaraa: {ad_name}\nTajaajila: {service}\nOgeessa: {og_name}\nKafaltii: {pay} ETB"
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID_MANAGER, 'text': tel_txt})
                    
                    st.success("Galmeeffameera! SMS fi Telegram ergameera.")
                    st.balloons()

    elif menu == "📊 Gabaasa & Excel":
        st.subheader("Gabaasa Excel Qopheessi")
        if st.button("Uumi & Telegram-itti Ergi"):
            if os.path.exists(DATA_FILE):
                wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Gabaasa"
                headers = ["Guyyaa", "Maqaa AD", "Bilbila", "Araddaa", "Tajaajila", "Ogeessa", "Kafaltii"]
                ws.append(headers)
                with open(DATA_FILE, "r") as f:
                    for line in f:
                        p = line.strip().split("|")
                        ws.append([p[0], p[1], p[2], p[3], p[4], p[5], p[8]])
                
                f_name = f"Gabaasa_Dadar_{datetime.now().strftime('%H%M%S')}.xlsx"
                wb.save(f_name)
                send_telegram_file(f_name, "Gabaasa Mana Hojii")
                st.success(f"Gabaasni {f_name} uumamee Telegram irratti hoggantootaaf ergameera.")

    elif menu == "📜 Sartifiketii":
        st.subheader("Sartifiketii Badhaasa Ogeessaa")
        og_n = st.text_input("Maqaa Ogeessaa")
        rank = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
        year = st.text_input("Waggaa", "2018")
        if st.button("PDF Qopheessi"):
            if og_n:
                file = generate_award_pdf(og_n, rank, year)
                with open(file, "rb") as f:
                    st.download_button("📥 Sartifiketii Buufadhu", f, file_name=file)
                st.success("Sartifiketiin qophaa'eera.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()


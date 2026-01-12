import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "Dadar2026"
# KANNA DHUGAA GALCHI:
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "-1002345678901" # ID Garee keetii as galchi (Fkn: -100...)
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

# --- 2. FUNKSHIINIIWWAN TELEGRAM ---

def send_telegram_msg(message):
    """Ergaa barreffamaa qofa erguuf"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=payload)
        return response.json()
    except Exception as e:
        st.error(f"Ergaan hin dabarre: {e}")
        return None

def send_telegram_file(file_path, caption):
    """Faayila (txt/Excel) erguuf"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            files = {"document": file}
            payload = {"chat_id": CHAT_ID, "caption": caption}
            response = requests.post(url, data=payload, files=files)
            return response.json()
    except Exception as e:
        st.error(f"Faayilli hin dabarre: {e}")
        return None

# --- 3. FUNKSHIINIIWWAN BIROO ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(31, 78, 120); pdf.set_line_width(4); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(218, 165, 32); pdf.set_line_width(1.5); pdf.rect(13, 13, 271, 184)
    if LOGO_PATH: pdf.image(LOGO_PATH, x=133, y=18, w=30)
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 35); pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 15, 'SARTIFIKETII KABAJAA', ln=True, align='C')
    pdf.ln(15); pdf.set_font('Arial', '', 20); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Badhaasni kun ogeessa gahumsa qabuuf kenname:', ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 30); pdf.set_text_color(184, 134, 11)
    pdf.cell(0, 20, name.upper(), ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 16); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 10, f"Waggaa {year} keessa tajaajila gaarii fi amanamummaa qabuun tajaajilaa waan turtaniif badhaasa sadarkaa {rank}ffaa argattanii jirtu.", align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. CSS STYLE ---
st.markdown("""<style> .stApp { background-color: #f4f7f9; } .header-box { text-align: center; padding: 40px; background: linear-gradient(135deg, #0f2027, #2c5364); color: white; border-radius: 20px; } .metric-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #1f4e78; } </style>""", unsafe_allow_html=True)

# --- 5. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div style="background:white; padding:40px; border-radius:20px; margin-top:50px; box-shadow:0 10px 30px rgba(0,0,0,0.1); text-align:center;">', unsafe_allow_html=True)
        st.title("Dadar Land Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- MAIN APP ---
    with st.sidebar:
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.sidebar.selectbox("Menu", menu)
        st.info(f"📅 Hardha: {to_ethiopian(datetime.now())}")

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Magaalaa Dadar</h1><p>Sistama Bulchiinsa Ragaa Ammayyaa</p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="metric-card"><h4>👥 Abbootii Dhimmaa</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            rev = df.iloc[:, -1].astype(float).sum()
            c2.markdown(f'<div class="metric-card"><h4>💰 Galii</h4><h2>{rev:,.0f} ETB</h2></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="metric-card"><h4>✅ Status</h4><h2>Active</h2></div>', unsafe_allow_html=True)
            st.subheader("📊 Haala Hojii")
            st.bar_chart(df[5].value_counts())
        else:
            st.info("Ragaan hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        with st.form("AddRecord", clear_on_submit=True):
            f1, f2 = st.columns(2)
            ad = f1.text_input("👤 Maqaa Abbaa Dhimmaa")
            ar = f1.text_input("📍 Araddaa")
            wi = f1.text_input("🏢 Wirtuu")
            gs = f2.selectbox("🛠️ Gosa Tajaajilaa", ["Kartaa", "Jijjiiraa Maqaa", "Gibira", "Kan biro"])
            og = f2.text_input("👨‍💼 Maqaa Ogeessaa")
            kaf = f2.number_input("💵 Kafaltii (ETB)", min_value=0.0)
            if st.form_submit_button("✅ GALMEESSI"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                line = f"{now}|{ad}|{ar}|{wi}|-|{gs}|{og}|-|Hardha|0|0|0|{kaf}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                st.success(f"Galmee {ad} milkiin raawwate!")
                st.balloons()

    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📁 Gabaasa Telegram", "🎓 Sartifiketii"])
        
        with tab1:
            st.subheader("Gabaasa Gara Telegram-itti Ergi")
            if st.button("🚀 GABAASA ERGI"):
                if os.path.exists(DATA_FILE):
                    df = pd.read_csv(DATA_FILE, sep="|", header=None)
                    t_clients = len(df)
                    t_rev = df.iloc[:, -1].astype(float).sum()
                    
                    # 1. Ergaa Gabaabaa qopheessi
                    report_msg = f"📊 <b>GABAASA WAJJIRA LAFA DADAR</b>\n" \
                                 f"📅 Guyyaa: {to_ethiopian(datetime.now())}\n" \
                                 f"----------------------------------\n" \
                                 f"👥 Abbootii Dhimmaa: {t_clients}\n" \
                                 f"💰 Galii Waligalaa: {t_rev:,.2f} ETB\n" \
                                 f"----------------------------------\n" \
                                 f"✅ Sistama irraa ergame."
                    
                    # 2. Telegram-itti ergi
                    res1 = send_telegram_msg(report_msg)
                    res2 = send_telegram_file(DATA_FILE, "Faayila Ragaa Guutuu (Database)")
                    
                    if res1 and res2:
                        st.success("Gabaasni milkiin garee Telegram-itti ergameera!")
                    else:
                        st.error("Dogoggora uumameera. Bot Token fi Chat ID kee mirkaneessi.")
                else:
                    st.warning("Ragaan erguu dandeessu hin jiru.")
        
        with tab2:
            c_name = st.text_input("Maqaa Ogeessaa")
            c_rank = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
            if st.button("🎨 SARTIFIKETII UUMI"):
                if c_name:
                    pdf = generate_certificate(c_name, c_rank, "2017")
                    st.download_button("📥 Buufadhu", pdf, f"{c_name}.pdf")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

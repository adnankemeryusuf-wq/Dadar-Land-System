import streamlit as st
import os
import requests
import pandas as pd
import qrcode
import openpyxl
from datetime import datetime, timedelta
from io import BytesIO
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
from openpyxl.styles import Font, PatternFill

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send" # IP Gateway kee
DEVICE_ID = "1" # Device ID kee asitti galchi
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

# --- 2. CSS STYLE (PC FORMAT) ---
st.markdown("""
    <style>
    .header-box { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 15px; border-bottom: 5px solid #1f4e78; margin-bottom: 20px; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .login-card { max-width: 400px; margin: auto; padding: 40px; background: white; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKSHIINIIWWAN (SMS, TELEGRAM, DATE) ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def send_sms(phone, message):
    try:
        if phone.startswith('0'): phone = "+251" + phone[1:]
        payload = {'token': SMS_TOKEN, 'device': DEVICE_ID, 'to': phone, 'message': message}
        res = requests.post(SMS_URL, data=payload, timeout=5)
        return res.status_code == 200
    except: return False

def send_telegram_file(file_data, file_name, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, files={'document': (file_name, file_data)})
    except: st.error("Telegram erguu hin danda'amne!")

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(31, 78, 120); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    pdf.set_font('Arial', 'B', 30)
    pdf.ln(40)
    pdf.cell(0, 20, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', '', 18)
    pdf.cell(0, 15, f"Ogeessa Kabajamaa: {name.upper()}", ln=True, align='C')
    pdf.multi_cell(0, 10, f"Waggaa {year} keessa tajaajila quubsaa kennaa turaniif badhaasa {rank} ta'uun qophaa'eef.", align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=120)
        st.subheader("Dadar Land System Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username/Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. MAIN INTERFACE ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.sidebar.selectbox("Main Menu", menu)
        st.divider()
        st.info(f"System Date: {to_ethiopian(datetime.now())}")

    # Header
    st.markdown('<div class="header-box">', unsafe_allow_html=True)
    if LOGO_PATH: st.image(LOGO_PATH, width=80)
    st.markdown("<h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- DASHBOARD ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            total_rev = df.iloc[:, -1].astype(float).sum()
            c1, c2, c3 = st.columns(3)
            c1.metric("Abbootii Dhimmaa", len(df))
            c2.metric("Galii Waligalaa", f"{total_rev:,.2f} ETB")
            c3.metric("Status", "Online ✅")
            st.write("### 🕒 Galmeewwan Dhiyoo")
            st.dataframe(df.tail(10), use_container_width=True)
        else: st.info("Ragaan galmaa'e hin jiru.")

    # --- GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Haaraa Galchi")
        with st.form("RegForm", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                bad = st.text_input("Bilbila AD")
                ar = st.text_input("Araddaa")
            with col2:
                wi = st.text_input("Wirtuu")
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Gibira"])
                og = st.text_input("Maqaa Ogeessaa")
            with col3:
                bog = st.text_input("Bilbila Ogeessaa")
                gb = st.date_input("Guyyaa Beellamaa")
                sb = st.time_input("Sa'aatii")

            st.write("--- 💰 Kafaltiiwwan ---")
            k1, k2, k3 = st.columns(3)
            kartaa = k1.number_input("Kartaa", value=0.0)
            lizi = k2.number_input("Lizi", value=0.0)
            tot = k3.number_input("TOT/Gibira", value=0.0)

            if st.form_submit_button("✅ GALMEESSI FI SMS ERGI"):
                if ad and bad:
                    total = kartaa + lizi + tot
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Save Data
                    line = f"{now_str}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|{bog}|{gb} {sb}|{kartaa}|{lizi}|{tot}|{total}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    
                    # SMS Sending
                    msg_ad = f"Kabajamaa {ad}, tajaajila {gs}af galmeeffamtaniittu. Beellama: {gb}. W/L/M/Dadar."
                    send_sms(bad, msg_ad)
                    if bog:
                        msg_og = f"Ogeessa {og}, mamiila {ad} (Araddaa {ar}) safaruuf beellama qabdu."
                        send_sms(bog, msg_og)
                    
                    st.success(f"Galmee {ad} milkiin xumurameera! SMS ergameera.")
                else: st.warning("Maaloo maqaa fi bilbila galchi.")

    # --- GABAASA & CERTIFICATE ---
    elif choice == "📊 Gabaasa & Sartifiketii":
        st.subheader("📊 Gabaasa Excel fi Sartifiketii Ogeessaa")
        f_type = st.radio("Yeroo Filadhu:", ["Guyyaa 1", "Ji'a 1", "Waggaa 1"])
        
        if st.button("🚀 GABAASA GENERATE GODHI"):
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE, sep="|", header=None)
                # Excel Creation
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Gabaasa')
                
                send_telegram_file(output.getvalue(), f"Gabaasa_{f_type}.xlsx", f"Gabaasa {f_type}")
                st.success("Gabaasni Telegram irratti ergameera!")
                
                # Certificate Logic (Top 1)
                if f_type == "Waggaa 1":
                    top_og = df[6].value_counts().idxmax()
                    cert_pdf = generate_certificate(top_og, "1ffaa", "2018")
                    send_telegram_file(cert_pdf, f"Sartifiketii_{top_og}.pdf", f"Badhaasa Ogeessa Waggaa: {top_og}")
                    st.balloons()
                    st.success(f"Sartifiketiin {top_og} uumamee ergameera!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

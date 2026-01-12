import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
import plotly.express as px

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System V11", layout="wide", page_icon="🏢")

USER_NAME, PASS_WORD = "admin", "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "logo.png"
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send" 
DEVICE_ID = "1"

# --- 2. FUNKSHIINIIWWAN ---

def to_ethiopian(dt):
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

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(31, 78, 120)
    pdf.set_line_width(2.5)
    pdf.rect(10, 10, 277, 190)
    
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=133, y=15, w=30)
    
    pdf.ln(38)
    pdf.set_font('Arial', 'B', 26); pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 15, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 16); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Badhaasni kun ogeessa kabajamaa:", ln=True, align='C')
    pdf.set_font('Arial', 'B', 24); pdf.cell(0, 20, name.upper(), ln=True, align='C')
    pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 10, f"Waggaa {year} keessa tajaajila quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank}ffaa ta'uu keessaniif qophaa'e.", align='C')
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "Obbo Aqiil Abdujaliil - Office Head", align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .header-box { text-align: center; padding: 20px; background: linear-gradient(135deg, #1f4e78, #3b71a3); color: white; border-radius: 15px; margin-bottom: 20px; }
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #1f4e78; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MAIN LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.header("Seensa Systemii")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    # Sidebar
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        choice = st.radio("MENU", ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"])
        st.divider()
        st.write(f"📅 {to_ethiopian(datetime.now())}")

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    # --- LOAD DATA ---
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ["Yeroo", "Maqaa", "Araddaa", "Wirtuu", "Bilbila", "Dhimma", "Ogeessa", "B_Ogeessa", "Beellama", "Kartaa", "Lizi", "TOT", "Waligala"]
        except: df = pd.DataFrame()
    else: df = pd.DataFrame()

    # --- DASHBOARD ---
    if choice == "🏠 Dashboard":
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card">👥 Abbootii Dhimmaa<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card">💰 Galii Waligalaa<br><h2>{df["Waligala"].sum():,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card">✅ Haala Hojii<br><h2>Hojirra jira</h2></div>', unsafe_allow_html=True)
            
            st.plotly_chart(px.bar(df, x="Dhimma", title="Tajaajila Gosaan"), use_container_width=True)
        else: st.info("Ragaan galmaa'e hin jiru.")

    # --- GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Haaraa")
        with st.form("RegForm", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                bad = st.text_input("Bilbila AD")
                ar = st.text_input("Araddaa")
                wi = st.text_input("Wirtuu")
            with col2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Lizi", "Jijjiirraa Maqaa", "Safara", "Gibira"])
                og = st.text_input("Maqaa Ogeessaa")
                beellama = st.text_input("Beellama (Fkn: 2026-02-15)")
            
            k1, k2, k3 = st.columns(3)
            v_kartaa = k1.number_input("Kafaltii Kartaa", value=0.0)
            v_lizi = k2.number_input("Kafaltii Lizi", value=0.0)
            v_tot = k3.number_input("TOT/Gibira", value=0.0)

            if st.form_submit_button("✅ GALMEESSI"):
                if ad and bad:
                    total = v_kartaa + v_lizi + v_tot
                    now_s = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_line = f"{now_s}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|0|{beellama}|{v_kartaa}|{v_lizi}|{v_tot}|{total}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(new_line)
                    st.success(f"Galmeen {ad} milkiin xumurameera!")
                    st.balloons()
                else: st.error("Maaloo ragaa guuti!")

    # --- REPORT & CERTIFICATE ---
    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📊 Gabaasa Data", "🎓 Sartifiketii Ogeessaa"])
        
        with tab1:
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Excel Buufadhu", csv, "gabaasa.csv", "text/csv")
            else: st.info("Ragaan hin jiru.")

        with tab2:
            st.write("### Sartifiketii Ogeessa Waggaa Uumi")
            name_og = st.text_input("Maqaa Ogeessaa Galchi")
            rank_og = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
            if st.button("🎓 SARTIFIKETII GENERATE"):
                if name_og:
                    cert_pdf = generate_certificate(name_og, rank_og, "2018")
                    st.download_button("📥 Sartifiketii Buufadhu (PDF)", cert_pdf, f"Sartifiketii_{name_og}.pdf", "application/pdf")
                else: st.warning("Maaloo maqaa galchi.")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

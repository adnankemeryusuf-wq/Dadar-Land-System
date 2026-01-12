import streamlit as st
import pandas as pd
import os
import requests
import qrcode
from datetime import datetime, timedelta
from io import BytesIO
from fpdf import FPDF
import openpyxl

# --- 1. QINDAA'INA (CONFIG) ---
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
USER_NAME = "admin"
PASS_WORD = "1234"
LOGO_PATH = "logo.png" # Faayilli kun folder kee keessa jiraachuu qaba

st.set_page_config(page_title="Dadar Land System", layout="wide")

# --- 2. FUNKSHIINIIWWAN GARGAARTUU ---

def to_ethiopian(date_obj):
    # Gabaabumatti (E.C calculation complex waan ta'eef placeholder)
    # Library 'ethiopian_date' fayyadamuu dandeessa
    return f"{date_obj.day}/{date_obj.month}/{date_obj.year - 8} E.C"

def generate_certificate(name, rank, year):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="SARTIFIKETII BADHAASA OGEESSAA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Sartifiketiin kun ogeessa kabajamaa {name}f tajaajila "
                              f"gaarii waggaa {year} keessa kennaa turaniif sadarkaa {rank}ffaa "
                              f"ta'uun qophaa'eef.")
    return pdf.output(dest='S').encode('latin-1')

def send_telegram_file(file_data, file_name, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    payload = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try:
        requests.post(url, data=payload, files=files, timeout=20)
    except: st.error("Telegram erguun hin danda'amne.")

def get_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, sep="|", header=None, 
                          names=["Guyyaa", "Maqaa_AD", "Araddaa", "Wirtuu", "Bilbila", "Tajaajila", 
                                 "Ogeessa", "B_Ogeessa", "Beellama", "K_Kartaa", "K_User", "K_Jij", "Waligala"])
    return pd.DataFrame()

# --- 3. STYLE (CSS) ---
st.markdown("""
    <style>
    .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px #ddd; text-align: center; }
    .header-box { background: #007bff; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .login-card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<br><br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.header("Login - Dadar Land System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI / LOGIN"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username/Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. MAIN INTERFACE ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🔍 Barbaadi", "🚪 Logout"]
        choice = st.sidebar.selectbox("Funaansa", menu)
        st.divider()
        st.write(f"📅 Guyyaa: {to_ethiopian(datetime.now())}")

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1><p>Sistama Bulchiinsa Galmee Ammayyaa</p></div>', unsafe_allow_html=True)

    df = get_data()

    if choice == "🏠 Dashboard":
        if not df.empty:
            total_rev = df["Waligala"].sum()
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><h3>👥 Abbootii Dhimmaa</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><h3>💰 Galii Waligalaa</h3><h2>{total_rev:,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><h3>✅ Status</h3><h2>Hojirra jira</h2></div>', unsafe_allow_html=True)
            
            st.write("### 📈 Gosa Tajaajilaa")
            st.bar_chart(df["Tajaajila"].value_counts())
            st.dataframe(df.tail(10), use_container_width=True)
        else: st.info("Ragaan galmaa'e hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        with st.form("RegForm", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                wi = st.text_input("Wirtuu")
                bad = st.text_input("Bilbila AD")
            with col2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizio", "TOT", "Gibira"])
                og = st.text_input("Maqaa Ogeessa")
                gb = st.date_input("Beellama")
                sb = st.time_input("Sa'aatii")
            
            st.write("--- Kafaltiiwwan ---")
            k1 = st.number_input("Kafaltii Kartaa", 0.0)
            k2 = st.number_input("Kafaltii User", 0.0)
            k3 = st.number_input("Kafaltii Jijjiirraa", 0.0)
            
            if st.form_submit_button("Galmeessi"):
                waligala = k1 + k2 + k3
                now_s = datetime.now().strftime("%Y-%m-%d %H:%M")
                line = f"{now_s}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|-|{gb} {sb}|{k1}|{k2}|{k3}|{waligala}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                
                qr_img = qrcode.make(f"AD: {ad}\nKafaltii: {waligala} ETB\nBeellama: {gb}")
                buf = BytesIO()
                qr_img.save(buf, format="PNG")
                st.image(buf.getvalue(), caption="QR Code", width=200)
                st.success("Galmeeffameera!")

    elif choice == "📊 Gabaasa & Sartifiketii":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 GABAASA EXCEL TELEGRAM-ITTI ERGI"):
                if not df.empty:
                    output = BytesIO()
                    df.to_excel(output, index=False)
                    send_telegram_file(output.getvalue(), "Gabaasa_Dadar.xlsx", "Gabaasa Galmee")
                    st.success("Gabaasni ergameera!")
        with col2:
            name_og = st.text_input("Maqaa Ogeessaa")
            rank_og = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
            if st.button("🎓 SARTIFIKETII UUMI"):
                if name_og:
                    cert_data = generate_certificate(name_og, rank_og, "2018")
                    st.download_button("📥 Buufadhu", cert_data, f"{name_og}.pdf")
                    st.balloons()

    elif choice == "🔍 Barbaadi":
        search = st.text_input("Maqaa galchi:")
        if search:
            res = df[df['Maqaa_AD'].str.contains(search, case=False, na=False)]
            st.dataframe(res)

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

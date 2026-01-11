import streamlit as st
import os
import requests
import qrcode
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- QINDAA'INA (CONFIG) ---
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8586015354:AAEliISf-RtoeJ8anbVLapY3NBm7hz8dZWI"
CHAT_ID_MANAGER = "568248052"
DATA_FILE = "dadar_final_report.txt"

# --- LOGO BARBAADU ---
logo_options = ["Adiaan/logo.png", "Adiaan/logo.png.png", "logo.png", "logo.png.png"]
LOGO_PATH = next((p for p in logo_options if os.path.exists(p)), None)

# --- WEB UI CONFIG ---
st.set_page_config(
    page_title="Dadar Land Administration System", 
    page_icon=LOGO_PATH if LOGO_PATH else "🏢",
    layout="wide"
)

# --- CUSTOM CSS (Style Bareeduuf) ---
st.markdown("""
    <style>
    /* Gidduu qabachiisuuf (Centering) */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #007bff; }
    .stButton>button { border-radius: 8px; background-color: #007bff; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKSHIINIIWWAN ---
def send_telegram(file_data, file_name, file_type="doc", caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    url += "sendDocument" if file_type == "doc" else "sendPhoto"
    try:
        files = {'document' if file_type == "doc" else 'photo': (file_name, file_data)}
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, files=files, timeout=20)
    except:
        st.error("Internet kee mirkaneeffadhu!")

# --- LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        if LOGO_PATH: st.image(LOGO_PATH, width=180)
        st.title("Dadar Land System Login")
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni (Login)"):
                if u == USER_NAME and p == PASS_WORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Login Dogoggora!")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.markdown("---")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa Excel", "🚪 Logout"]
        choice = st.selectbox("Menu Filadhu:", menu)

    # --- CENTERED HEADER (LOGO FI MAQAA) ---
    # Bakka kanaatu logo gidduu qabachiisa
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    if LOGO_PATH:
        st.image(LOGO_PATH, width=120)
    st.markdown("""
        <h1 style='margin-top: 10px; color: #1f4e78;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>
        <p style='color: #6c757d; font-size: 18px;'>Customer Registration & Management System</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 1. DASHBOARD ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            total_entries = len(df)
            total_money = df[10].astype(float).sum() if len(df.columns) > 10 else 0
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Abbootii Dhimmaa", f"{total_entries}")
            c2.metric("Galii Waligalaa", f"{total_money:,.2f} ETB")
            c3.metric("System Status", "Online ✅")
            
            st.write("### 🕒 Galmeewwan Dhiyoo")
            df.columns = ["Yeroo", "Maqaa", "Bilbila", "Tajaajila", "Ogeessa", "B_Ogeessa", "Beellama", "Kartaa", "User", "Jijjiirra", "Waligala"]
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("Ragaan galmaa'e hin jiru.")

    # --- 2. GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Haaraa Galchi")
        with st.form("RegForm", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                bad = st.text_input("Bilbila Abbaa Dhimmaa")
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizio", "TOT", "Gibira"])
            with col2:
                og = st.text_input("Maqaa Ogeessa")
                gb = st.date_input("Beellama")
                sb = st.time_input("Sa'aatii")
            
            st.markdown("---")
            k1, k2, k3 = st.columns(3)
            with k1: kartaa = st.number_input("Kartaa", value=0.0)
            with k2: user = st.number_input("User", value=0.0)
            with k3: jij = st.number_input("Jijjiirra", value=0.0)
            
            if st.form_submit_button("✅ Galmeessi"):
                if ad and bad:
                    total = kartaa + user + jij
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Save
                    line = f"{now}|{ad}|{bad}|{gs}|{og}|-|{gb} {sb}|{kartaa}|{user}|{jij}|{total}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    # QR
                    qr = qrcode.make(f"AD: {ad}\nKafaltii: {total}\nBeellama: {gb}")
                    buf = BytesIO(); qr.save(buf, format="PNG")
                    send_telegram(buf.getvalue(), f"{ad}.png", "photo", f"✅ Galmee: {ad}\n💰 {total} ETB")
                    st.success(f"Galmee {ad} milkiin xumurameera!")
                    st.image(buf.getvalue(), width=150)

    # --- 3. GABAASA EXCEL ---
    elif choice == "📊 Gabaasa Excel":
        st.subheader("📊 Gabaasa Gara Telegram")
        if st.button("🚀 Excel Gara Telegram Ergi"):
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE, sep="|", header=None)
                buf = BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                send_telegram(buf.getvalue(), "Gabaasa.xlsx", "doc", "Gabaasa Bulchiinsa Lafaa")
                st.success("Gabaasni hoggantatti ergameera!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

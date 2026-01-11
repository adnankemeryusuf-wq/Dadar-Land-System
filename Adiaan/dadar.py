import streamlit as st
import os
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA JALQABAA (Must be the first Streamlit command) ---
st.set_page_config(page_title="Dadar Land System V9", layout="wide", page_icon="🏢")

# --- 2. CONFIGURATION & PATHS ---
USER_NAME, PASS_WORD = "admin", "1234"
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send" 
DEVICE_ID = "1" 
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "logo.png" # Fakkii logo kee asitti kaa'i

# --- 3. HELPER FUNCTIONS ---
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

# --- 4. CUSTOM CSS (Styling) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box { text-align: center; padding: 20px; background: linear-gradient(90deg, #1f4e78, #2e75b6); color: white; border-radius: 15px; margin-bottom: 20px; }
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #1f4e78; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LOGIN LOGIC ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1.5,1])
    with col:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        st.subheader("Login - Dadar Land System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username/Password dogoggora!")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)
        st.title("Main Menu")
        menu = st.radio("Filaa:", ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa", "🚪 Logout"])
        st.divider()
        st.info(f"📅 Guyyaa: {to_eth_date(datetime.now())}")
        if menu == "🚪 Logout":
            st.session_state.logged_in = False
            st.rerun()

    # --- HEADER WITH LOGO ---
    col1, col2 = st.columns([1, 6])
    with col1:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=80)
    with col2:
        st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    # Load Data
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ["Yeroo", "Maqaa", "Araddaa", "Wirtuu", "Bilbila", "Dhimma", "Ogeessa", "B_Ogeessa", "Beellama", "Kartaa", "Lizi", "TOT", "Waligala"]
        except: df = pd.DataFrame()
    else: df = pd.DataFrame()

    # --- ROUTING LOGIC ---
    if menu == "🏠 Dashboard":
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card">👤 Galmee Waliigalaa<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card">💰 Galii Waliigalaa<br><h2>{df["Waligala"].sum():,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card">🛠 Tajaajila Baay\'ee<br><h2>{df["Dhimma"].mode()[0]}</h2></div>', unsafe_allow_html=True)
            
            fig = px.pie(df, names="Dhimma", values="Waligala", title="Raawwii Gosa Tajaajilaa (Galii)")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Ragaan galmaa'e hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Haaraa")
        with st.form("RegForm", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                bad = st.text_input("Bilbila AD (09...)")
                ar = st.text_input("Araddaa")
                wi = st.text_input("Wirtuu")
            with col_b:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Lizi", "Jijjiirraa Maqaa", "Safara", "Gibira"])
                og = st.text_input("Maqaa Ogeessaa")
                bog = st.text_input("Bilbila Ogeessaa")
                beellama = st.text_input("Beellama (Fkn: 2026-02-10 04:00)")

            st.write("💰 Kafaltiiwwan")
            k1, k2, k3 = st.columns(3)
            v_kartaa = k1.number_input("Kafaltii Kartaa", min_value=0.0)
            v_lizi = k2.number_input("Kafaltii Lizi", min_value=0.0)
            v_tot = k3.number_input("TOT/Gibira", min_value=0.0)

            if st.form_submit_button("✅ GALMEESSI FI SMS ERGI"):
                if ad and bad:
                    total = v_kartaa + v_lizi + v_tot
                    now_s = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_line = f"{now_s}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|{bog}|{beellama}|{v_kartaa}|{v_lizi}|{v_tot}|{total}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f:
                        f.write(new_line)
                    
                    msg = f"Kabajamaa {ad}, tajaajila {gs}af galmeeffamtaniittu. Beellama: {beellama}. Dadar Land."
                    send_sms(bad, msg)
                    st.success(f"Galmeen {ad} milkiin xumurameera!")
                    st.balloons()
                else: st.error("Maaloo maqaa fi bilbila guuti!")

    elif menu == "✅ Xumurame Beeksisi":
        st.subheader("✅ Tajaajila Xumurame Beeksisi")
        if not df.empty:
            search_name = st.selectbox("Maqaa mamiilaa filadhu", df["Maqaa"].unique())
            mamiila = df[df["Maqaa"] == search_name].iloc[-1]
            if st.button("SMS Xumuraa Ergi"):
                msg = f"Kabajamaa {mamiila['Maqaa']}, tajaajilli keessan ({mamiila['Dhimma']}) xumurameera. Waajjira dhufuun fudhachuu dandeessu. Dadar Land."
                if send_sms(str(mamiila['Bilbila']), msg):
                    st.success(f"Beeksisni gara {mamiila['Bilbila']} ergameera!")
                else: st.error("SMS erguun hin danda'amne.")
        else: st.warning("Ragaan mamiilaa hin jiru.")

    elif menu == "📊 Gabaasa":
        st.subheader("📊 Gabaasa Daataa Waliigalaa")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Gabaasa CSV Download godhuuf", data=csv, file_name="gabaasa_dadar.csv", mime="text/csv")
        else: st.info("Gabaasni agarsiifamu hin jiru.")

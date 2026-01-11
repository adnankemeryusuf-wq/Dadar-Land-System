import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill
import plotly.express as px

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System V8", layout="wide", page_icon="🏢")

# Credential-ota kee
USER_NAME, PASS_WORD = "admin", "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
TRACCAR_URL = "http://localhost:8082/" # Localhost yoo ta'e server irratti jijjiirama
SMS_TOKEN = "08a96817-22ab-4660-b866-b7647dbcbf82"
DB_FILE = "galmee_abbaa_dhimmaa.txt"
LOGO_PATH = "logo.png"

# --- 2. FUNKSHIINIIWWAN GARGAARTUU ---

def load_data():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    data_list = []
    with open(DB_FILE, "r") as f:
        for line in f:
            parts = [x.split(":")[1].strip() for x in line.split("|")]
            data_list.append(parts)
    cols = ["ID", "Guyyaa", "Maqaa", "Bilbila", "Araddaa", "Wirtuu", "Dhimma", "Kartaa", "Lizi", "Beellama", "Ogeessa", "Status"]
    return pd.DataFrame(data_list, columns=cols)

def send_ethio_sms(bilbila, ergaa):
    if bilbila.startswith('0'): bilbila = "+251" + bilbila[1:]
    headers = {"Authorization": SMS_TOKEN, "Content-Type": "application/json"}
    payload = {"to": bilbila, "message": ergaa}
    try:
        requests.post(TRACCAR_URL, json=payload, headers=headers, timeout=5)
        return True
    except: return False

def send_telegram_file(file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as doc:
            requests.post(url, files={'document': doc}, data={'chat_id': CHAT_ID_MANAGER, 'caption': "Gabaasa Excel"})
    except: pass

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-header { background: #1f4e78; color: white; padding: 25px; border-radius: 15px; text-align: center; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #1f4e78; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.subheader("Seensa Systemii")
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
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = st.radio("HOJJEDHU", ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa & Telegram", "🚪 Logout"])
        st.info(f"System V8.0\nUser: {USER_NAME}")

    df = load_data()

    if menu == "🏠 Dashboard":
        st.markdown('<div class="header-header"><h1>Waajjira Lafaa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)
        st.write("")
        
        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card">Total Galmee<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2: 
            rev = df['Kartaa'].astype(float).sum() + df['Lizi'].astype(float).sum() if not df.empty else 0
            st.markdown(f'<div class="metric-card">Total Galii<br><h2>{rev:,.0f} ETB</h2></div>', unsafe_allow_html=True)
        with c3:
            pend = len(df[df['Status'] == 'Pending']) if not df.empty else 0
            st.markdown(f'<div class="metric-card">Harka Irra Jiru<br><h2>{pend}</h2></div>', unsafe_allow_html=True)
        with c4:
            fin = len(df[df['Status'] == 'Finished']) if not df.empty else 0
            st.markdown(f'<div class="metric-card">Xumuraman<br><h2>{fin}</h2></div>', unsafe_allow_html=True)

        if not df.empty:
            col_left, col_right = st.columns(2)
            with col_left:
                fig = px.pie(df, names='Dhimma', title="Gosa Tajaajilaa", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            with col_right:
                st.subheader("Galmee dhiyoo")
                st.table(df[['ID', 'Maqaa', 'Dhimma', 'Status']].tail(5))

    elif menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Fi Ogeessaa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
                bilbila_a = st.text_input("Bilbila AD")
                araddaa = st.text_input("Araddaa")
                wirtuu = st.text_input("Wirtuu")
            with col2:
                dhimma = st.selectbox("Dhimma", ["Kartaa", "Lizi", "Jijjiirraa Maqaa", "Safara", "Gibira"])
                beellama = st.date_input("Guyyaa Beellamaa")
                kartaa = st.number_input("Kafaltii Kartaa", value=0.0)
                lizi = st.number_input("Kafaltii Lizi", value=0.0)
            
            ogeessa = st.text_input("Maqaa Ogeessaa (Safaraaf yoo ta'e)")
            bilbila_o = st.text_input("Bilbila Ogeessaa")

            if st.form_submit_button("Galmeessi & SMS Ergi"):
                guyyaa_ammaa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                id_sys = datetime.now().strftime("%f")[:4]
                
                # Save to Text File
                dataa = (f"ID:{id_sys} | Guyyaa:{guyyaa_ammaa} | Maqaa:{maqaa} | Bilbila:{bilbila_a} | "
                         f"Araddaa:{araddaa} | Wirtuu:{wirtuu} | Dhimma:{dhimma} | Kartaa:{kartaa} | "
                         f"Lizi:{lizi} | Beellama:{beellama} | Ogeessa:{ogeessa} | Status:Pending\n")
                
                with open(DB_FILE, "a") as f: f.write(dataa)
                
                # SMS to Ogeessa if Safara
                if "safara" in dhimma.lower() and bilbila_o:
                    msg_o = f"Kabajamaa {ogeessa}, Ajaja Safaraa AD {maqaa}, Bilbila: {bilbila_a} isiniif kennameera."
                    send_ethio_sms(bilbila_o, msg_o)
                
                st.success(f"Galmeeffameera! ID: {id_sys}")
                st.balloons()

    elif menu == "✅ Xumurame Beeksisi":
        st.subheader("Dhimma Xumurame Beeksisi")
        id_input = st.text_input("ID Abbaa Dhimmaa Galchi:")
        if st.button("Xumurameera jedhi"):
            if not df.empty:
                rows = []
                found = False
                with open(DB_FILE, "r") as f:
                    lines = f.readlines()
                for line in lines:
                    if f"ID:{id_input}" in line and "Status:Pending" in line:
                        parts = [x.split(":")[1].strip() for x in line.split("|")]
                        # parts[2]=Maqaa, parts[3]=Bilbila, parts[6]=Dhimma
                        msg = f"Kabajamaa {parts[2]}, Dhimmi keessan ({parts[6]}) xumurameera. Guyyaa beellamaa dhuftanii fudhadhaa. Dadar Land."
                        send_ethio_sms(parts[3], msg)
                        line = line.replace("Status:Pending", "Status:Finished")
                        found = True
                    rows.append(line)
                with open(DB_FILE, "w") as f: f.writelines(rows)
                if found: st.success("SMS ergameera, Status 'Finished' jedhameera.")
                else: st.warning("ID hin argamne ykn duraan xumurameera.")

    elif menu == "📊 Gabaasa & Telegram":
        st.subheader("Excel & Telegram Report")
        if st.button("Excel Uumi & Telegram-itti Ergi"):
            if not df.empty:
                f_name = f"gabaasa_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx"
                df.to_excel(f_name, index=False)
                send_telegram_file(f_name)
                st.success(f"Gabaasni {f_name} uumamee Telegram irratti ergameera!")
            else: st.error("Data'n hin jiru.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
import streamlit as st
import os
import requests
import pandas as pd
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
SMS_URL = "http://10.181.252.6:8082/send" 
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

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box { text-align: center; padding: 25px; background: linear-gradient(90deg, #1f4e78, #2e75b6); color: white; border-radius: 15px; margin-bottom: 20px; }
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #1f4e78; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIN LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1.2,1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
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
        menu = st.radio("MENU", ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa", "🚪 Logout"])
        if menu == "🚪 Logout":
            st.session_state.logged_in = False
            st.rerun()

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    # Load Data
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ["Yeroo", "Maqaa", "Araddaa", "Wirtuu", "Bilbila", "Dhimma", "Ogeessa", "B_Ogeessa", "Beellama", "Kartaa", "Lizi", "TOT", "Waligala"]
        except: df = pd.DataFrame()
    else: df = pd.DataFrame()

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card">👤 Galmee Waliigalaa<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card">💰 Galii Waliigalaa<br><h2>{df["Waligala"].sum():,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card">🛠️ Tajaajila Baay\'ee<br><h2>{df["Dhimma"].mode()[0]}</h2></div>', unsafe_allow_html=True)
            
            fig = px.pie(df, names="Dhimma", values="Waligala", title="Raawwii Gosa Tajaajilaa")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Ragaan galmaa'e hin jiru.")

    # --- GALMEE HAARAA (FORM FIX) ---
    elif menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Haaraa")
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
                beellama = st.text_input("Beellama (Fkn: 2026-02-10 04:00)")

            st.write("💰 **Kafaltiiwwan**")
            k1, k2, k3 = st.columns(3)
            v_kartaa = k1.number_input("Kafaltii Kartaa", value=0.0)
            v_lizi = k2.number_input("Kafaltii Lizi", value=0.0)
            v_tot = k3.number_input("TOT/Gibira", value=0.0)

            submitted = st.form_submit_button("✅ GALMEESSI FI SMS ERGI")

            if submitted:
                if ad and bad:
                    total = v_kartaa + v_lizi + v_tot
                    now_s = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_line = f"{now_s}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|{bog}|{beellama}|{v_kartaa}|{v_lizi}|{v_tot}|{total}\n"
                    
                    with open(DATA_FILE, "a", encoding="utf-8") as f:
                        f.write(new_line)
                    
                    send_sms(bad, f"Kabajamaa {ad}, tajaajila {gs}af galmeeffamtaniittu. Beellama: {beellama}. Dadar Land.")
                    st.success(f"Galmeen {ad} milkiin xumurameera!")
                else: st.error("Maaloo maqaa fi bilbila guuti!")

    # --- XUMURAME BEEKSISI ---
    elif menu == "✅ Xumurame Beeksisi":
        st.subheader("✅ Tajaajila Xumurame Beeksisi")
        if not df.empty:
            search_name = st.selectbox("Maqaa Filadhu", df["Maqaa"].unique())
            mamiila = df[df["Maqaa"] == search_name].iloc[-1]
            
            if st.button("SMS Xumuraa Ergi"):
                msg = f"Kabajamaa {mamiila['Maqaa']}, tajaajilli keessan ({mamiila['Dhimma']}) xumurameera. Waajjira dhufuun fudhachuu dandeessu."
                if send_sms(mamiila['Bilbila'], msg):
                    st.success("Beeksisni ergameera!")
                else: st.error("SMS erguun hin danda'amne.")
        else: st.warning("Ragaan mamiilaa hin jiru.")

    # --- GABAASA ---
    elif menu == "📊 Gabaasa":
        st.subheader("📊 Gabaasa Waliigalaa")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Gabaasa Excel (CSV) Fudhadhu", csv, "gabaasa_dadar.csv", "text/csv")
        else: st.info("Ragaan gabaasaaf ta'u hin jiru.")

import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
from ethiopian_date import EthiopianDateConverter
import plotly.express as px

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System V10", layout="wide", page_icon="🏢")

USER_NAME, PASS_WORD = "admin", "1234"
DATA_FILE = "dadar_final_report.txt"
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send" 
DEVICE_ID = "1"

# --- 2. FUNKSHIINIIWWAN ---
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

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box { text-align: center; padding: 20px; background: linear-gradient(90deg, #1f4e78, #2e75b6); color: white; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login - Dadar Land System")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("SEENI"):
        if u == USER_NAME and p == PASS_WORD:
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Username/Password dogoggora!")
else:
    with st.sidebar:
        menu = st.radio("MENU", ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa", "🚪 Logout"])
        if menu == "🚪 Logout":
            st.session_state.logged_in = False
            st.rerun()

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    # --- GALMEE HAARAA ---
    if menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Haaraa")
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
                beellama = st.text_input("Beellama (Fkn: 2026-02-10 09:00)")

            st.write("💰 **Kafaltiiwwan**")
            k1, k2, k3 = st.columns(3)
            v_kartaa = k1.number_input("Kafaltii Kartaa", value=0.0)
            v_lizi = k2.number_input("Kafaltii Lizi", value=0.0)
            v_tot = k3.number_input("TOT/Gibira", value=0.0)

            submitted = st.form_submit_button("✅ GALMEESSI FI SMS ERGI")

            if submitted:
                if ad and bad:
                    total = v_kartaa + v_lizi + v_tot
                    now_s = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_line = f"{now_s}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|{bog}|{beellama}|{v_kartaa}|{v_lizi}|{v_tot}|{total}\n"
                    
                    with open(DATA_FILE, "a", encoding="utf-8") as f:
                        f.write(new_line)
                    
                    # SMS Erguu
                    msg_ad = f"Kabajamaa {ad}, tajaajila {gs}af galmeeffamtaniittu. Beellama: {beellama}. Dadar Land."
                    send_sms(bad, msg_ad)
                    
                    st.success(f"Galmeen {ad} milkiin xumurameera! SMS ergameera.")
                    st.balloons()
                else:
                    st.error("Maaloo maqaa fi bilbila galchi!")

    # --- DASHBOARD & GABAASA ---
    elif menu == "🏠 Dashboard" or menu == "📊 Gabaasa":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ["Yeroo", "Maqaa", "Araddaa", "Wirtuu", "Bilbila", "Dhimma", "Ogeessa", "B_Ogeessa", "Beellama", "Kartaa", "Lizi", "TOT", "Waligala"]
            st.dataframe(df)
            
            fig = px.bar(df, x="Dhimma", y="Waligala", title="Galii Gosa Tajaajilaatiin")
            st.plotly_chart(fig)
        else:
            st.info("Ragaan galmaa'e hin jiru.")


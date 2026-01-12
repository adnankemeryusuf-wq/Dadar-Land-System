import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dadar Land System ", layout="wide", page_icon="🏢")

# Credentials & API Config
USER_NAME, PASS_WORD = "admin", "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
TRACCAR_URL = "http://localhost:8082/" 
SMS_TOKEN = "08a96817-22ab-4660-b866-b7647dbcbf82"
DB_FILE = "galmee_abbaa_dhimmaa.txt"
LOGO_PATH = "logo.png"

# --- 2. HELPER FUNCTIONS ---

def load_data():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    data_list = []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                # Extracts values between colons and pipes
                parts = [x.split(":")[1].strip() for x in line.split("|") if ":" in x]
                if len(parts) == 12:  # Ensure all columns are present
                    data_list.append(parts)
            except IndexError:
                continue
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
            requests.post(url, files={'document': doc}, data={'chat_id': CHAT_ID_MANAGER, 'caption': "Gabaasa Excel Haaraa"})
    except Exception as e:
        st.error(f"Telegram Error: {e}")

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-header { background: #1f4e78; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .metric-card { background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #1f4e78; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
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
        if st.button("Seeni", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    # Sidebar Navigation
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = st.radio("HOJJEDHU", ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa & Telegram", "🚪 Logout"])
        st.divider()
        st.info(f"System Version: 8.1\nOgeessa: {USER_NAME}")

    df = load_data()

    if menu == "🏠 Dashboard":
        st.markdown('<div class="main-header"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)
        
        # Search Bar
        search_query = st.text_input("🔍 Barbaadi (Maqaa ykn ID galchi)", "")
        
        # Filter Data
        display_df = df.copy()
        if search_query:
            display_df = df[df['Maqaa'].str.contains(search_query, case=False, na=False) | 
                            df['ID'].str.contains(search_query, case=False, na=False)]

        # Metrics Row
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card">Total Galmee<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2: 
            total_rev = pd.to_numeric(df['Kartaa'], errors='coerce').sum() + pd.to_numeric(df['Lizi'], errors='coerce').sum() if not df.empty else 0
            st.markdown(f'<div class="metric-card">Total Galii<br><h2>{total_rev:,.0f} ETB</h2></div>', unsafe_allow_html=True)
        with c3:
            pend = len(df[df['Status'] == 'Pending']) if not df.empty else 0
            st.markdown(f'<div class="metric-card">Harka Irra Jiru<br><h2>{pend}</h2></div>', unsafe_allow_html=True)
        with c4:
            fin = len(df[df['Status'] == 'Finished']) if not df.empty else 0
            st.markdown(f'<div class="metric-card">Xumuraman<br><h2>{fin}</h2></div>', unsafe_allow_html=True)

        st.divider()

        if not display_df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                fig = px.pie(display_df, names='Dhimma', title="Gosa Tajaajilaa (Filtered)", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
            with col_right:
                st.subheader("Ragaalee Galmee")
                st.dataframe(display_df[['ID', 'Maqaa', 'Dhimma', 'Status']].tail(10), use_container_width=True)
        else:
            st.warning("Ragaan barbaadame hin argamne.")

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
                dhimma = st.selectbox("Dhimma", ["Itti Fayyadam", "Kartaa",  "Jijjiirraa Maqaa", "Walitti Bu'iinsa Dangaa", "Dhimmaa Mana Murtii"])
                beellama = st.date_input("Guyyaa Beellamaa")
                itti = st.number_input("Kafaltii Itti Fayyadam", value=0.0)
                kartaa = st.number_input("Kafaltii Kartaa", value=0.0)
                lizi = st.number_input("Kafaltii Jijjirraa Maqaa", value=0.0)
                lizi = st.number_input("Kafaltii Lizi Duraa", value=0.0)
                tot = st.number_input("Kafaltii TOT", value=0.0)
                kan = st.number_input("Kafaltii Biro", value=0.0)
            ogeessa = st.text_input("Maqaa Ogeessaa (Safaraaf yoo ta'e)")
            bilbila_o = st.text_input("Bilbila Ogeessaa")

            if st.form_submit_button("Galmeessi & SMS Ergi", use_container_width=True):
                guyyaa_ammaa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                id_sys = datetime.now().strftime("%H%M%S")[-4:] # Use last 4 of timestamp for better ID
                
                dataa = (f"ID:{id_sys} | Guyyaa:{guyyaa_ammaa} | Maqaa:{maqaa} | Bilbila:{bilbila_a} | "
                         f"Araddaa:{araddaa} | Wirtuu:{wirtuu} | Dhimma:{dhimma} | Kartaa:{kartaa} | "
                         f"Lizi:{lizi} | Beellama:{beellama} | Ogeessa:{ogeessa} | Status:Pending\n")
                
                with open(DB_FILE, "a", encoding="utf-8") as f: f.write(dataa)
                
                if "safara" in dhimma.lower() and bilbila_o:
                    msg_o = f"Kabajamaa {ogeessa}, Ajaja Safaraa AD {maqaa}, Bilbila: {bilbila_a} isiniif kennameera."
                    send_ethio_sms(bilbila_o, msg_o)
                
                st.success(f"Galmeeffameera! ID Haaraa: {id_sys}")
                st.balloons()

    elif menu == "✅ Xumurame Beeksisi":
        st.subheader("Dhimma Xumurame Beeksisi")
        id_input = st.text_input("ID Abbaa Dhimmaa Galchi:")
        if st.button("Xumurameera jedhi", use_container_width=True):
            if not df.empty:
                rows = []
                found = False
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for line in lines:
                    if f"ID:{id_input}" in line and "Status:Pending" in line:
                        parts = [x.split(":")[1].strip() for x in line.split("|") if ":" in x]
                        msg = f"Kabajamaa {parts[2]}, Dhimmi keessan ({parts[6]}) xumurameera. Guyyaa beellamaa dhuftanii fudhadhaa. Dadar Land."
                        send_ethio_sms(parts[3], msg)
                        line = line.replace("Status:Pending", "Status:Finished")
                        found = True
                    rows.append(line)
                
                with open(DB_FILE, "w", encoding="utf-8") as f: f.writelines(rows)
                if found: st.success("SMS ergameera, Status 'Finished' jedhameera.")
                else: st.warning("ID hin argamne ykn duraan xumurameera.")

    elif menu == "📊 Gabaasa & Telegram":
        st.subheader("Excel & Telegram Report")
        if st.button("Excel Uumi & Telegram-itti Ergi", use_container_width=True):
            if not df.empty:
                f_name = f"gabaasa_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
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
LOGO_PATH = "logo.png" 

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

    # --- MAIN HEADER ---
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





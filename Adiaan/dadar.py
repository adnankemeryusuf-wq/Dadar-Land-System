import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dadar Land System V8.1", layout="wide", page_icon="🏢")

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






import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import openpyxl
import plotly.express as px
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System V7", layout="wide", page_icon="🏢")

USER_NAME = "admin"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "logo.png" 

# SMS & Telegram (Settings kee)
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send"

# --- 2. FUNKSHIINIIWWAN ---

def to_eth_str(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def load_data():
    if not os.path.exists(DATA_FILE): return pd.DataFrame()
    try:
        df = pd.read_csv(DATA_FILE, sep="|", header=None, 
                         names=["Yeroo", "Maqaa_AD", "Bilbila_AD", "Araddaa", "Tajaajila", "Ogeessa", "Bilbila_Og", "Beellama", "Kafaltii"])
        return df
    except: return pd.DataFrame()

def send_sms(phone, message):
    try:
        if phone.startswith('0'): phone = "+251" + phone[1:]
        payload = {'token': SMS_TOKEN, 'to': phone, 'message': message}
        requests.post(SMS_URL, data=payload, timeout=5)
    except: pass

# --- 3. CSS STYLE (UI Ammayyaa) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box {
        background: linear-gradient(135deg, #1f4e78, #3b71a3);
        color: white; padding: 30px; border-radius: 15px;
        text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 5px solid #1f4e78;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIN LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.header("Login - Dadar Land System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogooggora!")
else:
    # --- MAIN INTERFACE ---
    df = load_data()
    
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        st.title("Admin Panel")
        menu = st.radio("Fayyadami:", ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Excel", "📜 Sartifiketii", "🚪 Logout"])
        st.markdown("---")
        st.write(f"📅 {to_eth_str(datetime.now())}")

    if menu == "🏠 Dashboard":
        st.markdown(f'<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1><p>Dashboard Sirna Hordoffii Ragaa</p></div>', unsafe_allow_html=True)
        
        # Metric Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><h3>Galmee</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2: 
            total = df['Kafaltii'].sum() if not df.empty else 0
            st.markdown(f'<div class="metric-card"><h3>Galii</h3><h2>{total:,.0f}</h2></div>', unsafe_allow_html=True)
        with c3:
            ar = df['Araddaa'].nunique() if not df.empty else 0
            st.markdown(f'<div class="metric-card"><h3>Araddaawwan</h3><h2>{ar}</h2></div>', unsafe_allow_html=True)
        with c4:
            og = df['Ogeessa'].nunique() if not df.empty else 0
            st.markdown(f'<div class="metric-card"><h3>Ogeessota</h3><h2>{og}</h2></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Section
        if not df.empty:
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("📊 Gosa Tajaajilaa")
                fig = px.pie(df, names='Tajaajila', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                st.subheader("📈 Galmee Guyyaan")
                df['Date_Obj'] = pd.to_datetime(df['Yeroo']).dt.date
                trend = df.groupby('Date_Obj').size().reset_index(name='Counts')
                fig2 = px.bar(trend, x='Date_Obj', y='Counts', color_discrete_sequence=['#1f4e78'])
                st.plotly_chart(fig2, use_container_width=True)
            
            st.subheader("📋 Ragaalee Galmee")
            st.dataframe(df.sort_values(by="Yeroo", ascending=False), use_container_width=True)
        else:
            st.info("Ragaan galmaa'e hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.subheader("Galmee Abbaa Dhimmaa Haaraa")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            ad_name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ad_phone = c1.text_input("Bilbila AD")
            araddaa = c1.text_input("Araddaa")
            service = c2.selectbox("Tajaajila", ["Kartaa", "Lizi", "Jijjiirraa Maqaa", "Gibira"])
            og_name = c2.text_input("Maqaa Ogeessaa")
            og_phone = c2.text_input("Bilbila Ogeessaa")
            pay = st.number_input("Kafaltii", min_value=0.0)
            beellama = st.date_input("Guyyaa Beellamaa")
            
            if st.form_submit_button("GALMEESSI"):
                if ad_name and ad_phone:
                    yeroo = datetime.now().strftime("%Y-%m-%d %H:%M")
                    line = f"{yeroo}|{ad_name}|{ad_phone}|{araddaa}|{service}|{og_name}|{og_phone}|{beellama}|{pay}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    
                    # SMS logic as per previous code
                    send_sms(ad_phone, f"Kabajamaa {ad_name}, tajaajila {service}af galmeeffamtaniittu. Dadar Land.")
                    st.success("Galmeeffameera!")
                    st.balloons()

    # (Kutaawwan biroo 'Gabaasa' fi 'Sartifiketii' akkuma koodii kee duraatti itti fufu)

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

import streamlit as st
import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. CONFIG ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

USER_NAME = "Lafa2026"
PASS_WORD = "Dadar@2026"
DATA_FILE = "dadar_final_report.txt"

# Telegram Config
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI" 
TELEGRAM_CHAT_ID = "7329587700"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Telegram-itti erguun hin danda'amne: {e}")

# --- 2. CSS STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    .header-box { 
        text-align: center; padding: 25px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #15803d 100%); 
        color: white; border-radius: 15px; margin-bottom: 20px;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border-top: 5px solid #15803d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>Seensa / Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    with st.sidebar:
        st.title("Dadar Land")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Telegram"]
        choice = st.selectbox("Menu", menu)

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            # Ragaa dubbisuu
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Bilbila', 'Gosa', 'Ogeessa', 'Maqaa_L_K', 'Guyyaa', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><h4>👥 Abbootii Dhimmaa</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><h4>💰 Galii Waligalaa</h4><h2>{df["Kafaltii"].sum():,.2f}</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><h4>✅ Status</h4><h2>Hojirra jira</h2></div>', unsafe_allow_html=True)
            
            st.subheader("Galmeewwan Dhiyoo")
            st.dataframe(df.tail(10), use_container_width=True)

    elif choice == "📝 Galmee Haaraa":
        with st.form("form", clear_on_submit=True):
            st.subheader("Ragaa Abbaa Dhimmaa Haaraa")
            c1, c2 = st.columns(2)
            with c1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                qx = st.text_input("Qaxana (Zone)")
                bl = st.text_input("Lakk. Bilbilaa")
            with c2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Ground", "Gibira"])
                og = st.text_input("Maqaa Ogeessa Tajaajila Kennu")
                lk = st.text_input("Lakk. Kenniinsa Tajaajilaa (Reference)")
                k_wal = st.number_input("Kafaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("GALMEE MIRKANEEESSI"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                # Format: Yeroo|Maqaa|Araddaa|Qaxana|Bilbila|Gosa|Ogeessa|Lakk_Kenniinsa|Guyyaa|0|0|0|Kafaltii
                line = f"{now}|{ad}|{ar}|{qx}|{bl}|{gs}|{og}|{lk}|Hardha|0|0|0|{k_wal}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(line)
                st.success(f"Ragaan '{ad}' milkiin galmaa'era!")
                st.balloons()

    elif choice == "📊 Gabaasa & Telegram":
        st.subheader("To'annoo Gabaasaa fi Ergaa Telegram")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Bilbila', 'Gosa', 'Ogeessa', 'Maqaa_L_K', 'Guyyaa', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Yeroo'] = pd.to_datetime(df['Yeroo'])
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)

            # --- FILTERS (Guyyaa, Torban, Jia...) ---
            st.markdown("### Filter Gabaasaa")
            f_col1, f_col2 = st.columns(2)
            now = datetime.now()
            
            with f_col1:
                yeroo_filadhu = st.radio("Yeroo Gabaasaa Filadhu:", 
                    ["Hunda", "Hardha", "Torban Kana", "Ji'a Kana", "Kurmaana (3 Mo)", "Waggaa Kana"], horizontal=True)

            if yeroo_filadhu == "Hardha":
                df_filtered = df[df['Yeroo'].dt.date == now.date()]
            elif yeroo_filadhu == "Torban Kana":
                df_filtered = df[df['Yeroo'] >= (now - timedelta(days=7))]
            elif yeroo_filadhu == "Ji'a Kana":
                df_filtered = df[df['Yeroo'].dt.month == now.month]
            elif yeroo_filadhu == "Kurmaana (3 Mo)":
                df_filtered = df[df['Yeroo'] >= (now - timedelta(days=90))]
            elif yeroo_filadhu == "Waggaa Kana":
                df_filtered = df[df['Yeroo'].dt.year == now.year]
            else:
                df_filtered = df

            st.dataframe(df_filtered, use_container_width=True)

            if st.button("🚀 GABAASA FILATAME TELEGRAM-ITTI ERGI"):
                total_cust = len(df_filtered)
                total_money = df_filtered['Kafaltii'].sum()
                
                msg = (f"📊 *Gabaasa Waajjira Lafaa Dadar ({yeroo_filadhu})*\n\n"
                       f"👤 Baay'ina Abbootii Dhimmaa: `{total_cust}`\n"
                       f"💰 Galii Waligalaa: *{total_money

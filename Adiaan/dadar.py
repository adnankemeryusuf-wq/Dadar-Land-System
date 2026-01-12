import streamlit as st
import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA BU'URAA ---
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
    .stApp { background-color: #f8fafc; }
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

# --- 3. SEENSA (LOGIN) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>Login - Dadar Land</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    # --- 4. NAVIGATION ---
    with st.sidebar:
        st.title("Dadar Land")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Telegram"]
        choice = st.selectbox("Menu", menu)
        st.divider()
        st.info(f"📅 Hardha: {datetime.now().strftime('%Y-%m-%d')}")

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    # --- 5. PAGES ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Bilbila', 'Gosa', 'Ogeessa', 'Lakk_Galmee', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><h4>👥 Abbootii Dhimmaa</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><h4>💰 Galii Waligalaa</h4><h2>{df["Kafaltii"].sum():,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><h4>✅ Status</h4><h2>Hojirra Jira</h2></div>', unsafe_allow_html=True)
            
            st.subheader("🕒 Galmeewwan Dhiyoo")
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.warning("Ragaan galmaa'e hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        with st.form("form_galmee", clear_on_submit=True):
            st.subheader("Ragaa Abbaa Dhimmaa Galmeessi")
            c1, c2 = st.columns(2)
            with c1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                qx = st.text_input("Qaxana / Lakkoofsa")
                bl = st.text_input("Lakkoofsa Bilbilaa")
            with c2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Ground", "Gibira"])
                og = st.text_input("Maqaa Ogeessa Tajaajila Kennu")
                lk = st.text_input("Lakkoofsa Kenniinsa Tajaajilaa")
                k_wal = st.number_input("Kafaltii Waligalaa (ETB)", min_value=0.0)
            
            if st.form_submit_button("✅ GALMEE MIRKANEEESSI"):
                if ad and ar:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Ragaa walitti qindeessu
                    line = f"{now}|{ad}|{ar}|{qx}|{bl}|{gs}|{og}|{lk}|Hardha|0|0|0|{k_wal}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f:
                        f.write(line)
                    st.success(f"Ragaan '{ad}' milkiin galmaa'era!")
                    st.balloons()
                else:
                    st.error("Maaloo ragaalee barbaachisoo guuti!")

    elif choice == "📊 Gabaasa & Telegram":
        st.subheader("To'annoo Gabaasaa (Filter)")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Bilbila', 'Gosa', 'Ogeessa', 'Lakk_Galmee', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Yeroo'] = pd.to_datetime(df['Yeroo'])
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)

            # Filter Menu
            yeroo_filadhu = st.radio("Yeroo Gabaasaa Filadhu:", 
                                     ["Hunda", "Hardha", "Torban", "Ji'a", "Kurmaana", "Waggaa"], 
                                     horizontal=True)
            
            now = datetime.now()
            if yeroo_filadhu == "Hardha":
                df_f = df[df['Yeroo'].dt.date == now.date()]
            elif yeroo_filadhu == "Torban":
                df_f = df[df['Yeroo'] >= (now - timedelta(days=7))]
            elif yeroo_filadhu == "Ji'a":
                df_f = df[df['Yeroo'].dt.month == now.month]
            elif yeroo_filadhu == "Kurmaana":
                df_f = df[df['Yeroo'] >= (now - timedelta(days=90))]
            elif yeroo_filadhu == "Waggaa":
                df_f = df[df['Yeroo'].dt.year == now.year]
            else:
                df_f = df

            st.dataframe(df_f, use_container_width=True)
            
            if st.button("🚀 GABAASA TELEGRAM-ITTI ERGI"):
                t_cust = len(df_f)
                t_money = df_f['Kafaltii'].sum()
                
                # Ergaa Telegram (Syntax Error sirreeffameera)
                msg = (f"📊 *Gabaasa Waajjira Lafaa Dadar*\n"
                       f"━━━━━━━━━━━━━━━━━━\n"
                       f"📅 Yeroo: *{yeroo_filadhu}*\n"
                       f"👤 Abbootii Dhimmaa: `{t_cust}`\n"
                       f"💰 Galii Waligalaa: *{t_money:,.2f} ETB*\n"
                       f"━━━━━━━━━━━━━━━━━━\n"
                       f"📅 Guyyaa Ergame: {now.strftime('%Y-%m-%d')}")
                
                send_telegram_msg(msg)
                st.success(f"Gabaasni ({yeroo_filadhu}) gara Telegram-itti ergameera!")
                
    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

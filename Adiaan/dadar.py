import streamlit as st
import os
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- CONFIG ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

USER_NAME = "Lafa2026"
PASS_WORD = "Dadar@2026"
DATA_FILE = "dadar_final_report.txt"

# --- TELEGRAM CONFIG (Bakka kana jijjiiri) ---
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI" 
TELEGRAM_CHAT_ID = "7329587700"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Telegram-itti erguun hin danda'amne: {e}")

# --- CSS STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    .header-box { 
        text-align: center; padding: 30px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #15803d 100%); 
        color: white; border-radius: 20px; margin-bottom: 25px;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #15803d;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP LOGIC ---
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
    # Sidebar
    with st.sidebar:
        st.title("Dadar Land")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Telegram"]
        choice = st.selectbox("Menu", menu)

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df[12] = pd.to_numeric(df[12], errors='coerce').fillna(0)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><h4>👥 Abbootii Dhimmaa</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><h4>💰 Galii</h4><h2>{df[12].sum():,.2f}</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><h4>✅ Status</h4><h2>Active</h2></div>', unsafe_allow_html=True)
            
            st.subheader("Galmeewwan Dhiyoo")
            st.dataframe(df.tail(10), use_container_width=True)

    elif choice == "📝 Galmee Haaraa":
        with st.form("form"):
            st.subheader("Ragaa Galmeessi")
            c1, c2 = st.columns(2)
            with c1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
            with c2:
                # "Ground" ashaaraa keetti dabalameera
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Ground", "Gibira"])
                k_wal = st.number_input("Kafaltii", min_value=0.0)
            
            if st.form_submit_button("GALMEESSI"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                line = f"{now}|{ad}|{ar}|-| - |{gs}|-| - |Hardha|0|0|0|{k_wal}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(line)
                st.success("Galmaa'eera!")

    elif choice == "📊 Gabaasa & Telegram":
        st.subheader("Gabaasa Maalaqaa fi Hojii")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df[12] = pd.to_numeric(df[12], errors='coerce').fillna(0)
            
            st.dataframe(df)
            
            if st.button("🚀 GABAASA TELEGRAM-ITTI ERGI"):
                total_cust = len(df)
                total_money = df[12].sum()
                ground_count = len(df[df[5] == "Ground"])
                
                msg = (f"📊 *Gabaasa Waajjira Lafaa Dadar*\n\n"
                       f"👤 Baay'ina Abbootii Dhimmaa: {total_cust}\n"
                       f"🏗️ Tajaajila Ground: {ground_count}\n"
                       f"💰 Galii Waligalaa: {total_money:,.2f} ETB\n"
                       f"📅 Guyyaa: {datetime.now().strftime('%Y-%m-%d')}")
                
                send_telegram_msg(msg)
                st.success("Gabaasni gara Telegram-itti ergameera!")


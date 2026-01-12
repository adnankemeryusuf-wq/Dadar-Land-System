import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

# Constants (Missing in your original code)
USER_NAME, PASS_WORD = "admin", "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "logo.png"
DB_FILE = "dadar_database.txt" # File ragaan itti kuufamu
SMS_TOKEN = "YOUR_SMS_TOKEN_HERE" # Token kee as galchi
TRACCAR_URL = "http://YOUR_SMS_GATEWAY_URL" # URL SMS kee

# --- 2. HELPER FUNCTIONS ---

def load_data():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    data_list = []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                # Seeraan addaan baasuu
                parts = [x.split(":")[1].strip() for x in line.split("|") if ":" in x]
                # Column 15 (Kafaltiiwwan hunda dabalatee)
                if len(parts) == 15:  
                    data_list.append(parts)
            except: continue
    cols = ["ID", "Guyyaa", "Maqaa", "Bilbila", "Araddaa", "Wirtuu", "Dhimma", 
            "Itti_Fay", "Kartaa", "J_Maqaa", "Lizi", "TOT", "Biro", "Beellama", "Ogeessa", "Status"]
    # Column-oonni koodii kee wajjiin akka walsimuuf (16 columns total with status)
    return pd.DataFrame(data_list, columns=cols[:15] + ["Status"])

def send_ethio_sms(bilbila, ergaa):
    if not bilbila: return False
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
    .metric-card { background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #1f4e78; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col2, _ = st.columns([1, 1, 1])
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
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = st.radio("HOJJEDHU", ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa & Telegram", "🚪 Logout"])
        st.divider()
        st.info(f"Version: 8.1\nAdmin: {USER_NAME}")

import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime, timedelta
from fpdf import FPDF

# ================= 1. TELEGRAM CONFIG =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except:
        pass

# ================= 2. CORE FUNCTIONS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Guyyaa'] = pd.to_datetime(df['Guyyaa'], dayfirst=True)
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

# ================= 3. APP NAVIGATION =================
df = load_data()

with st.sidebar:
    st.header("🏢 DADAR ADMIN")
    menu = st.radio("FILANNOO:", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "📄 Clearance", "📤 Gabaasa Ergi", "🚪 Logout"])

# --- 1. BARBAADI (SEARCH ONLY) ---
if menu == "🔍 Barbaadi":
    st.title("🔍 Barbaadi")
    q = st.text_input("Maqaa maamilaa galchi...")
    if q and not df.empty:
        res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
        st.table(res)

# --- 2. CLEARANCE (WARAQAA QULQULLUMMAA) ---
elif menu == "📄 Clearance":
    st.title("📄 Waraqaa Qulqullummaa")
    name_search = st.text_input("Maqaa maamilaa ragaa barbaaduufii galchi...")
    if name_search and not df.empty:
        res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(name_search, case=False, na=False)]
        for idx, row in res.iterrows():
            with st.expander(f"Ragaa {row['Maqaa_Abbaa_Dhimmaa']}"):
                st.write(f"Tajaajila: {row['Gosa_Tajajjilaa']} | Kaffaltii: {row['Kafaltii_Taj']} ETB")
                if st.button(f"PDF Uumi ({idx})"):
                    st.success("Waraqaan Qulqullummaa qopha'eera (Buufadhu).")

# --- 3. GABAASA TELEGRAM (GUYYAA, TORBEE, JI'A, WAGGAA) ---
elif menu == "📤 Gabaasa Ergi":
    st.title("📤 Gabaasa Telegramitti Ergi")
    g_type = st.selectbox("Gosa Gabaasaa:", ["Guyyaa", "Torbee", "Ji'a", "Kurmaana", "Waggaa"])
    
    if st.button("🚀 Gabaasa Gara Telegram Ergi"):
        now = datetime.now()
        if g_type == "Guyyaa":
            filtered = df[df['Guyyaa'].dt.date == now.date()]
        elif g_type == "Torbee":
            filtered = df[df['Guyyaa'] > (now - timedelta(days=7))]
        elif g_type == "Ji'a":
            filtered = df[df['Guyyaa'].dt.month == now.month]
        elif g_type == "Kurmaana":
            filtered = df[df['Guyyaa'].dt.month.isin([(now.month-1)//3*3+i for i in range(1,4)])]
        else: # Waggaa
            filtered = df[df['Guyyaa'].dt.year == now.year]

        total_galii = filtered['Kafaltii_Taj'].sum()
        total_count = len(filtered)
        
        report_msg = (f"📊 GABAASA {g_type.upper()}\n"
                      f"📅 Guyyaa: {now.strftime('%d/%m/%Y')}\n"
                      f"👥 Waliigala Maamiltoota: {total_count}\n"
                      f"💰 Waliigala Galii: {total_galii:,.2f} ETB\n"
                      f"🏢 Wajjira Lafa Dadar")
        
        send_telegram_msg(report_msg)
        st.success(f"Gabaasni {g_type} Telegram irratti ergameera!")

# --- 4. DASHBOARD & REGISTRATION (Koodii kee duraanii itti fufa...) ---

import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

# ================= 1. CONFIGURATION =================
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 2. TELEGRAM FUNCTIONS =================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"}
        requests.get(url, params=params)
    except Exception as e:
        st.error(f"Telegram error: {e}")

# ================= 3. DATA FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

# ================= 4. UI SETTINGS =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if st.session_state.logged_in:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa"])

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard & Telegram Report")
        
        # Filter for today's data
        today_str = datetime.now().strftime('%d/%m/%Y')
        today_df = df[df['Guyyaa'] == today_str]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Guyyaa Har'aa", f"{today_df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota Har'aa", len(today_df))
        c3.metric("👷 Ogeeyyii Hojjetan", today_df['Maqaa_Ogeessa'].nunique())

        st.divider()
        
        # --- TELEGRAM DAILY REPORT BUTTON ---
        st.subheader("📤 Gabaasa Guyyaa Telegramitti Ergi")
        if st.button("🚀 Gabaasa Har'aa Ergi"):
            if not today_df.empty:
                total_income = today_df['Kafaltii_Taj'].sum()
                customer_count = len(today_df)
                
                # Format message
                report_msg = (
                    f"📅 *GABAASA GUYYAA: {today_str}*\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 *Waliigala Galii:* {total_income:,.2f} ETB\n"
                    f"👥 *Baay'ina Maamilaa:* {customer_count}\n"
                    f"👷 *Ogeeyyii Hojjetan:* {today_df['Maqaa_Ogeessa'].nunique()}\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ Gabaasni kun ofumaan ergame."
                )
                send_telegram(report_msg)
                st.success("✅ Gabaasni guyyaa Telegram irratti ergameera!")
            else:
                st.warning("Har'a ragaan galmeeffame hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        # (Koodii kee isa duraanii itti fufa...)
        st.title("📝 Galmee Tajaajilaa")
        with st.form("reg_form"):
            name = st.text_input("Maqaa Abbaa Dhimmaa")
            og = st.text_input("Ogeessa")
            fee = st.number_input("Kaffaltii", min_value=0.0)
            submit = st.form_submit_button("Galmeessi")
            
            if submit and name and og:
                # Save and Send Instant Notification
                msg = f"🆕 *Galmee Haaraa*\n👤 Maamila: {name}\n💵 Kaffaltii: {fee} ETB\n👷 Ogeessa: {og}"
                send_telegram(msg)
                st.success("Galmeeffameera!")

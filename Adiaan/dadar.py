import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ================= TELEGRAM CONFIG =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

def send_telegram(msg):
    """Ergaa gabaabaa fi gabaasa guyyaa erguuf"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID_MANAGER, 
            "text": msg, 
            "parse_mode": "Markdown"
        }
        requests.get(url, params=params)
    except Exception as e:
        print(f"Error: {e}")

# ================= 1. ERGAA BATTALAA (INSTANT) =================
# Yeroo ati 'Galmeessi' cuqaastu kana fayyadama
def report_new_entry(name, service, fee, officer):
    msg = (
        f"🆕 *GALMEE HAARAA*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Maamila:* {name}\n"
        f"🛠 *Tajaajila:* {service}\n"
        f"💰 *Kaffaltii:* {fee:,.2f} ETB\n"
        f"👷 *Ogeessa:* {officer}\n"
        f"📅 *Guyyaa:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )
    send_telegram(msg)

# ================= 2. GABAASA GUYYAA (DAILY SUMMARY) =================
# Dashboard irratti button cuqaasamuun gabaasa kana erga
def report_daily_summary(df):
    today = datetime.now().strftime('%d/%m/%Y')
    today_df = df[df['Guyyaa'] == today]
    
    if not today_df.empty:
        total_income = today_df['Kafaltii_Taj'].sum()
        count = len(today_df)
        top_service = today_df['Gosa_Tajajjilaa'].mode()[0]
        
        msg = (
            f"📊 *GABAASA GUYYAA ({today})*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Waliigala Galii:* {total_income:,.2f} ETB\n"
            f"👥 *Baay'ina Maamilaa:* {count}\n"
            f"🔝 *Tajaajila Baay'ate:* {top_service}\n"
            f"👷 *Ogeeyyii Hojjetan:* {today_df['Maqaa_Ogeessa'].nunique()}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🏢 _Wajjira Lafa Magaalaa Dadar_"
        )
        send_telegram(msg)
        return True
    return False

# ================= STREAMLIT UI INTEGRATION =================
# Menu Dashboard keessatti:
if st.button("🚀 Gabaasa Har'aa Telegramitti Ergi"):
    if report_daily_summary(df):
        st.success("Gabaasni Guyyaa Manager-iif ergameera!")
    else:
        st.warning("Har'a ragaan galmeeffame hin jiru.")

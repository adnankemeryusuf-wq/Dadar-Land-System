import streamlit as st
import pandas as pd
import os, io, requests
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
LOGO_FILE = "logo_waajjiraa.png"

# TELEGRAM CONFIG (TOKEN KEE FI ID KEE)
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

# ================= 2. CORE FUNCTIONS =================

def load_data():
    COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Nagahee_Img']
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(df):
    """Excel uumee Telegram-atti erga"""
    try:
        # Excel gara memory-tti jijjiiruu
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Gabaasa_Dadar')
        output.seek(0)

        # Telegram API waamuu
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        files = {'document': ('Gabaasa_Lafa_Dadar.xlsx', output, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        payload = {'chat_id': CHAT_ID_MANAGER, 'caption': f"📊 Gabaasa Hojii Waajjira Lafaa Magaalaa Dadar\nGuyyaa: {datetime.now().strftime('%d/%m/%Y')}"}
        
        response = requests.post(url, data=payload, files=files)
        return response.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Section
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026": 
            st.session_state.logged_in = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📜 CLEARANCE", "📈 Gabaasa", "Ba'i"])

    # --- KUTAA GABAASAA (TELEGRAM INTEGRATION) ---
    if menu == "📈 Gabaasa":
        st.header("📋 Gabaasa Galmeewwan Hundi")
        
        if not df.empty:
            # Table mul'isuu
            st.dataframe(df.drop(columns=['Nagahee_Img']), use_container_width=True)
            
            st.divider()
            c1, c2 = st.columns([1, 1])
            
            # Button 1: Excel Buufachuuf (Local)
            csv = df.to_csv(index=False).encode('utf-8')
            c1.download_button("📥 Excel Local Buufadhu", csv, "Gabaasa.csv", "text/csv")
            
            # Button 2: Telegram-atti Erguuf
            if c2.button("📤 Gabaasa Telegram-atti Ergi", type="primary"):
                with st.spinner("Gabaasni ergamaa jira..."):
                    res = send_to_telegram(df)
                    if res.get("ok"):
                        st.success("✅ Excel'n gara Telegram-atti milka'inaan ergameera!")
                    else:
                        st.error(f"❌ Rakkoon uumame: {res.get('description')}")
        else:
            st.info("Data'n galmeeffame hin jiru.")

    # --- DASHBOARD & OTHERS ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            st.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            fig = px.bar(df, x='Guyyaa', y='Kafaltii_Taj', title="Raawwii Galii")
            st.plotly_chart(fig, use_container_width=True)

    # (Kutaaleen Galmee Haaraa fi Clearance akkuma duraatti itti fufu...)
    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

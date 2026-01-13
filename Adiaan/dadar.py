import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime

# --- CONFIGURATION TELEGRAM ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div[data-baseweb="multiselect"] { border: 2px solid #2e7d32 !important; background-color: #ffffff !important; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
WEEKDAY_MAP = {0: "Wixata", 1: "Filatama", 2: "Roobii", 3: "Kamisa", 4: "Jimmata", 5: "Sanbata", 6: "Dilbata"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    # Guyyaa gara format datetime tti jijjiiruuf
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a_Lakk'] = df['Date_Obj'].dt.month
    df['Ji\'a'] = df['Ji\'a_Lakk'].map(MONTH_MAP)
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
    df['Guyyaa_Torbee'] = df['Date_Obj'].dt.dayofweek.map(WEEKDAY_MAP)
    # Kurmaana (Ethiopian Fiscal Year context: Q1 start Sept)
    df['Kurmaana'] = df['Ji\'a_Lakk'].apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try:
        response = requests.post(url, files=files, data=data)
        return response.status_code == 200
    except: return False

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi", "Ba'i"])

    df = load_data()

    if menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Calalame")
        if not df.empty:
            st.sidebar.markdown("### 🔍 Calaltuu Filadhu")
            f_type = st.sidebar.radio("Gosa Gabaasaa:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa"])
            
            sel_year = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].unique(), reverse=True))
            filtered_df = df[df['Waggaa'] == sel_year]

            if f_type == "Kurmaana":
                sel_q = st.sidebar.selectbox("Kurmaana (Q)", [1, 2, 3, 4])
                filtered_df = filtered_df[filtered_df['Kurmaana'] == sel_q]
            elif f_type == "Ji'a":
                sel_m = st.sidebar.selectbox("Ji'a", list(MONTH_MAP.values()))
                filtered_df = filtered_df[filtered_df['Ji\'a'] == sel_m]
            elif f_type == "Torbee":
                sel_m = st.sidebar.selectbox("Ji'a", list(MONTH_MAP.values()))
                sel_w = st.sidebar.selectbox("Torbee", [1, 2, 3, 4])
                filtered_df = filtered_df[(filtered_df['Ji\'a'] == sel_m) & (filtered_df['Torbee'] == sel_w)]
            elif f_type == "Guyyaa":
                sel_d = st.sidebar.selectbox("Guyyaa Torbee", ["Wixata", "Filatama", "Roobii", "Kamisa", "Jimmata"])
                filtered_df = filtered_df[filtered_df['Guyyaa_Torbee'] == sel_d]

            st.dataframe(filtered_df[COL_NAMES], use_container_width=True)
            total_income = filtered_df['Kafaltii_Taj'].sum()
            st.metric(f"Waliigala Galii ({f_type})", f"{total_income:,.2f} ETB")

            # EXCEL
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                filtered_df[COL_NAMES].to_excel(writer, index=False, sheet_name='Report')
            
            file_name = f"Gabaasa_{f_type}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            st.divider()
            c1, c2 = st.columns(2)
            with c1: st.download_button("📥 Excel Buufadhu", buffer.getvalue(), file_name=file_name)
            with c2:
                if st.button("✈️ Telegram-itti Ergi"):
                    caption = f"📊 Gabaasa {f_type}\n💰 Galii: {total_income:,.2f} ETB\n📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}"
                    if send_to_telegram(buffer.getvalue(), file_name, caption): st.success("Ergameera!")
                    else: st.error("Hin ergamne!")
        else: st.info("Data'n hin jiru.")

    # (Menu-wwan biroo akkuma kanaan duraatti itti fufu...)
    elif menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Haaraa Galmeessi")
        # (Koodiin galmee haaraa asitti itti fufa...)

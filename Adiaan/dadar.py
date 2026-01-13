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
    div.stForm { background: rgba(255, 255, 255, 0.9); border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def send_to_telegram(file_data, file_name):
    """File Excel kallaattiin gara Telegram itti gaafatamaatti erga"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': f"📊 Gabaasa Haaraa: {file_name}\nGuyyaa: {datetime.now().strftime('%d/%m/%Y')}"}
    try:
        response = requests.post(url, f_files=files, data=data)
        return response.status_code == 200
    except:
        return False

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "Ba'i"])

    df = load_data()

    if menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Itti Gaafatamaatti Ergi")
        if not df.empty:
            df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y')
            df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
            
            sel_month = st.selectbox("Ji'a Filadhu", list(MONTH_MAP.values()))
            filtered_df = df[df['Ji\'a'] == sel_month]
            
            st.dataframe(filtered_df[COL_NAMES], use_container_width=True)
            
            # EXCEL EXPORT
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                filtered_df[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            
            file_name = f"Gabaasa_{sel_month}_{datetime.now().strftime('%Y%m%d')}.xlsx"

            st.divider()
            if st.button("✈️ Gabaasa Kana Gara Telegram Hoggansaatti Ergi"):
                with st.spinner("Ergamaa jira..."):
                    success = send_to_telegram(buffer.getvalue(), file_name)
                    if success:
                        st.success("✅ Gabaasni kallaattiin itti gaafatamaatti ergameera!")
                    else:
                        st.error("❌ Erguun hin danda'amne. Bot Token ykn Chat ID kee sirri ta'uu mirkaneeffadhu.")
        else:
            st.info("Data'n hin jiru.")

    # ... (Dashboard fi Galmee Haaraa akkuma duraatti itti fufa)

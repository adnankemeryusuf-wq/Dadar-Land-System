import streamlit as st
import pandas as pd
import os
import hashlib
import requests
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw

# ================= 1. CONFIG & STYLE =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom right, #f8fafc, #e2e8f0); }
    [data-testid="stSidebar"] { background-color: #1e293b !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    div[data-testid="metric-container"] {
        background-color: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #3b82f6;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
TELEGRAM_TOKEN = "7864321234:AAH_F_XXXXXXXXXXXXX" # API Token galchi
TELEGRAM_CHAT_ID = "123456789"                   # Chat ID galchi

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Ittii Fayyaddam": 50.0, "Kartaa": 150.0, "Jijjirra Maqaa": 200.0,
    "Dhimma Dangaa": 100.0, "Dhimma Mana Murtii": 0.0, "Ugura Mana Murtii": 50.0,
    "Uguraa Mana Murtii Kasuu": 50.0, "Dorkka Liqii Bankii": 100.0, "Dorkkaa Liqii Bankii Kasuu": 100.0
}

# ================= 3. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_telegram_file(file_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"document": file})
            return True
    except: return False

def create_pdf_report(df, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Gabaasa Tajaajila Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(30, 10, "Guyyaa", 1, 0, 'C', True)
    pdf.cell(50, 10, "Maqaa", 1, 0, 'C', True)
    pdf.cell(70, 10, "Gosa Tajaajilaa", 1, 0, 'C', True)
    pdf.cell(30, 10, "Kafaltii", 1, 1, 'C', True)
    
    for _, row in df.iterrows():
        pdf.cell(30, 10, str(row['Yeroo']), 1)
        pdf.cell(50, 10, str(row['Maqaa'])[:20], 1)
        pdf.cell(70, 10, str(row['Gosa']), 1)
        pdf.cell(30, 10, f"{row['Kafaltii_Taj']}", 1, 1)
    
    pdf.output(filename)

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.title("🏢 Login")
        u, p = st.text_input("User"), st.text_input("Pass", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
else:
    with st.sidebar:
        st.header("🏢 Dadar Land")
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee", "🔍 Sirreessi", "📤 Gabaasa Ergi", "Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        c1, c2 = st.columns(2)
        c1.metric("Baay'ina", len(df))
        total = df['Kafaltii_Taj'].sum() if not df.empty else 0
        c2.metric("Kafaltii Waliigalaa", f"{total} ETB")
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("entry"):
            m = st.text_input("Maqaa Abbaa Dhimmaa")
            g = st.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            o = st.text_input("Maqaa Ogeessaa")
            add_fee = st.number_input("Kafaltii Dabalataa (yoo jiraate)", min_value=0.0, value=0.0)
            
            base_fee = GATII_DICT[g]
            total_fee = base_fee + add_fee
            st.info(f"💰 Kafaltii Waliigalaa: {total_fee} ETB")
            
            if st.form_submit_button("💾 Galmeessi"):
                new = [datetime.now().strftime('%d/%m/%Y'), m, "N/A", "N/A", g, o, total_fee]
                df.loc[len(df)] = new
                save_data(df)
                st.success("Galmeeffameera!")

    elif menu == "🔍 Sirreessi":
        st.header("🔍 Sirreessi ykn Haqi")
        q = st.text_input("Maqaa barbaadi...")
        if not df.empty:
            search = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            for idx, row in search.iterrows():
                with st.expander(f"👤 {row['Maqaa']}"):
                    new_m = st.text_input("Maqaa", row['Maqaa'], key=f"m_{idx}")
                    if st.button("Save", key=f"s_{idx}"):
                        df.at[idx, 'Maqaa'] = new_m
                        save_data(df); st.rerun()
                    if st.button("Delete", key=f"d_{idx}"):
                        df = df.drop(idx)
                        save_data(df); st.rerun()

    elif menu == "📤 Gabaasa Ergi":
        st.header("📤 Gabaasa Telegram-itti Ergi")
        if not df.empty:
            c1, c2 = st.columns(2)
            if c1.button("📤 Excel Ergi (Telegram)"):
                df.to_excel("Gabaasa.xlsx", index=False)
                if send_telegram_file("Gabaasa.xlsx", "Gabaasa Excel Magaalaa Dadar"):
                    st.success("Excel Ergameera!")
            
            if c2.button("📤 PDF Ergi (Telegram)"):
                create_pdf_report(df, "Gabaasa.pdf")
                if send_telegram_file("Gabaasa.pdf", "Gabaasa PDF Magaalaa Dadar"):
                    st.success("PDF Ergameera!")
        else: st.warning("Data'n hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

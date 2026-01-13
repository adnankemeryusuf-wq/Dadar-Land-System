import streamlit as st
import pandas as pd
import os
import hashlib
import requests
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageOps
import io

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom right, #f0f2f6, #e0e5ec); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    div[data-testid="metric-container"] {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); border-top: 4px solid #3b82f6;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
# ================= 2. DATA SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
# Telegram API Credentials (Asitti galchi)
TELEGRAM_TOKEN = "7864321234:AAH_F_XXXXXXXXXXXXX" 
TELEGRAM_CHAT_ID = "123456789"

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {"Gibira":50.0,
    "Ittii Fayyaddam": 50.0, "Kartaa": 150.0, "Jijjirra Maqaa": 200.0,
    "Dhimma Dangaa": 100.0, "Dhimma Mana Murtii": 0.0, "Ugura Mana Murtii": 50.0,
    "Uguraa Mana Murtii Kasuu": 50.0, "Dorkka Liqii Bankii": 100.0, "Dorkkaa Liqii Bankii Kasuu": 100.0,
"Kan Biro": 100.0}

# ================= 3. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"document": file})
            return True
    except: return False

def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Gabaasa Tajaajila Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
    pdf.ln(10)
    
    # Header
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
    
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<h1 style='text-align: center;'>🏢 Dadar Land</h1>", unsafe_allow_html=True)
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("Seeni", use_container_width=True):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
else:
    with st.sidebar:
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Sirreessi", "📤 Gabaasa Ergi", "🏆 Sartiifiketa", "Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("Baay'ina", len(df))
        total = df['Kafaltii_Taj'].astype(float).sum() if not df.empty else 0
        c2.metric("Kafaltii Waliigalaa", f"{total} ETB")
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("entry_form"):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            gosa = st.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            ogeessa = st.text_input("Maqaa Ogeessaa")
            add_fee = st.number_input("Kafaltii Dabalataa (yoo jiraate)", min_value=0.0)
            
            total_fee = GATII_DICT[gosa] + add_fee
            st.info(f"💰 Kafaltii Waliigalaa: **{total_fee} ETB**")
            
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, "N/A", "N/A", gosa, ogeessa, total_fee]
                df.loc[len(df)] = new_row
                save_data(df)
                st.success("✅ Galmeeffameera!")

    elif menu == "🔍 Barbaadi & Sirreessi":
        st.header("🔍 Barbaadi & Sirreessi")
        q = st.text_input("Maqaa...")
        if not df.empty:
            search_df = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            for idx, row in search_df.iterrows():
                with st.expander(f"👤 {row['Maqaa']}"):
                    n_maqaa = st.text_input("Maqaa", row['Maqaa'], key=f"n_{idx}")
                    if st.button("Save", key=f"s_{idx}"):
                        df.at[idx, 'Maqaa'] = n_maqaa
                        save_data(df); st.rerun()
                    if st.button("Delete", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    elif menu == "📤 Gabaasa Ergi":
        st.header("📤 Gabaasa Telegram-itti Ergi")
        if not df.empty:
            col1, col2 = st.columns(2)
            if col1.button("📤 Excel Ergi"):
                df.to_excel("Gabaasa.xlsx", index=False)
                if send_to_telegram("Gabaasa.xlsx", "Gabaasa Excel Dadar"):
                    st.success("Excel Ergameera!")
            
            if col2.button("📤 PDF Ergi"):
                pdf_data = generate_pdf_report(df)
                with open("Gabaasa.pdf", "wb") as f: f.write(pdf_data)
                if send_to_telegram("Gabaasa.pdf", "Gabaasa PDF Dadar"):
                    st.success("PDF Ergameera!")

    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Sartiifiketa")
        if not df.empty:
            og = st.selectbox("Ogeessa", df['Ogeessa'].unique())
            if st.button("📜 PDF Qopheessi"):
                # (Same generate_certificate function logic)
                st.info("Qophaa'aa jira...")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()



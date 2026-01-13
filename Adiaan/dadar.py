import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# Logo Path
LOGO_PATH = "logo.png"

st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom right, #f8fafc, #e2e8f0); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    div[data-testid="metric-container"] {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-top: 5px solid #3b82f6;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; height: 3em; background-color: #2563eb; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
TELEGRAM_TOKEN = "7864321234:AAH_F_XXXXXXXXXXXXX" 
TELEGRAM_CHAT_ID = "123456789"

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira Bara Kanaa": 100.0,
    "Ittii Fayyaddam": 50.0,
    "Kartaa": 150.0,
    "Jijjirra Maqaa": {"Jijjirraa": 200.0, "Lizii Duraa": 500.0, "TOT": 100.0},
    "Dhimma Dangaa": 100.0,
    "Dhimma Mana Murtii": 0.0,
    "Ugura Mana Murtii": 50.0,
    "Uguraa Mana Murtii Kasuu": 50.0,
    "Dorkka Liqii Bankii": 100.0,
    "Dorkkaa Liqii Bankii Kasuu": 100.0
}

# ================= 3. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"document": file})
            return True
    except: return False

def generate_certificate(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # Border
    pdf.set_line_width(3); pdf.set_draw_color(184, 134, 11); pdf.rect(10, 10, 277, 190) 
    
    # Logo on Certificate
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=135, y=15, w=30)
    
    pdf.ln(40)
    pdf.set_font('Arial', 'B', 40); pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 30); pdf.set_text_color(185, 28, 28)
    pdf.cell(0, 20, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 18); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, "Tajaajila qulqulluu fi saffisaa tajaajilamtootaaf kennaa turaniif beekamtii kana kennineefirra.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        st.markdown("<h2 style='text-align: center;'>Dadar Land Admin</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    # --- SIDEBAR WITH LOGO ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
        st.markdown(f"### 👤 {st.session_state.user}")
        st.divider()
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Sirreessi", "📤 Gabaasa Ergi", "🏆 Sartiifiketa", "Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("Baay'ina", len(df))
        total = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').sum() if not df.empty else 0
        c2.metric("Waliigala (ETB)", f"{total}")
        st.divider()
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            gosa = col2.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            
            if gosa == "Jijjirra Maqaa":
                d = GATII_DICT["Jijjirra Maqaa"]
                base_fee = d["Jijjirraa"] + d["Lizii Duraa"] + d["TOT"]
                st.warning(f"💡 Breakdown: Jijjirraa({d['Jijjirraa']}) + Lizii({d['Lizii Duraa']}) + TOT({d['TOT']}) = {base_fee}")
            else:
                base_fee = GATII_DICT[gosa]

            total_fee = base_fee + st.number_input("Kafaltii Dabalataa", min_value=0.0)
            st.info(f"💰 Waliigala: {total_fee} ETB")
            
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, total_fee]
                df.loc[len(df)] = new_row
                save_data(df); st.success("✅ Galmeeffameera!")

    elif menu == "🔍 Barbaadi & Sirreessi":
        st.header("🔍 Barbaadi & Sirreessi")
        q = st.text_input("Maqaa...")
        if not df.empty:
            search = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            for idx, row in search.iterrows():
                with st.expander(f"👤 {row['Maqaa']}"):
                    n_maqaa = st.text_input("Maqaa", row['Maqaa'], key=f"n_{idx}")
                    if st.button("Save", key=f"s_{idx}"):
                        df.at[idx, 'Maqaa'] = n_maqaa
                        save_data(df); st.rerun()

    elif menu == "📤 Gabaasa Ergi":
        st.header("📤 Telegram-itti Ergi")
        if st.button("📤 Excel Ergi"):
            file_name = "Gabaasa_Dadar.xlsx"
            df.to_excel(file_name, index=False)
            send_to_telegram(file_name, "Gabaasa Dadar"); st.success("Ergameera!")

    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Sartiifiketa")
        if not df.empty:
            og = st.selectbox("Ogeessa", df['Ogeessa'].unique())
            if st.button("📜 PDF Qopheessi"):
                pdf = generate_certificate(og)
                st.download_button("📥 Buufadhu", pdf, f"Sartii_{og}.pdf")

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

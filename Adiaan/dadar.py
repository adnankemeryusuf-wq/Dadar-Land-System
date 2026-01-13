import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
import io

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

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
# Telegram Credentials - TOKEN fi ID kee asitti galchi
TELEGRAM_TOKEN = "7864321234:AAH_F_XXXXXXXXXXXXX" 
TELEGRAM_CHAT_ID = "123456789"

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

# Gosa Tajaajilaa fi Herrega Kaffaltii
GATII_DICT = {
    "Gibira Bara Kanaa": 100.0,
    "Ittii Fayyaddam": 50.0,
    "Kartaa": 150.0,
    "Jijjirra Maqaa": {
        "Jijjirraa": 200.0,
        "Lizii Duraa": 500.0,
        "TOT": 100.0
    },
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
    except:
        return False

def generate_certificate(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(3); pdf.set_draw_color(184, 134, 11); pdf.rect(10, 10, 277, 190) 
    pdf.ln(30); pdf.set_font('Arial', 'B', 40); pdf.set_text_color(30, 64, 175)
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
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>🏢 Dadar Land Admin</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Dogoggora!")
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        st.divider()
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Sirreessi", "📤 Gabaasa Ergi", "🏆 Sartiifiketa", "Ba'i"])

    df = load_data()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Gabaasa Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("Baay'ina Tajaajilaa", len(df))
        if not df.empty:
            total_money = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').sum()
        else:
            total_money = 0
        c2.metric("Kafaltii Waliigalaa", f"{total_money} ETB")
        c3.metric("Ogeessota", len(df['Ogeessa'].unique()) if not df.empty else 0)
        st.divider()
        st.dataframe(df, use_container_width=True)

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            gosa = col2.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            
            # Herrega Jijjirraa Maqaa (Breakdown)
            if gosa == "Jijjirra Maqaa":
                d = GATII_DICT["Jijjirra Maqaa"]
                base_fee = d["Jijjirraa"] + d["Lizii Duraa"] + d["TOT"]
                st.warning(f"Breakdown: Jijjirraa({d['Jijjirraa']}) + Lizii({d['Lizii Duraa']}) + TOT({d['TOT']}) = {base_fee} ETB")
            else:
                base_fee = GATII_DICT[gosa]

            extra = st.number_input("Kafaltii Dabalataa (yoo jiraate)", min_value=0.0)
            total_fee = base_fee + extra
            st.info(f"💰 Kafaltii Waliigalaa: **{total_fee} ETB**")
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, total_fee]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success("Galmeeffameera!")
                else:
                    st.error("Maqaa fi Ogeessa guuti!")

    # --- BARBAADI & SIRREESSI ---
    elif menu == "🔍 Barbaadi & Sirreessi":
        st.header("🔍 Barbaadi ykn Sirreessi")
        q = st.text_input("Maqaa barreessi...")
        if not df.empty:
            search = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            for idx, row in search.iterrows():
                with st.expander(f"👤 {row['Maqaa']} - {row['Gosa']}"):
                    n_maqaa = st.text_input("Maqaa", row['Maqaa'], key=f"n_{idx}")
                    if st.button("💾 Save", key=f"s_{idx}"):
                        df.at[idx, 'Maqaa'] = n_maqaa
                        save_data(df); st.rerun()
                    if st.button("🗑 Delete", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    # --- GABAASA ERGI ---
    elif menu == "📤 Gabaasa Ergi":
        st.header("📤 Gabaasa Telegram-itti Ergi")
        if not df.empty:
            if st.button("📤 Excel Gara Telegram Ergi"):
                file_name = "Gabaasa_Dadar.xlsx"
                df.to_excel(file_name, index=False)
                if send_to_telegram(file_name, f"Gabaasa Guyyaa: {datetime.now().strftime('%d/%m/%Y')}"):
                    st.success("Excel Telegram-itti ergameera!")
        else:
            st.warning("Data'n hin jiru.")

    # --- SARTIIFIKETA ---
    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Sartiifiketa Beekamtii")
        if not df.empty:
            og = st.selectbox("Ogeessa Filadhu", df['Ogeessa'].unique())
            if st.button("📜 PDF Qopheessi"):
                pdf_bytes = generate_certificate(og)
                st.download_button("📥 Buufadhu (PDF)", pdf_bytes, f"Sartii_{og}.pdf", "application/pdf")

    # --- BA'I ---
    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

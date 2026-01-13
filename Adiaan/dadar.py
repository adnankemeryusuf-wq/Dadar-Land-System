import streamlit as st
import pandas as pd
import os
import hashlib
import requests
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageOps

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# --- CSS BAREEDINA (Background fi Style) ---
st.markdown("""
    <style>
    /* Background waliigalaa */
    .stApp {
        background: linear-gradient(to bottom right, #f0f2f6, #e0e5ec);
    }
    
    /* Sidebar bifa buluu gadi furee */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* Metric Cards (Dashboard) */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-top: 4px solid #3b82f6;
    }

    /* Buttons Style */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
USERS_FILE = "users.csv"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Ittii Fayyaddam": 50.0, "Kartaa": 150.0, "Jijjirra Maqaa": 200.0,
    "Dhimma Dangaa": 100.0, "Dhimma Mana Murtii": 0.0, "Ugura Mana Murtii": 50.0,
    "Uguraa Mana Murtii Kasuu": 50.0, "Dorkka Liqii Bankii": 100.0, "Dorkkaa Liqii Bankii Kasuu": 100.0
}

# ================= 3. FUNCTIONS =================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def generate_certificate(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(2)
    pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200) 
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 40)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(22, 101, 52)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. LOGIN SYSTEM =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<h1 style='text-align: center;'>🏢 Dadar Land Admin</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni", use_container_width=True):
                if u == "admin" and p == "123": # Fake login for example
                    st.session_state.logged_in, st.session_state.user = True, u
                    st.rerun()
                else: st.error("Username ykn Password dogoggora!")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, width=100)
        st.markdown(f"### 👤 {st.session_state.user}")
        st.divider()
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Sirreessi", "🏆 Sartiifiketa", "Ba'i"])

    df = load_data()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Gabaasa Gabaabaa")
        c1, c2, c3 = st.columns(3)
        c1.metric("Baay'ina Tajaajilaa", len(df))
        total = df['Kafaltii_Taj'].astype(float).sum() if not df.empty else 0
        c2.metric("Kafaltii Waliigalaa", f"{total} ETB")
        c3.metric("Ogeessota", len(df['Ogeessa'].unique()) if not df.empty else 0)
        st.divider()
        st.dataframe(df, use_container_width=True)

    # --- GALMEE ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            gosa = col2.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            k_wal = GATII_DICT[gosa]
            st.info(f"💰 Kafaltii Ofumaan Herregame: **{k_wal} ETB**")
            
            if st.form_submit_button("💾 Galmeessi", use_container_width=True):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, k_wal]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                else: st.error("Maqaa fi Ogeessa guuti!")

    # --- BARBAADI, SIRREESSI & HAQUU ---
    elif menu == "🔍 Barbaadi & Sirreessi":
        st.header("🔍 Barbaadi, Sirreessi ykn Haqi")
        q = st.text_input("Maqaa barreessi...")
        if not df.empty:
            search_df = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            for idx, row in search_df.iterrows():
                with st.expander(f"👤 {row['Maqaa']} - {row['Gosa']}"):
                    c1, c2 = st.columns(2)
                    n_maqaa = c1.text_input("Maqaa Sirreessi", value=row['Maqaa'], key=f"n_{idx}")
                    n_araddaa = c2.text_input("Araddaa Sirreessi", value=row['Araddaa'], key=f"a_{idx}")
                    
                    b1, b2, _ = st.columns([1, 1, 2])
                    if b1.button("✅ Ol-kaayi", key=f"s_{idx}"):
                        df.at[idx, 'Maqaa'] = n_maqaa
                        df.at[idx, 'Araddaa'] = n_araddaa
                        save_data(df)
                        st.success("Sirreeffameera!")
                        st.rerun()
                    if b2.button("🗑️ Haqi", key=f"d_{idx}"):
                        df = df.drop(idx)
                        save_data(df)
                        st.warning("Haqameera!")
                        st.rerun()

    # --- SARTIIFIKETA ---
    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Beekamtii Ogeessaa")
        if not df.empty:
            og = st.selectbox("Ogeessa Filadhu", df['Ogeessa'].unique())
            if st.button("📜 Sartiifiketa Qopheessi"):
                cert = generate_certificate(og)
                st.download_button("📥 PDF Buufadhu", cert, f"Cert_{og}.pdf")

    # --- BA'I ---
    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

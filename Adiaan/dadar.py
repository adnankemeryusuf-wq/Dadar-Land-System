import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

LOGO_PATH = "logo.png" 

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm, div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    .stButton>button {
        background: linear-gradient(90deg, #4caf50, #2e7d32);
        color: white; border-radius: 8px; font-weight: bold; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & GATII =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

# GATII FI FILANNOO
GATII_DICT = {
    "Dabarsa Lafa": {
        "Jijjirraa Maqaa": 200.0,
        "Lizii Duraa": 500.0,
        "TOT": 100.0
    },
    "Ittii Fayyaddam": 50.0,
    "Kartaa": 150.0,
    "Dhimma Dangaa": 100.0,
    "Ugura Mana Murtii": 50.0,
    "Dorkka Liqii Bankii": 100.0
}

# Waggaa, Ji'a fi Guyyaa E.C
YEARS = [str(y) for y in range(2000, 2025)]
MONTHS = ["Meskerem", "Tikimt", "Hidar", "Tahsas", "Tir", "Yakatit", "Magabit", "Miazia", "Gunbot", "Sene", "Hamle", "Nehasse", "Pagume"]
DAYS = [str(d) for d in range(1, 31)]

# ================= 3. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #2e7d32;'>📊 Dashboard</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Baay'ina Tajaajilaa", len(df))
        total_money = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').sum() if not df.empty else 0
        c2.metric("Waliigala Galii", f"{total_money} ETB")
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #2e7d32;'>📝 Galmee Tajaajilaa</h2>", unsafe_allow_html=True)
        
        gosa = st.selectbox("Gosa Tajaajilaa", ["Dabarsa Lafa", "Gibira", "Ittii Fayyaddam", "Kartaa", "Dhimma Dangaa"])
        
        base_fee = 0.0
        details = ""

        # 1. Dabarsa Lafa Logic
        if gosa == "Dabarsa Lafa":
            d = GATII_DICT["Dabarsa Lafa"]
            base_fee = d["Jijjirraa Maqaa"] + d["Lizii Duraa"] + d["TOT"]
            details = f"(Jijjirraa: {d['Jijjirraa Maqaa']} + Lizii: {d['Lizii Duraa']} + TOT: {d['TOT']})"
            st.warning(details)

        # 2. Gibira Logic (Guyyaa, Ji'a, Waggaa)
        elif gosa == "Gibira":
            st.markdown("##### Bara Kalandara (E.C)")
            c1, c2, c3 = st.columns(3)
            guyyaa = c1.selectbox("Guyyaa", DAYS)
            jia = c2.selectbox("Ji'a", MONTHS)
            bara = c3.selectbox("Waggaa", YEARS)
            base_fee = 100.0 # Gatii gibiraa waggaa tokkoo
            st.info(f"Gibira Bara {bara} ({guyyaa}/{jia})")

        else:
            base_fee = GATII_DICT.get(gosa, 0.0)

        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa Fullatti")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            extra = st.number_input("Kafaltii Dabalataa", min_value=0.0)
            
            total_fee = base_fee + extra
            st.markdown(f"<div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #4caf50;'><h2 style='color: #2e7d32; margin: 0;'>💰 {total_fee} ETB</h2></div>", unsafe_allow_html=True)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    yeroo_ammaa = datetime.now().strftime('%d/%m/%Y')
                    new_row = [yeroo_ammaa, maqaa, araddaa, qaxana, gosa, ogeessa, total_fee]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success(f"✅ Tajaajilli {maqaa} galmeeffameera!")
                else:
                    st.error("Maqaa fi Ogeessa guuti!")

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

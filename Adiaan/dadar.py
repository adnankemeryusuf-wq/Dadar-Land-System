import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIG & STYLING (BAREEDINA) =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

LOGO_PATH = "logo.png" 

# Background Baredaa fi Glassmorphism Effect
st.markdown("""
    <style>
    /* Background waliigalaa */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Sidebar bareedina isaa */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }
    
    /* Sanduuqa (Container) Dashboard fi Forms */
    div.stForm, div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    }

    /* Button miidhagaa */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white;
        border-radius: 10px;
        border: none;
        transition: 0.3s;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira": {str(year): 100.0 for year in range(2000, 2019)}, 
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

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>Dadar Land Admin</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Dilaalli Sirrii Miti!")
else:
    # --- APP CONTENT ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown(f"### 👤 {st.session_state.user}")
        st.divider()
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "🏆 Sartiifiketa", "Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #1e3a8a;'>📊 Dashboard Gabaasaa</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.metric("Baay'ina Tajaajilaa", len(df))
        with c2: 
            total = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').sum() if not df.empty else 0
            st.metric("Waliigala Galii (ETB)", f"{total} ETB")
        st.divider()
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #1e3a8a;'>📝 Galmee Haaraa Galmeessi</h2>", unsafe_allow_html=True)
        
        gosa = st.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
        
        base_fee = 0.0
        if gosa == "Gibira":
            bara = st.selectbox("Bara Gibiraa", list(GATII_DICT["Gibira"].keys()))
            base_fee = GATII_DICT["Gibira"][bara]
        elif gosa == "Jijjirra Maqaa":
            d = GATII_DICT["Jijjirra Maqaa"]
            base_fee = d["Jijjirraa"] + d["Lizii Duraa"] + d["TOT"]
        else:
            base_fee = GATII_DICT[gosa]

        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            
            extra = st.number_input("Kafaltii Dabalataa", min_value=0.0)
            total_fee = base_fee + extra
            
            st.markdown(f"<h3 style='color: #2563eb;'>💰 Kafaltii: {total_fee} ETB</h3>", unsafe_allow_html=True)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, total_fee]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success("✅ Milkaa'inaan Galmeeffameera!")
                else: st.error("Maqaa fi Ogeessa guuti!")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

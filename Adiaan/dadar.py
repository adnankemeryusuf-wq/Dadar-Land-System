import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

LOGO_PATH = "logo.png" 

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

MONTHS_OR = {
    "01": "Fulbaana", "02": "Onkololeessa", "03": "Sadaasa", "04": "Muddee",
    "05": "Amajjii", "06": "Guraandhala", "07": "Bitootessa", "08": "Eebila",
    "09": "Caamsaa", "10": "Waxabajjii", "11": "Adooleessa", "12": "Hagayya", "13": "Qaammee"
}

# Gatiiwwan Ati Kennite
GATII_DICT = {
    "Ittii Fayyaddam": 50.0, 
    "Kartaa": 150.0, 
    "Jijjirra Maqaa": 200.0,
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

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "Ba'i"])

    df = load_data()

    if menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #2e7d32;'>📝 Galmee Tajaajilaa</h2>", unsafe_allow_html=True)
        
        # Dabarsa Lafa fi Gibira dabalatee listii filannoo
        options = ["Dabarsa Lafa", "Gibira"] + list(GATII_DICT.keys()) + ["Kan Biroo"]
        gosa_main = st.selectbox("Gosa Tajaajilaa Filadhu", options)
        
        base_fee = 0.0
        gosa_galmeeffamu = gosa_main

        # --- LOGIC DABARSA LAFA ---
        if gosa_main == "Dabarsa Lafa":
            sub_gosa = st.radio("Dabarsa Lafa Keessaa:", ["Jijjirraa Maqaa", "Lizii Duraa", "TOT"])
            base_fee = 200.0 if sub_gosa == "Jijjirraa Maqaa" else (500.0 if sub_gosa == "Lizii Duraa" else 100.0)
            gosa_galmeeffamu = f"Dabarsa Lafa ({sub_gosa})"

        # --- LOGIC GIBIRA ---
        elif gosa_main == "Gibira":
            c1, c2, c3 = st.columns(3)
            guyyaa = c1.selectbox("Guyyaa", [f"{i:02d}" for i in range(1, 31)])
            ji_lakk = c2.selectbox("Ji'a", list(MONTHS_OR.keys()), format_func=lambda x: f"{x} - {MONTHS_OR[x]}")
            bara = c3.selectbox("Waggaa", [str(y) for y in range(2000, 2025)])
            yeroo_gibiraa = f"{guyyaa}/{ji_lakk}/{bara}"
            base_fee = 100.0
            gosa_galmeeffamu = f"Gibira ({yeroo_gibiraa})"

        # --- LOGIC KAN BIROO (SABABAA BIROO) ---
        elif gosa_main == "Kan Biroo":
            sababa_biroo = st.text_input("Sababa tajaajilaa barreessi (Fkn: Kenniinsa Lafa Haaraa)")
            base_fee = st.number_input("Kafaltii tajaajila kanaa (ETB)", min_value=0.0, step=10.0)
            gosa_galmeeffamu = f"Biroo: {sababa_biroo}"

        else:
            base_fee = GATII_DICT.get(gosa_main, 0.0)

        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa Fullatti")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            extra = st.number_input("Kafaltii Dabalataa (Yoo jiraate)", min_value=0.0)
            
            total_fee = base_fee + extra
            st.markdown(f"<div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #4caf50;'><h2 style='color: #2e7d32; margin: 0;'>💰 {total_fee} ETB</h2></div>", unsafe_allow_html=True)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa and gosa_galmeeffamu:
                    yeroo_ammaa = datetime.now().strftime('%d/%m/%Y')
                    new_row = [yeroo_ammaa, maqaa, araddaa, qaxana, gosa_galmeeffamu, ogeessa, total_fee]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success(f"✅ Galmeeffameera!")
                else: st.error("Maaloo odeeffannoo guuti!")

    elif menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        st.dataframe(df, use_container_width=True)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIG & STYLING (HALLUU & LOGO) =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# Maqaa fayila logo keetii (Folder tokko keessa jiraachuu qaba)
LOGO_PATH = "logo.png" 

st.markdown("""
    <style>
    /* Background Magariisa Lallaafaa */
    .stApp {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    }
    
    /* Sidebar bifa magariisa dukkanaawaa */
    [data-testid="stSidebar"] {
        background-color: #1b5e20 !important;
        border-right: 1px solid #2e7d32;
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Sanduuqa (Glassmorphism Effect) */
    div.stForm, div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    /* Button magariisa baredaa */
    .stButton>button {
        background: linear-gradient(90deg, #4caf50, #2e7d32);
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        height: 3.5em;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2e7d32, #1b5e20);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

# GATII_DICT (Gibira bara 2000-2018 fi Jijjirra Maqaa)
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

def generate_certificate(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(3); pdf.set_draw_color(184, 134, 11); pdf.rect(10, 10, 277, 190) 
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, x=133, y=15, w=30)
    pdf.ln(45); pdf.set_font('Arial', 'B', 40); pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 30); pdf.set_text_color(185, 28, 28)
    pdf.cell(0, 20, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.markdown("<h2 style='text-align: center; color: #2e7d32;'>Dadar Land Admin</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Username ykn Password dogoggora!")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown(f"### 👤 {st.session_state.user}")
        st.divider()
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "🏆 Sartiifiketa", "Ba'i"])

    df = load_data()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #2e7d32;'>📊 Dashboard Gabaasaa</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Baay'ina Tajaajilaa", len(df))
        total_money = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').sum() if not df.empty else 0
        c2.metric("Waliigala Galii", f"{total_money} ETB")
        st.divider()
        st.dataframe(df, use_container_width=True)

    # --- GALMEE HAARAA (SIRREEFFAME) ---
    elif menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #2e7d32;'>📝 Galmee Haaraa Galmeessi</h2>", unsafe_allow_html=True)
        
        gosa = st.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
        
        base_fee = 0.0
        if gosa == "Gibira":
            bara = st.selectbox("Bara Gibiraa (E.C)", list(GATII_DICT["Gibira"].keys()))
            base_fee = GATII_DICT["Gibira"][bara]
        elif gosa == "Jijjirra Maqaa":
            d = GATII_DICT["Jijjirra Maqaa"]
            base_fee = d["Jijjirraa"] + d["Lizii Duraa"] + d["TOT"]
        else:
            base_fee = GATII_DICT[gosa]

        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa Fullatti")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            extra = st.number_input("Kafaltii Dabalataa", min_value=0.0)
            
            # Kafaltii Waliigalaa haqamee herrega qofatu mul'ata
            total_fee = base_fee + extra
            st.markdown(f"<div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #4caf50;'><h2 style='color: #2e7d32; margin: 0;'>💰 {total_fee} ETB</h2></div>", unsafe_allow_html=True)
            st.write("") 

            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    yeroo = datetime.now().strftime('%d/%m/%Y')
                    new_row = [yeroo, maqaa, araddaa, qaxana, gosa, ogeessa, total_fee]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success(f"✅ Tajaajilli {maqaa} galmeeffameera!")
                else:
                    st.error("Maqaa fi Ogeessa guuti!")

    # --- BARBAADI ---
    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        search_q = st.text_input("Maqaa barreessi...")
        if not df.empty:
            result = df[df['Maqaa'].str.contains(search_q, case=False, na=False)]
            st.dataframe(result, use_container_width=True)

    # --- SARTIIFIKETA ---
    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Sartiifiketa Beekamtii")
        if not df.empty:
            og_list = df['Ogeessa'].unique()
            selected_og = st.selectbox("Ogeessa Filadhu", og_list)
            if st.button("📜 PDF Qopheessi"):
                pdf_bytes = generate_certificate(selected_og)
                st.download_button("📥 Sartiifiketa Buufadhu", pdf_bytes, f"Sartii_{selected_og}.pdf")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

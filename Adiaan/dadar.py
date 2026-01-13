import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# Logo Path
LOGO_PATH = "logo.png" 

st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom right, #f8fafc, #e2e8f0); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    .stButton>button { 
        border-radius: 8px; font-weight: bold; width: 100%; height: 3em; 
        background-color: #2563eb; color: white; border: none;
    }
    .stButton>button:hover { background-color: #1d4ed8; color: white; }
    /* Sanduuqa galmee (Forms) irratti miidhagina dabalataa */
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

# GATII_DICT (Gibira bara 2000-2018)
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
    pdf.ln(10); pdf.set_font('Arial', '', 18); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, "Tajaajila qulqulluu fi saffisaa tajaajilamtootaaf kennaa turaniif beekamtii kana kennineefirra.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
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
                else: st.error("Username ykn Password dogoggora!")
else:
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown(f"### 👤 {st.session_state.user}")
        st.divider()
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Sirreessi", "🏆 Sartiifiketa", "Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Gabaasaa")
        c1, c2 = st.columns(2)
        c1.metric("Baay'ina Tajaajilaa", len(df))
        total = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').sum() if not df.empty else 0
        c2.metric("Waliigala Galii (ETB)", f"{total}")
        st.divider()
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        
        # Filannoo Gosa Tajaajilaa Sanduuqa galmee gubbaatti
        gosa = st.selectbox("Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        
        base_fee = 0.0
        if gosa == "Gibira":
            bara = st.selectbox("Bara Gibiraa (E.C)", list(GATII_DICT["Gibira"].keys()))
            base_fee = GATII_DICT["Gibira"][bara]
        elif gosa == "Jijjirra Maqaa":
            d = GATII_DICT["Jijjirra Maqaa"]
            base_fee = d["Jijjirraa"] + d["Lizii Duraa"] + d["TOT"]
            st.warning(f"💡 Herrega: Jijjirraa({d['Jijjirraa']}) + Lizii({d['Lizii Duraa']}) + TOT({d['TOT']}) = {base_fee} ETB")
        else:
            base_fee = GATII_DICT[gosa]

        # Sanduuqa Galmee - Maqaa Abbaa Dhimmaa fi kkf
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            # Sanduuqa Maqaa Abbaa Dhimmaa asitti deebisera
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa Fullatti")
            araddaa = col2.text_input("Araddaa / Ganda")
            qaxana = col1.text_input("Qaxana / Zone")
            ogeessa = col2.text_input("Maqaa Ogeessa Tajaajile")
            
            extra = st.number_input("Kafaltii Dabalataa (yoo jiraate)", min_value=0.0)
            total_fee = base_fee + extra
            
            st.info(f"💰 **Kafaltii Waliigalaa: {total_fee} ETB**")
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, total_fee]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success(f"✅ Tajaajilli {maqaa} galmeeffameera!")
                else:
                    st.error("Maqaa fi Ogeessa guutuun dirqama!")

    elif menu == "🔍 Barbaadi & Sirreessi":
        st.header("🔍 Barbaadi ykn Sirreessi")
        search_q = st.text_input("Maqaa barbaadi...")
        if not df.empty:
            result = df[df['Maqaa'].str.contains(search_q, case=False, na=False)]
            st.dataframe(result, use_container_width=True)

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

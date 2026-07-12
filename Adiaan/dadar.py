import streamlit as st
import pandas as pd
import os
import io
import requests
import tempfile
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 900; color: #10b981; text-align: center; }
    div[data-testid="stSidebarUserContent"] .stRadio label {
        background-color: #10b981 !important;
        color: #000000 !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        margin-bottom: 8px !important;
        font-weight: 700 !important;
        display: block;
        cursor: pointer;
    }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-left: 5px solid #10b981; }
    .metric-value { font-size: 2rem; font-weight: 900; color: #10b981; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & PDF FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

# (Harka fuudhuu PDF fi Sartiifikeetaa functions asitti galchi)
def create_clearance_pdf(data, logo_l, logo_r):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Times', 'B', 15)
    pdf.cell(0, 10, "WAAJJIRA LAFAA MAGAALAA DADAR", ln=True, align='C')
    # ... (PDF details)
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 class='main-title'>Dadar Land System</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        menu = st.radio("Filannoo", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📜 Clearance (Ragaa)", "📈 Gabaasa", "🚪 Logout"])
    
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("Maamiltoota", len(df))

    elif menu == "📝 Galmee Tajaajilaa":
        with st.form("reg_form"):
            name = st.text_input("Maqaa Maamilaa")
            # ... (Galmee Logic)
            if st.form_submit_button("💾 GALMEESSI"):
                # ... (Save Logic)
                st.success("✅ Galmeeffameera!")
    
    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
x='Gosa_Tajajjilaa', y='Kafaltii_Taj', title="Galii Gosa Tajaajilaan")
st.plotly_chart(fig, use_container_width=True)

elif menu == "📝 Galmee Haaraa":
st.title("📝 Galmee Tajaajilaa Haaraa")
# --- SERVICE STRUCTURE ---
SERVICE_STRUCTURE = {
"🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax) 2%"],
"📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa"],
"🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Hayyama Ijaarsaa"],
"⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
"📂 Tajaajila Biroo": ["Waraqaa Qulqullummaa", "Deebii Iyyannoo"],
"⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"]
}

with st.form("reg_form"):
col1, col2 = st.columns(2)
name = col1.text_input("Maqaa Abbaa Dhimmaa")
ara = col1.text_input("Araddaa")
qax = col2.text_input("Qaxana")
og = col2.text_input("Maqaa Ogeessaa")

cat_choice = st.selectbox("Ramaddii Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
serv_choice = st.selectbox("Gosa Tajaajilaa", SERVICE_STRUCTURE[cat_choice])

fee_input = st.number_input("Kaffaltii (ETB)", min_value=0.0)
final_fee = fee_input * 0.02 if "TOT" in serv_choice else fee_input

if st.form_submit_button("💾 GALMEESSI"):
if name and og:
new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, serv_choice, og, final_fee]
df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
save_data(df)
st.success(f"✅ Galmeeffameera! Kaffaltii: {final_fee:,.2f} ETB")

elif menu == "📈 Gabaasa":
st.title("📈 Gabaasa Waliigalaa")
st.dataframe(df, use_container_width=True)
st.download_button("📥 CSV Buufadhu", df.to_csv(index=False), "gabaasa.csv")

elif menu == "🔍 Barbaadi":
st.title("🔍 Barbaadi / Haqii")
q = st.text_input("Maqaa Barbaadi...")
if q:
results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
st.dataframe(results)
idx = st.selectbox("ID Haquuf:", results.index)
if st.button("🗑 Haqii"):
df = df.drop(idx)
save_data(df)
st.rerun()




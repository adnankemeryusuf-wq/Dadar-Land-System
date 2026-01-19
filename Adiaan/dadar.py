import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & SETUP =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# Folder uumuuf
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Administration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

# Style bareedsuuf
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 15, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    body = f"Maqaa: {data['maqaa']}\nAraddaa: {data['araddaa']}\nLakk. Manaa: {data['mana']}\nLakk. Kaartaa: {data['kaartaa']}\n\nQabiyyeen kun dhorkaa irraa bilisa ta'uu ni mirkaneessina."
    pdf.multi_cell(0, 10, body)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP UI =================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    st.markdown("<h2 style='text-align:center;'>🏢 Dadar Land Administration Login</h2>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username ykn Password dogoggora!")

else:
    # --- MAIN SIDEBAR ---
    df = load_data()
    with st.sidebar:
        st.header("FILANNOO")
        menu = st.radio("Menu", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "📜 Clearance", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("📅 Ji'a Kana", len(df[df['Ji\'a'] == MONTH_MAP[datetime.now().month]]))
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    # --- 2. REGISTRATION (GALMEE) ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara"]
        }
        
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        d_fees = {}
        details = []
        is_tot = False

        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g])
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0)
                    if s == "TOT": is_tot = True

        with st.form("reg_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            if is_tot:
                maqaa = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                araddaa = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
            else:
                maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
                araddaa = c2.text_input("Araddaa")
            
            qaxana = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                    st.rerun()

    # --- 3. CLEARANCE ---
    elif menu == "📜 Clearance":
        st.header("📜 Qophii Clearance")
        with st.form("clear_form"):
            c1, c2 = st.columns(2)
            clr_data = {
                'maqaa': c1.text_input("Maqaa Maamilaa"),
                'araddaa': c2.text_input("Araddaa"),
                'mana': c1.text_input("Lakk. Manaa"),
                'kaartaa': c2.text_input("Lakk. Kaartaa")
            }
            if st.form_submit_button("📄 PDF UUMI"):
                pdf_bytes = create_clearance_pdf(clr_data)
                st.download_button("📥 PDF Buufadhu", pdf_bytes, "Clearance.pdf", "application/pdf")

    # --- 4. SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Barbaadi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            # Edit logic asitti dabalachuu ni dandeessa

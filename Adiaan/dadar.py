import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# Hubachiisa: Library kanaan dura install gochuu kee mirkaneessi
# pip install ethiopian-date
try:
    from ethiopian_date import EthiopianDateConverter
except ImportError:
    st.error("Maaloo 'pip install ethiopian-date' godhi!")

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
LOGO_PATH = "Adiaan/logo.png"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    .stApp { background: #fdfdfd; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    div.stForm { background: white; border-radius: 15px; border: 2px solid #2e7d32; padding: 20px; }
    .card { background: white; padding: 15px; border-radius: 10px; border-top: 5px solid #2e7d32; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. FUNCTIONS =================
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

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}"

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277) # Border
    
    # Header
    pdf.set_y(22); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.line(20, 56, 190, 56)

    # Body Logic
    pdf.ln(20); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Dhimma: Waraqaa Ragaa Qulqullinaa - {data['maqaa']}", ln=True)
    pdf.set_font('Arial', '', 12)
    txt = f"Waraqaan kun Obbo/Adde {data['maqaa']} Araddaa {data['araddaa']} Qaxana {data['qaxana']} keessatti Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha. Bara gibiraa {data['bara_gibiraa']} xumuraniiru. Dhimma {data['dhimma']} raawwachuuf mormii hin qabnu."
    pdf.multi_cell(0, 10, txt)
    
    pdf.set_y(240); pdf.cell(0, 10, f"Itti Gaafatamaa: {data['head_name']}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.header("🔑 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
else:
    df = load_data()
    with st.sidebar:
        st.title("Dadar Land Admin")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "📝 CLEARANCE", "🔍 Barbaadi"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii</p><h3>{df['Kafaltii_Taj'].sum():,.2f}</h3></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><h3>{len(df)}</h3></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Cimaa</p><h3>{df['Maqaa_Ogeessa'].mode()[0]}</h3></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    # --- CLEARANCE ---
    elif menu == "📝 CLEARANCE":
        st.header("📝 Qophii Clearance")
        with st.form("clearance_form"):
            c1, c2 = st.columns(2)
            m_maqaa = c1.text_input("Maqaa Maamilaa *")
            m_kaartaa = c2.text_input("Lakk. Kaartaa *")
            m_araddaa = c1.text_input("Araddaa")
            m_qaxana = c2.text_input("Qaxana")
            m_bara = c1.text_input("Bara Gibiraa (Fkn: 2017)")
            m_dhimma = c2.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa"])
            m_head = st.text_input("Maqaa Itti Gaafatamaa *")
            
            if st.form_submit_button("💾 PDF UUMI"):
                if m_maqaa and m_kaartaa:
                    pdf_bytes = create_clearance_pdf({'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 'head_name': m_head})
                    st.download_button("📥 PDF Buufadhu", pdf_bytes, f"Clearance_{m_maqaa}.pdf")

    # --- GABAASA (CALALA) ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa fi Calala")
        
        f_type = st.selectbox("Calali:", ["Waliigala", "Waggaa", "Ji'a"])
        # (Kutaa gabaasa kee isa duraa asitti itti fufa...)
        st.dataframe(df[COL_NAMES])

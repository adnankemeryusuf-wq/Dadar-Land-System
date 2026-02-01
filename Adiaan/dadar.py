import streamlit as st
import pandas as pd
import os
import io
import requests
import tempfile
from datetime import datetime, timedelta
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
    div[data-testid="stSidebarUserContent"] .stRadio label {
        background-color: #10b981 !important;
        color: #000000 !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 15px 25px !important;
        margin-bottom: 10px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(12, 173, 120, 0.4) !important;
        display: block;
        cursor: pointer;
    }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-left: 5px solid #10b981; }
    .metric-value { font-size: 2rem; font-weight: 900; color: #10b981; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    df['Date_Temp'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Ji\'a'] = df['Date_Temp'].dt.month_name()
    return df

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date.day:02d}/{e_date.month:02d}/{e_date.year}"

# ================= 3. PDF GENERATION =================

def create_receipt_pdf(data):
    """Nagahee kaffaltii tajaajilaa uumuuf"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "NAGAHEE KAFFALTII TAJAAJILAA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Guyyaa: {data[0]}", ln=True)
    pdf.cell(0, 10, f"Maqaa: {data[1]}", ln=True)
    pdf.cell(0, 10, f"Tajaajila: {data[4]}", ln=True)
    pdf.cell(0, 10, f"Kaffaltii: {data[6]:,.2f} ETB", ln=True)
    pdf.cell(0, 10, f"Ogeessa: {data[5]}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

def create_clearance_pdf(data):
    """Waraqaa Ragaa Qulqullinaa (Clearance) uumuuf"""
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)
    
    pdf.set_y(22); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    pdf.write(5, f"Guyyaa: {get_ethiopian_date_str()}")
    pdf.ln(15); pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    body = f"Obbo/Adde {data['maqaa']} Araddaa {data['araddaa']} Lakk. Kaartaa {data['kaartaa']} irratti qabiyyee qabaniif ragaan qulqullinaa kun dhimma {data['dhimma']} kaffaltii bara {data['bara_gibiraa']} xumuraniif kennameera."
    pdf.multi_cell(170, 8, body)
    
    pdf.set_y(240); pdf.set_x(20)
    pdf.write(8, f"Maqaa Itti Gaafatamaa: {data['head_name']}\nMallattoo: _________________")
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. STREAMLIT UI =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login"):
            u, p = st.text_input("Username"), st.text_input("Password", type="password")
            if st.form_submit_button("SEENI"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.rerun()
else:
    df = load_data()
    with st.sidebar:
        menu = st.radio("Filannoo", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📜 Clearance (Ragaa)", "📈 Gabaasa", "🚪 Logout"])

    # --- REGISTRATION (Kutaa Ati Gaafatte) ---
    if menu == "📝 Galmee Tajaajilaa":
        st.header("📝 Galmee Haaraa Galchi")
        GATII_DICT = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
            "🏗 Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Mirkaneessa Sertifikeeta Ijaarsaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu"],
            "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"]
        }
        
        sel_main = st.multiselect("🟢 Ramaddii Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if sel_main:
            for g in sel_main:
                subs = st.multiselect(f"Filadhu ({g}):", GATII_DICT[g], key=f"s_{g}")
                if subs:
                    sub_cols = st.columns(len(subs))
                    for idx, s in enumerate(subs):
                        with sub_cols[idx]:
                            fee = st.number_input(f"Gatii {s}", min_value=0.0, key=f"v_{idx}_{s}")
                            details.append(s)
                            d_fees[f"{idx}_{s}"] = fee
                            if any(x in s for x in ["Jijjiirraa", "TOT", "Sale"]): is_tot = True

        with st.form("main_form"):
            c1, c2 = st.columns(2)
            if is_tot:
                name_f = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
            else:
                name_f, ara_f = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")
            
            qax_f, ogeessa = c1.text_input("Qaxana"), c2.text_input("Maqaa Ogeessaa")
            total_sum = sum(d_fees.values())
            st.markdown(f"### 💰 Waliigala Kaffaltii: {total_sum:,.2f} ETB")
            
            if st.form_submit_button("💾 GALMEESSI"):
                if name_f and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y %H:%M'), name_f, ara_f, qax_f, ", ".join(details), ogeessa, total_sum]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                    receipt = create_receipt_pdf(new_row)
                    st.download_button("📥 Nagahee Buufadhu", receipt, f"Nagahee_{name_f}.pdf", "application/pdf")
                else: st.warning("Maaloo odeeffannoo guuti!")

    # --- CLEARANCE (Ragaa Qulqullinaa) ---
    elif menu == "📜 Clearance (Ragaa)":
        st.header("📜 Waraqaa Ragaa Qulqullinaa")
        with st.form("clear_form"):
            c1, c2 = st.columns(2)
            clr_data = {
                'maqaa': c1.text_input("Maqaa Maamilaa *"),
                'araddaa': c2.text_input("Araddaa *"),
                'kaartaa': c1.text_input("Lakk. Kaartaa *"),
                'bara_gibiraa': c2.text_input("Bara Gibiraa Xumurame"),
                'dhimma': c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Baankii", "Kennaa"]),
                'head_name': c2.text_input("Maqaa Itti Gaafatamaa *")
            }
            if st.form_submit_button("📄 PDF UUMI"):
                if clr_data['maqaa'] and clr_data['head_name']:
                    pdf_out = create_clearance_pdf(clr_data)
                    st.download_button("📥 Clearance Buufadhu", pdf_out, f"Clearance_{clr_data['maqaa']}.pdf")
                else: st.error("Maaloo kutaalee hunda guuti!")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

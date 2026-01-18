import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & SETUP =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if 'pdf_to_download' not in st.session_state: st.session_state.pdf_to_download = None

# ================= 2. CORE FUNCTIONS =================

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)

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
    
    # Logos
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 18, 23)

    # Header
    pdf.set_y(22); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(2); pdf.line(20, 56, 190, 56)

    # Date/Ref
    e_date = get_ethiopian_date_str()
    pdf.ln(12); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    pdf.cell(90, 5, f"Lakk: DAD/WL/{e_date[-4:]}/____", align='L')
    pdf.cell(80, 5, f"Guyyaa: {e_date}", ln=True, align='R')

    # Body
    pdf.ln(15); pdf.set_font('Arial', 'BU', 14)
    pdf.cell(0, 10, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.set_y(95); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    
    txt = (f"Waraqaan ragaa kun Obbo/Adde {data['maqaa'].upper()}, Araddaa {data['araddaa']}, "
           f"Qaxana {data['qaxana']} keessatti qabiyyee Lakk. Kaartaa {data['kaartaa']} qabaniif kenname.\n\n"
           f"1. Gibira waggaa hanga bara {data['bara']} kaffalaniiru.\n"
           f"2. Kaffaltii {data['gosa']} hunda raawwatanii qulqulleessaniiru.\n"
           f"3. Qabiyyeen kun DHORKAA kamirraayyuu bilisa ta'uu ni mirkaneessina.\n\n"
           f"Kanaafuu, dhimma {data['dhimma']} raawwachuuf ragaa kana kenneeraaf.")
    pdf.multi_cell(170, 10, txt, align='L')

    # Sign
    pdf.set_y(240); pdf.set_font('Arial', 'B', 12); pdf.set_x(110)
    pdf.cell(0, 7, "Itti Gaafatamaa: ________________", ln=True)
    pdf.set_x(110); pdf.cell(0, 7, "(Chaappaa Waajjiraa)", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI LAYOUT =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")
df = load_data()

# SIDEBAR / SETTINGS
with st.sidebar:
    st.header("⚙️ Qindaa'ina")
    up_b = st.file_uploader("Logo Bittaa", type=['png', 'jpg'])
    if up_b: Image.open(up_b).convert("RGB").save("logo_bitta.jpg", "JPEG")
    up_m = st.file_uploader("Logo Mirgaa", type=['png', 'jpg'])
    if up_m: Image.open(up_m).convert("RGB").save("logo_mirga.jpg", "JPEG")
    st.markdown("---")
    menu = st.radio("FILANNOO", ["📝 Galmee & Clearance", "📊 Dashboard", "📈 Gabaasa"])

# 1. GALMEE & CLEARANCE
if menu == "📝 Galmee & Clearance":
    st.header("📝 Galmee Haaraa")
    with st.form("main_form"):
        c1, c2 = st.columns(2)
        m_maqaa = c1.text_input("Maqaa Maamilaa *")
        m_araddaa = c2.text_input("Araddaa *")
        m_qaxana = c1.text_input("Qaxana")
        m_kaartaa = c2.text_input("Lakk. Kaartaa *")
        m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii"])
        m_bara = c2.text_input("Bara Gibiraa (Fkn: 2017)")
        m_dhimma = c1.selectbox("Dhimma", ["Gurgurtaa", "Liqii", "Kennaa"])
        m_ogeessa = c2.text_input("Ogeessa Raawwate *")
        m_kafaltii = st.number_input("Kaffaltii (ETB)", min_value=0.0)
        
        if st.form_submit_button("💾 GALMEESSI"):
            if m_maqaa and m_araddaa:
                row = [datetime.now().strftime('%d/%m/%Y'), m_maqaa, m_araddaa, m_qaxana, m_dhimma, m_ogeessa, m_kafaltii]
                df = pd.concat([df, pd.DataFrame([row], columns=COL_NAMES)])
                save_data(df)
                data_pdf = {'maqaa':m_maqaa, 'araddaa':m_araddaa, 'qaxana':m_qaxana, 'kaartaa':m_kaartaa, 'bara':m_bara, 'gosa':m_gosa, 'dhimma':m_dhimma}
                st.session_state.pdf_to_download = create_clearance_pdf(data_pdf)
                st.rerun()

    if st.session_state.pdf_to_download:
        st.download_button("📥 PDF CLEARANCE BUUFADHU", st.session_state.pdf_to_download, "Clearance.pdf")

# 2. DASHBOARD
elif menu == "📊 Dashboard":
    st.header("📊 Statistiksii")
    c1, c2 = st.columns(2)
    c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
    c2.metric("Baay'ina Maamilaa", len(df))

# 3. GABAASA
elif menu == "📈 Gabaasa":
    st.header("📈 Gabatee Gabaasaa")
    st.dataframe(df, use_container_width=True)
    if st.button("🚀 Gabaasa Telegram-itti Ergi"):
        st.info("Eergamaa jira...")

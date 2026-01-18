import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & SETUP =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# Session State qopheessuu
if 'pdf_to_download' not in st.session_state:
    st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

# ================= 2. CORE FUNCTIONS =================

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding="utf-8")

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}"

# --- WARAQAA RAGAA (CLEARANCE) PDF ---
def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    
    # Logos
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 15, 25)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 170, 15, 25)

    # Header
    pdf.set_y(22); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 8, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "WAAJJIRA LAFAA BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    pdf.ln(5); pdf.set_line_width(0.5); pdf.line(20, 48, 190, 48)

    # Date & Ref
    converter = EthiopianDateConverter()
    now_ec = converter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)
    guyyaa_ec = get_ethiopian_date_str()
    
    pdf.ln(8); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    pdf.cell(90, 5, f"Lakk. Galmee: DAD/WL/{now_ec[0]}/____", align='L')
    pdf.cell(80, 5, f"Guyyaa: {guyyaa_ec}", ln=True, align='R')

    # Subject
    pdf.ln(10); pdf.set_font('Arial', 'BU', 14)
    pdf.cell(0, 10, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')

    # Body
    pdf.set_y(90); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    text_content = (
        f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} "
        f"Qaxana {data['qaxana']} keessatti tajaajila argachaa turaniif kan kennameedha.\n\n"
        f"Maamilli kun hanga guyyaa har'aatti ({guyyaa_ec}) tatti tajaajiloota waajjira keenya irraa:\n\n"
        f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} kaffalaniiru.\n"
        f"2. Qabiyyee Lakk. Kaartaa {data['kaartaa']} qabaniif kaffaltii barbaachisu raawwataniiru.\n"
        f"3. Qabiyyeen kun DHORKAA kamirrayyuu bilisa ta'uu isaa mirkaneessina.\n\n"
        f"Kanaafuu, dhimma '{data['dhimma']}' raawwachuuf ragaa kana akka dhiyeeffatan ni mirkaneessina."
    )
    pdf.multi_cell(170, 9, text_content, align='L')

    # Signature
    pdf.set_y(230); pdf.set_font('Arial', 'B', 12); pdf.set_x(120)
    pdf.cell(0, 8, "Itti Gaafatamaa Waajjiraa", ln=True)
    pdf.set_x(120); pdf.cell(0, 8, "Mallattoo: ____________", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI LAYOUT =================
st.set_page_config(page_title="Dadar Land Management", layout="wide")
df = load_data()

menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee & Clearance", "🏆 Badhaasa", "📈 Gabaasa"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
    c2.metric("Maamiltoota", len(df))
    c3.metric("Ogeeyyii", df['Maqaa_Ogeessa'].nunique())

# --- GALMEE & CLEARANCE ---
elif menu == "📝 Galmee & Clearance":
    st.header("📝 Galmee fi Qophii Clearance")
    
    # Logo Configuration in Sidebar
    st.sidebar.subheader("⚙️ Qindaa'ina Mallattoo")
    up_bitta = st.sidebar.file_uploader("Logo Bittaa", type=['png', 'jpg'])
    if up_bitta:
        img_b = Image.open(up_bitta).convert("RGB").save("logo_bitta.jpg")
    
    up_mirga = st.sidebar.file_uploader("Logo Mirgaa", type=['png', 'jpg'])
    if up_mirga:
        img_m = Image.open(up_mirga).convert("RGB").save("logo_mirga.jpg")

    if st.session_state.pdf_to_download:
        st.success("📄 Clearance qophaa'eera!")
        st.download_button("📥 PDF BUUFADHU", st.session_state.pdf_to_download, st.session_state.pdf_name)
        if st.button("Galmee Haaraa"): 
            st.session_state.pdf_to_download = None
            st.rerun()

    with st.form("clearance_form"):
        c1, c2 = st.columns(2)
        m_maqaa = c1.text_input("Maqaa Maamilaa *")
        m_ogeessa = c2.text_input("Maqaa Ogeessa Galmeessu *")
        m_araddaa = c1.text_input("Araddaa *")
        m_qaxana = c2.text_input("Qaxana")
        m_kaartaa = c1.text_input("Lakk. Kaartaa")
        m_bara = c2.text_input("Bara Gibiraa (Fkn: 2017)")
        m_dhimma = st.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
        m_kaffaltii = st.number_input("Kaffaltii Tajaajilaa (ETB)", min_value=0.0)
        m_dhorkaa = st.checkbox("Dhorkaa irraa bilisa ta'uu nan mirkaneessa")

        if st.form_submit_button("💾 GALMEESSI FI PDF UUMI"):
            if m_maqaa and m_ogeessa and m_dhorkaa:
                # Save to Data
                new_row = [get_ethiopian_date_str(), m_maqaa, m_araddaa, m_qaxana, "Clearance", m_ogeessa, m_kaffaltii]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                
                # Generate PDF
                data_map = {'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma}
                st.session_state.pdf_to_download = create_clearance_pdf(data_map)
                st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
                st.rerun()
            else: st.error("Maaloo odeeffannoo guutuu galchi!")

# --- GABAASA ---
elif menu == "📈 Gabaasa":
    st.header("📈 Gabaasa Galmee Waliigalaa")
    st.dataframe(df, use_container_width=True)
    
    if st.button("🚀 Excel Gara Telegram-itti Ergi"):
        # (Asitti logic Telegram kee itti fufi)
        st.info("Gabaasni gara maanjaraatti ergamaa jira...")

# --- BADHAASA ---
elif menu == "🏆 Badhaasa":
    st.header("🏆 Ogeeyyii Baay'ee Hojjetan")
    if not df.empty:
        st.bar_chart(df['Maqaa_Ogeessa'].value_counts())

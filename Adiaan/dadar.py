import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from ethiopian_date import EthiopianDateConverter

# ================= 1. QINDAA'INA BU'URAA =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

if 'pdf_to_download' not in st.session_state:
    st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

# ================= 2. FUNKSHINOOTA PDF =================

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date.day:02d}/{e_date.month:02d}/{e_date.year}"

def create_clearance_pdf(data):
    # Times New Roman (Times) fayyadamna
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Sarara Border
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Logos
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 15, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 15, 23)

    # --- HEADER (14pt & 15pt Bold) ---
    pdf.set_y(22)
    pdf.set_font('Times', 'B', 15)
    pdf.cell(0, 8, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.cell(0, 8, "WAAJJIRA LAFAA", ln=True, align='C')
    
    pdf.ln(2); pdf.set_line_width(0.5); pdf.line(20, 48, 190, 48)

    # Lakk fi Guyyaa (12pt)
    pdf.ln(8); pdf.set_font('Times', '', 12)
    converter = EthiopianDateConverter()
    now_ec = converter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)
    guyyaa_ec = get_ethiopian_date_str()

    pdf.set_x(20)
    pdf.cell(90, 5, f"Lakk. Galmee: DAD/WL/{now_ec.year}/____", ln=False, align='L')
    pdf.cell(80, 5, f"Guyyaa: {guyyaa_ec}", ln=True, align='R')

    # --- SUBJECT (14pt Bold + Underline) ---
    pdf.ln(10); pdf.set_font('Times', 'BU', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')

    # --- BODY TEXT (12pt, Spacing 9mm ≈ 1.5 spacing) ---
    pdf.set_y(90); pdf.set_font('Times', '', 12)
    
    if data.get('gosa_qabiyyee') == "Liizii":
        kaffaltii_ibsa = "2. Kaffaltii Liizii waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina."
    else:
        kaffaltii_ibsa = "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina."

    pdf.set_x(20)
    text_content = (
        f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} "
        f"Qaxana {data['qaxana']} keessatti mana/lafa Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\n"
        f"Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n"
        f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} guutummaatti kaffalaniiru.\n"
        f"{kaffaltii_ibsa}\n"
        f"3. Lafni/Manni kun DHORKAA MANA MURTII ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n"
        f"Kanaafuu, maamilli kun dhimma {data['dhimma']} raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, "
        f"waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina."
    )
    # 9mm spacing filatamaadha
    pdf.multi_cell(170, 9, text_content, align='L')

    # --- SIGNATURE (12pt Bold) ---
    pdf.set_y(230); pdf.set_font('Times', 'B', 12); pdf.set_x(120)
    pdf.cell(0, 8, "Maqaa Itti Gaafatamaa: ________________", ln=True)
    pdf.set_x(120); pdf.cell(0, 8, "Mallattoo: _________________", ln=True)
    pdf.set_x(120); pdf.cell(0, 8, f"Guyyaa (E.C): {guyyaa_ec}", ln=True)
    pdf.set_x(120); pdf.cell(0, 8, "(Chaappaa Waajjiraa)", ln=True)

    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI LAYOUT =================

st.sidebar.header("⚙️ Qindaa'ina Mallattoo")
up_bitta = st.sidebar.file_uploader("Logo Bittaa", type=['png', 'jpg', 'jpeg'], key="up_b")
if up_bitta:
    Image.open(up_bitta).convert("RGB").save("logo_bitta.jpg", "JPEG")

up_mirga = st.sidebar.file_uploader("Logo Mirgaa", type=['png', 'jpg', 'jpeg'], key="up_m")
if up_mirga:
    Image.open(up_mirga).convert("RGB").save("logo_mirga.jpg", "JPEG")

st.header("📝 Galmee fi Qophii Clearance (E.C.)")

if st.session_state.pdf_to_download:
    st.download_button("📥 PDF BUUFADHU", st.session_state.pdf_to_download, st.session_state.pdf_name, "application/pdf")
    if st.button("Galmee Haaraa"): 
        st.session_state.pdf_to_download = None; st.rerun()

with st.form("clearance_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    m_maqaa = c1.text_input("Maqaa Maamilaa *")
    m_araddaa = c2.text_input("Araddaa *")
    m_qaxana = c1.text_input("Lakk. Qaxana *")
    m_kaartaa = c2.text_input("Lakk. Kaartaa *")
    m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii (Permit)"])
    m_bara = c2.text_input("Bara Gibiraa Xumurame (Fkn: 2017)")
    m_dhimma = c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
    m_dhorkaa_bilisa = st.checkbox("Dhorkaa irraa bilisa ta'uu nan mirkaneessa.")

    if st.form_submit_button("💾 PDF UUMI"):
        if m_maqaa and m_kaartaa and m_dhorkaa_bilisa:
            data_map = {
                'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 
                'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 
                'gosa_qabiyyee': m_gosa
            }
            st.session_state.pdf_to_download = create_clearance_pdf(data_map)
            st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
            st.rerun()
        else:
            st.error("⚠️ Odeeffannoo hunda guuti!")

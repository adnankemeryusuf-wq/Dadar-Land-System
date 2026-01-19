import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from ethiopian_date import EthiopianDateConverter

# ================= 1. SETUP =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

if 'pdf_to_download' not in st.session_state:
    st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

# ================= 2. FUNCTIONS =================

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date.day:02d}/{e_date.month:02d}/{e_date.year}"

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Double line)
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Logos
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 18, 23)

    # --- Header Section (Tartiiba Ati Gaafatte) ---
    pdf.set_y(22)
    pdf.set_font('Times', 'B', 15)
    # 1. Naannoo
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    
    pdf.set_font('Times', 'B', 14)
    # 2. Waajjira
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    # 3. Bulchiinsa Magaalaa
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    # Header Underline
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)

    # Date and Ref No
    pdf.ln(12); pdf.set_font('Times', '', 12)
    guyyaa_ec = get_ethiopian_date_str()
    converter = EthiopianDateConverter()
    now_ec = converter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)

    pdf.set_x(20)
    pdf.write(5, "Lakk. Galmee: ")
    pdf.set_font('Times', 'B', 12) 
    pdf.write(5, f"DAD/WL/{now_ec.year}/____")
    pdf.set_font('Times', '', 12)
    pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {guyyaa_ec}")
    pdf.ln(18)

    # Subject
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8)

    # Body
    pdf.set_font('Times', '', 12)
    pdf.set_x(20)
    
    pdf.write(9, "Waraqaan ragaa kun Obbo/Adde/Dhaabbata ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['maqaa'].upper()}")
    pdf.set_font('Times', '', 12); pdf.write(9, " Araddaa ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['araddaa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " Qaxana ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['qaxana']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " keessatti mana/lafa Lakk. Kaartaa ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['kaartaa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " qabaniif kan kennameedha.\n\n")

    pdf.write(9, "Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n")

    # Items
    pdf.write(9, "1. Kaffaltii Gibira waggaa hanga bara ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['bara_gibiraa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " guutummaatti kaffalaniiru.\n")

    if data.get('gosa_qabiyyee') == "Liizii":
        pdf.write(9, "2. Kaffaltii "); pdf.set_font('Times', 'B', 12); pdf.write(9, "Liizii")
        pdf.set_font('Times', '', 12); pdf.write(9, " waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")
    else:
        pdf.write(9, "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")

    pdf.write(9, "3. Lafni/Manni kun "); pdf.set_font('Times', 'B', 12); pdf.write(9, "DHORKAA MANA MURTII")
    pdf.set_font('Times', '', 12); pdf.write(9, " ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n")

    pdf.write(9, "Kanaafuu, maamilli kun dhimma "); pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['dhimma']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina.")

    # --- SIGNATURE SECTION ---
    pdf.set_y(235)
    pdf.set_x(20)
    pdf.set_font('Times', '', 12); pdf.write(8, "Maqaa Itti Gaafatamaa: ")
    pdf.set_font('Times', 'B', 12); pdf.write(8, f"{data['head_name']}")
    
    pdf.ln(8); pdf.set_x(20)
    pdf.set_font('Times', '', 12); pdf.write(8, "Mallattoo: _________________")
    
    # Stamp (Right)
    pdf.set_y(243); pdf.set_x(120)
    pdf.set_font('Times', 'B', 11)
    pdf.cell(70, 8, "(Chaappaa Waajjiraa)", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')

# ================= 3. STREAMLIT UI =================
st.header("📝 Sirna Qophii Waraqaa Qulqullinaa (Clearance)")
with st.form("clearance_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    m_maqaa = c1.text_input("Maqaa Maamilaa *")
    m_araddaa = c2.text_input("Araddaa *")
    m_qaxana = c1.text_input("Lakk. Qaxana *")
    m_kaartaa = c2.text_input("Lakk. Kaartaa *")
    m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii (Permit)"])
    m_bara = c2.text_input("Bara Gibiraa Xumurame (Fkn: 2017)")
    m_dhimma = c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
    st.markdown("---")
    m_head = st.text_input("Maqaa Itti Gaafatamaa *")
    m_dhorkaa_bilisa = st.checkbox("Qabiyyeen kun dhorkaa irraa bilisa ta'uu nan mirkaneessa.")

    if st.form_submit_button("💾 PDF UUMI"):
        if all([m_maqaa, m_kaartaa, m_head, m_dhorkaa_bilisa]):
            data_map = {
                'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 
                'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 
                'gosa_qabiyyee': m_gosa, 'head_name': m_head
            }
            st.session_state.pdf_to_download = create_clearance_pdf(data_map)
            st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
            st.rerun()


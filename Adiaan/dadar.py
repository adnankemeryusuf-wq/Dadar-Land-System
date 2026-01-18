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
    
    # Border
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Logos
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 15, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 15, 23)

    # Header
    pdf.set_y(22)
    pdf.set_font('Times', 'B', 15)
    pdf.cell(0, 8, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.cell(0, 8, "WAAJJIRA LAFAA", ln=True, align='C')
    
    pdf.ln(2); pdf.set_line_width(0.5); pdf.line(20, 48, 190, 48)

    # Date
    pdf.ln(10); pdf.set_font('Times', '', 12)
    converter = EthiopianDateConverter()
    now_ec = converter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)
    guyyaa_ec = get_ethiopian_date_str()

    pdf.set_x(20)
    pdf.cell(90, 5, f"Lakk. Galmee: DAD/WL/{now_ec.year}/____", ln=False, align='L')
    pdf.cell(80, 5, f"Guyyaa: {guyyaa_ec}", ln=True, align='R')

    # Subject
    pdf.ln(12); pdf.set_font('Times', 'BU', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')

    # Body (Fageenya sararaa 9mm - 1.5 spacing)
    pdf.set_y(95); pdf.set_font('Times', '', 12)
    kaffaltii_ibsa = ("2. Kaffaltii Liizii waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina." 
                      if data.get('gosa_qabiyyee') == "Liizii" else 
                      "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina.")

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
    pdf.multi_cell(170, 9, text_content, align='L')

    # --- SIGNATURE SECTION (Bitatti Ogeessa, Mirgatti Itti Gaafatamaa) ---
    # Fageenya gahaa jalaan dhiiseera (y=230)
    pdf.set_y(230)
    
    # Sarara 1: Maqaa
    pdf.set_x(20)
    pdf.set_font('Times', 'B', 12)
    pdf.cell(85, 8, f"Ogeessa Qopheesse: {data['ogeessa_name']}", ln=0, align='L')
    pdf.set_x(110)
    pdf.cell(85, 8, f"Itti Gaafatamaa: {data['head_name']}", ln=1, align='L')
    
    pdf.ln(2) # Fageenya xiqqaa gidduutti

    # Sarara 2: Mallattoo
    pdf.set_x(20)
    pdf.cell(85, 8, "Mallattoo: _________________", ln=0, align='L')
    pdf.set_x(110)
    pdf.cell(85, 8, "Mallattoo: _________________", ln=1, align='L')

    pdf.ln(2)

    # Sarara 3: Guyyaa fi Chaappaa
    pdf.set_x(20)
    pdf.cell(85, 8, f"Guyyaa: {guyyaa_ec}", ln=0, align='L')
    pdf.set_x(110)
    pdf.cell(85, 8, "(Chaappaa Waajjiraa)", ln=1, align='L')

    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI LAYOUT =================

st.header("📝 Galmee fi Qophii Clearance (E.C.)")

# Logo handling (Optional sidebars)
with st.sidebar:
    st.header("⚙️ Logos")
    up_b = st.file_uploader("Logo Bittaa", type=['png', 'jpg'])
    if up_b: Image.open(up_b).convert("RGB").save("logo_bitta.jpg", "JPEG")
    up_m = st.file_uploader("Logo Mirgaa", type=['png', 'jpg'])
    if up_m: Image.open(up_m).convert("RGB").save("logo_mirga.jpg", "JPEG")

if st.session_state.pdf_to_download:
    st.success("📄 PDF Qophaa'eera!")
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
    
    st.markdown("### Kutaa Mallattoo")
    col_a, col_b = st.columns(2)
    m_ogeessa = col_a.text_input("Ogeessa Qopheesse (Bita) *")
    m_head = col_b.text_input("Itti Gaafatamaa (Mirga) *")
    
    m_dhorkaa_bilisa = st.checkbox("Dhorkaa irraa bilisa ta'uu nan mirkaneessa.")

    if st.form_submit_button("💾 PDF UUMI"):
        if all([m_maqaa, m_kaartaa, m_head, m_ogeessa, m_dhorkaa_bilisa]):
            data_map = {
                'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 
                'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 
                'gosa_qabiyyee': m_gosa, 'head_name': m_head, 'ogeessa_name': m_ogeessa
            }
            st.session_state.pdf_to_download = create_clearance_pdf(data_map)
            st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
            st.rerun()
        else:
            st.error("⚠️ Maaloo odeeffannoo hunda guuti!")

import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from ethiopian_date import EthiopianDateConverter

# ================= 1. SETUP =================
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
    # 'latin-1' irratti dogongora uumuu danda'a, 'replace' itti daballa
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Double line)
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Logos - Check if files exist
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 18, 23)

    # Header Section
    pdf.set_y(22)
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)

    # Date and Ref No
    pdf.ln(12); pdf.set_font('Arial', '', 12)
    guyyaa_ec = get_ethiopian_date_str()
    now_ec = EthiopianDateConverter().to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)

    pdf.set_x(20)
    pdf.write(5, f"Lakk. Galmee: DAD/WL/{now_ec.year}/____")
    pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {guyyaa_ec}")
    pdf.ln(18)

    # Subject
    pdf.set_font('Arial', 'B', 13)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8)

    # Body
    pdf.set_font('Arial', '', 12)
    pdf.set_x(20)
    
    # Maqaa fi odeeffannoo maamilaa
    pdf.write(9, "Waraqaan ragaa kun Obbo/Adde/Dhaabbata ")
    pdf.set_font('Arial', 'B', 12); pdf.write(9, f"{data['maqaa'].upper()}")
    pdf.set_font('Arial', '', 12); pdf.write(9, f" Araddaa {data['araddaa']} Qaxana {data['qaxana']} keessatti mana/lafa Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\n")

    pdf.write(9, "Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n")

    # Items
    pdf.write(9, f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} guutummaatti kaffalaniiru.\n")

    if data.get('gosa_qabiyyee') == "Liizii":
        pdf.write(9, "2. Kaffaltii Liizii waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")
    else:
        pdf.write(9, "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")

    pdf.write(9, "3. Lafni/Manni kun DHORKAA MANA MURTII ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n")

    pdf.write(9, f"Kanaafuu, maamilli kun dhimma {data['dhimma']} raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina.")

    # Signature Section
    pdf.set_y(235); pdf.set_x(20)
    pdf.write(8, f"Maqaa Itti Gaafatamaa: {data['head_name']}\n")
    pdf.write(8, "Mallattoo: _________________")
    
    pdf.set_y(243); pdf.set_x(120); pdf.set_font('Arial', 'B', 11)
    pdf.cell(70, 8, "(Chaappaa Waajjiraa)", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. STREAMLIT UI =================
st.header("📝 Sirna Qophii Waraqaa Qulqullinaa (Clearance)")

# Iddoo Download itti mul'atu (Form'n ala)
if st.session_state.pdf_to_download:
    st.success(f"✅ Clearance {st.session_state.pdf_name} Qophaa'eera!")
    st.download_button(
        label="📥 Waraqaa Qulqullinaa Buusi (Download PDF)",
        data=st.session_state.pdf_to_download,
        file_name=st.session_state.pdf_name,
        mime="application/pdf"
    )
    if st.button("🔄 Qophii Haaraa Jalqabi"):
        st.session_state.pdf_to_download = None
        st.rerun()

with st.form("clearance_form"):
    c1, c2 = st.columns(2)
    m_maqaa = c1.text_input("Maqaa Maamilaa *")
    m_araddaa = c2.text_input("Araddaa *")
    m_qaxana = c1.text_input("Lakk. Qaxana *")
    m_kaartaa = c2.text_input("Lakk. Kaartaa *")
    m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii (Permit)"])
    m_bara = c2.text_input("Bara Gibiraa Xumurame (Fkn: 2017)")
    m_dhimma = c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
    m_head = st.text_input("Maqaa Itti Gaafatamaa *")
    m_confirm = st.checkbox("Qabiyyeen kun dhorkaa irraa bilisa ta'uu nan mirkaneessa.")

    if st.form_submit_button("💾 PDF UUMI"):
        if all([m_maqaa, m_kaartaa, m_head, m_confirm]):
            data_map = {
                'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 
                'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 
                'gosa_qabiyyee': m_gosa, 'head_name': m_head
            }
            pdf_out = create_clearance_pdf(data_map)
            st.session_state.pdf_to_download = pdf_out
            st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
            st.rerun()
        else:
            st.error("⚠️ Maaloo odeeffannoo urjii (*) qaban hunda guuti!")

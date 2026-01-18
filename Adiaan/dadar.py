import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF

# ================= 1. SETUP & CONFIG =================
# Folder maqaa "Adiaan" jedhu keessa jiraachuu isaa mirkaneessi
LOGO_PATH = "Adiaan/logo.png" 
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if 'pdf_to_download' not in st.session_state: st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state: st.session_state.pdf_name = ""

# ================= 2. CORE FUNCTIONS =================

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border bareedaa
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Header - LOGO
    try:
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, 92, 15, 26)
    except:
        pdf.set_y(25); pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')

    pdf.set_y(45); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 8, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 8, "WAAJJIRA LAFAA", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Arial', '', 11)
    pdf.cell(0, 5, f"Lakk. Galmee: DAD/WL/{datetime.now().year}/____", ln=False, align='L')
    pdf.cell(0, 5, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    
    pdf.ln(10); pdf.set_font('Arial', 'B', 13); pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "SUBJECT: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C', fill=True)
    
    # Ibsa kaffaltii
    kaffaltii_ibsa = "2. Kaffaltii Liizii waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina." if data['gosa_qabiyyee'] == "Liizii" else "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina."

    pdf.set_y(95); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    text = (
        f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} "
        f"Qaxana {data['qaxana']} keessatti mana/lafa Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\n"
        f"Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n"
        f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} guutummaatti kaffalaniiru.\n"
        f"{kaffaltii_ibsa}\n"
        f"3. Lafni/Manni kun DHORKAA MANA MURTII ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n"
        f"Kanaafuu, maamilli kun dhimma {data['dhimma']} raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, "
        f"waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina."
    )
    pdf.multi_cell(170, 8, text, align='L')
    
    pdf.set_y(230); pdf.set_font('Arial', 'B', 12)
    pdf.cell(110); pdf.cell(0, 7, "Maqaa Itti Gaafatamaa:", ln=True)
    pdf.cell(110); pdf.cell(0, 7, "Mallattoo: _________________", ln=True)
    pdf.cell(110); pdf.cell(0, 7, "(Chaappaa Waajjiraa)", ln=True)
    
    return pdf.output(dest='S').encode('latin-1'))
# ================= 3. UI LAYOUT =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

# Formii Galmeessaa
st.header("📝 Galmee fi Qophii Clearance")

if st.session_state.pdf_to_download:
    st.success("📄 Clearance qophaa'eera!")
    st.download_button("📥 IRRA BUUFADHU (PDF)", st.session_state.pdf_to_download, st.session_state.pdf_name, "application/pdf")
    if st.button("Galmee Haaraa"): 
        st.session_state.pdf_to_download = None; st.rerun()

with st.form("clearance_form", clear_on_submit=True):
    st.subheader("Odeeffannoo Maamilaa fi Qabiyyee")
    c1, c2 = st.columns(2)
    m_maqaa = c1.text_input("Maqaa Maamilaa *")
    m_araddaa = c2.text_input("Araddaa *")
    m_qaxana = c1.text_input("Lakk. Qaxana *")
    m_kaartaa = c2.text_input("Lakk. Kaartaa *")
    
    m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii (Permit)"])
    m_bara = c2.text_input("Bara Gibiraa Xumurame (Fkn: 2017)")
    
    m_dhimma = c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee", "Waraqaa Ragaa"])
    m_kaffaltii = c2.number_input("Kaffaltii Tajaajilaa (ETB)", min_value=0.0)
    
    st.write("---")
    # DHORKAA CHECK
    st.warning("⚠️ Mirkaneessa Seeraa")
    m_dhorkaa_bilisa = st.checkbox("Lafni/Manni kun Dhorkaa Mana Murtii fi Injunction kamirrayyuu bilisa ta'uu isaa nan mirkaneessa.")
    
    m_ogeessa = st.text_input("Ogeessa Galmeesse *")

    if st.form_submit_button("💾 GALMEESSI FI PDF UUMI"):
        if m_maqaa and m_kaartaa and m_dhorkaa_bilisa:
            data_map = {
                'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana,
                'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma,
                'gosa_qabiyyee': m_gosa
            }
            st.session_state.pdf_to_download = create_clearance_pdf(data_map)
            st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
            st.success("Galmeen milkaa'eera! PDF gubbaatti dhufeera.")
            st.rerun()
        elif not m_dhorkaa_bilisa:
            st.error("⚠️ Hubachiisa: Dhorkaa irraa bilisa ta'uu isaa osoo hin mirkaneessin Clearance uumuun hin danda'amu!")
        else:
            st.error("⚠️ Maaloo odeeffannoo guutuu galchi!")


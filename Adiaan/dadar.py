import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF
from PIL import Image  # Rakkoo gosa fayilaa furuuf kan dabalame

# ================= 1. SETUP & CONFIG =================
LOGO_FILE = "waajjira_logo.png" 
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if 'pdf_to_download' not in st.session_state: st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state: st.session_state.pdf_name = ""

# ================= 2. CORE FUNCTIONS =================

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # 1. HEADER - LOGO (ERROR-PROOF)
    if os.path.exists(LOGO_FILE):
        try:
            # Gosa fayilaa sirreessuuf (PNG/JPG mismatch furuuf)
            img = Image.open(LOGO_FILE)
            if img.mode in ("RGBA", "P"): # Yoo duubbiin isaa calaqqisiiftuu ta'e
                img = img.convert("RGB")
            img.save("temp_logo.jpg", "JPEG")
            pdf.image("temp_logo.jpg", 90, 15, 30)
        except Exception as e:
            st.error(f"Logo uumuun hin danda'amne: {e}")
            pdf.ln(20)
    else:
        pdf.ln(20)

    pdf.set_y(48)
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 8, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "WAAJJIRA LAFAA", ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font('Arial', '', 11)
    pdf.set_x(20)
    pdf.cell(0, 5, f"Lakk. Galmee: DAD/WL/{datetime.now().year}/____", ln=False, align='L')
    pdf.set_x(20)
    pdf.cell(170, 5, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    
    # 2. SUBJECT (CLEAN)
    pdf.ln(10)
    pdf.set_font('Arial', 'BU', 13)
    pdf.cell(0, 10, "SUBJECT: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    
    # 3. BODY TEXT
    pdf.set_y(95)
    pdf.set_font('Arial', '', 12)
    kaffaltii_ibsa = "2. Kaffaltii Liizii waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina." if data['gosa_qabiyyee'] == "Liizii" else "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina."

    pdf.set_x(20)
    text = (f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} "
            f"Qaxana {data['qaxana']} keessatti mana/lafa Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\n"
            f"Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n"
            f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} guutummaatti kaffalaniiru.\n"
            f"{kaffaltii_ibsa}\n"
            f"3. Lafni/Manni kun DHORKAA MANA MURTII ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n"
            f"Kanaafuu, maamilli kun dhimma {data['dhimma']} raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, "
            f"waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina.")
    pdf.multi_cell(170, 8, text, align='L')
    
    # 4. SIGN SECTION
    pdf.set_y(235)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_x(120)
    pdf.cell(0, 7, "Maqaa Itti Gaafatamaa:", ln=True)
    pdf.set_x(120)
    pdf.cell(0, 7, "Mallattoo: _________________", ln=True)
    pdf.set_x(120)
    pdf.cell(0, 7, "(Chaappaa Waajjiraa)", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI LAYOUT =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

# SIDEBAR: UPLOAD LOGO
st.sidebar.header("⚙️ Qindaa'ina")
uploaded_logo = st.sidebar.file_uploader("Mallattoo Waajjiraa (Logo) Ol-kaasi", type=['png', 'jpg', 'jpeg'])
if uploaded_logo is not None:
    with open(LOGO_FILE, "wb") as f:
        f.write(uploaded_logo.getbuffer())
    st.sidebar.success("✅ Logoon milkaa'inaan jijjiirameera!")

# MAIN UI
st.header("📝 Galmee fi Qophii Clearance")

if st.session_state.pdf_to_download:
    st.success("📄 Clearance qophaa'eera!")
    st.download_button("📥 IRRA BUUFADHU (PDF)", st.session_state.pdf_to_download, st.session_state.pdf_name, "application/pdf")
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
    m_ogeessa = c2.text_input("Ogeessa Galmeesse *")
    
    st.warning("⚠️ Mirkaneessa Seeraa")
    m_dhorkaa_bilisa = st.checkbox("Lafni/Manni kun Dhorkaa Mana Murtii irraa bilisa ta'uu isaa nan mirkaneessa.")

    if st.form_submit_button("💾 GALMEESSI FI PDF UUMI"):
        if m_maqaa and m_kaartaa and m_dhorkaa_bilisa:
            data_map = {'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 'gosa_qabiyyee': m_gosa}
            # Amma RuntimeError sun hin uumamu
            st.session_state.pdf_to_download = create_clearance_pdf(data_map)
            st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
            st.rerun()
        else:
            st.error("⚠️ Maaloo odeeffannoo guutuu galchi, dhorkaa bilisa ta'uus mirkaneessi!")

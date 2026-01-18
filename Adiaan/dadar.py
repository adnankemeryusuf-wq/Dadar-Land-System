import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF

# ================= 1. SETUP & CONFIG =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# Session State: Download akka hin badneef
if 'pdf_to_download' not in st.session_state: st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state: st.session_state.pdf_name = ""

# ================= 2. FUNCTIONS =================
def create_clearance_pdf(name, araddaa, qaxana, services, nagahee_lakk):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.5)
    pdf.rect(10, 10, 190, 277)
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 90, 15, 25)
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'U', 14)
    pdf.cell(0, 10, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.set_y(90)
    pdf.set_font('Arial', '', 12)
    pdf.set_x(20)
    date_str = datetime.now().strftime('%d/%m/%Y')
    text = (
        f"Waraqaan ragaa kun Obbo/Adde {str(name).upper()}, Araddaa {araddaa}, "
        f"Qaxana {qaxana} keessatti tajaajila argachaa turaniif kan kennameedha.\n\n"
        f"Maamilli kun kaffaltii tajaajila gosa '{services}' jedhamaniif "
        f"Lakk. Nagahee {nagahee_lakk} kaffaltii barbaachisu hunda raawwatanii waan xumuraniif, "
        f"guyyaa har'aa ({date_str}) ragaa qulqullinaa kana akka tajaajiluuf waajjirri keenya kenneeraaf."
    )
    pdf.multi_cell(170, 10, text, align='L')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI LAYOUT =================
st.set_page_config(page_title="Dadar Land", layout="wide")

# --- KUTAA DOWNLOAD (GUUTUMMAATTI GUBBAATTI) ---
if st.session_state.pdf_to_download:
    st.success("📄 WARAQAAN RAGAA (CLEARANCE) QOPHAA'EERA!")
    st.download_button(
        label="📥 AS CUQAASII IRRA BUUFADHU (DOWNLOAD PDF)",
        data=st.session_state.pdf_to_download,
        file_name=st.session_state.pdf_name,
        mime="application/pdf",
        key="top_download_button"
    )
    if st.button("Qulqulleessi (Clear Link)"):
        st.session_state.pdf_to_download = None
        st.rerun()
    st.divider()

# --- FORMII GALMEESSAA ---
st.header("📝 Galmee Tajaajilaa Haaraa")
GATII_DICT = {"📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"]}
selected_cats = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))

details, d_fees = [], {}
for cat in selected_cats:
    with st.expander(f"Filannoo {cat}", expanded=True):
        subs = st.multiselect(f"Tajaajiloota {cat}:", GATII_DICT[cat], key=cat)
        for s in subs:
            details.append(s)
            d_fees[s] = st.number_input(f"Kaffaltii {s}", min_value=0.0, key=f"p_{s}")

with st.form("main_form", clear_on_submit=True):
    st.subheader("Odeeffannoo Maamilaa")
    c1, c2 = st.columns(2)
    m_maqaa = c1.text_input("Maqaa Maamilaa *")
    m_araddaa = c2.text_input("Araddaa *")
    m_qaxana = c1.text_input("Qaxana")
    m_nagahee_lakk = c2.text_input("Lakk. Nagahee *")
    m_ogeessa = c1.text_input("Ogeessa Raawwate *")
    
    submit = st.form_submit_button("💾 GALMEESSI FI KUUSI")
    
    if submit:
        if m_maqaa and m_araddaa and details:
            # 1. PDF Uumuu (Yoo Clearance filatame)
            if "Waraqaa Ragaa (Clearance)" in details:
                pdf_bytes = create_clearance_pdf(m_maqaa, m_araddaa, m_qaxana, ", ".join(details), m_nagahee_lakk)
                st.session_state.pdf_to_download = pdf_bytes
                st.session_state.pdf_name = f"Clearance_{m_maqaa}.pdf"
                st.success("✅ Galmeen kuufameera! Download linkii gubbaatti mul'atu fayyadami.")
                st.rerun() # Gubbaatti akka mul'atuuf appii lammata hojjeta
            else:
                st.success(f"✅ Galmeen {m_maqaa} milkaa'eera!")
        else:
            st.error("⚠️ Maaloo odeeffannoo guutuu galchi!")

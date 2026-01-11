import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

USER_NAME = "admin"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"

# Logoon kee maqaa 'logo.png' jedhuun folder koodiin kun jiru keessa jiraachuu qaba
LOGO_PATH = "logo.png" 

# --- 2. CSS STYLE (UI AMMAYYAA) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .header-box { 
        text-align: center; padding: 25px; 
        background: linear-gradient(135deg, #1f4e78, #3b71a3); 
        color: white; border-radius: 15px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stMetric { 
        background: white; padding: 20px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #1f4e78;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKSHIINIIWWAN ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border Miidhagaa
    pdf.set_draw_color(31, 78, 120)
    pdf.set_line_width(2.5)
    pdf.rect(10, 10, 277, 190)

    # --- LOGO SARTIFIKETII IRRATTII ---
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=133, y=15, w=30) # Gidduu gubbaatti
    
    pdf.ln(38)
    
    # Title - Bilingual
    pdf.set_font('Arial', 'B', 26)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 15, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'ANNUAL AWARD CERTIFICATE', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    
    # Content - Afaan Oromoo
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, f"Badhaasni kun ogeessa kabajamaa:", ln=True, align='C')
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 15, name.upper(), ln=True, align='C')
    
    pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 10, f"Waggaa {year} keessa tajaajila quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank}ffaa ta'uu keessaniif qophaa'e.", align='C')
    
    # Content - English
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 12)
    pdf.multi_cell(0, 8, f"In recognition of your outstanding performance and dedicated service throughout the year {year}, ranking at level {rank}.", align='C')
    
    # Signature Section (Obbo Aqiil Abdujaliil)
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_xy(30, 165)
    pdf.cell(100, 7, "__________________________", ln=True, align='L')
    pdf.set_x(30)
    pdf.cell(100, 7, "Obbo Aqiil Abdujaliil", ln=True, align='L')
    pdf.set_font('Arial', '', 10)
    pdf.set_x(30)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa / Office Head", ln=True, align='L')

    return pdf.output(dest='S').encode('latin-1')

# --- 4. MAIN INTERFACE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login UI
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown('<div style="background:white; p-5; border-radius:15px; padding:30px; box-shadow:0 4px 10px rgba(0,0,0,0.1)">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.header("Dadar Land Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # Sidebar Logo
    with st.sidebar:
        if os.path.exists(LOGO_PATH): 
            st.image(LOGO_PATH, use_container_width=True)
        menu = ["🏠 Dashboard", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)

    # Header Logo & Title
    st.markdown('<div class="header-box">', unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 4])
    with col_l:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
    with col_r:
        st.markdown("<h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        st.write("### Tajaajila Galmeessuun itti fufa...")
        st.info(f"Guyyaa Hardhaa: {to_ethiopian(datetime.now())}")

    elif choice == "📊 Gabaasa & Sartifiketii":
        st.subheader("🎓 Sartifiketii Ogeessaa Qopheessi")
        c_name = st.text_input("Maqaa Ogeessaa")
        c_rank = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
        c_year = st.text_input("Waggaa (E.C)", "2018")
        
        if st.button("🎨 GENERATE PDF"):
            if c_name:
                pdf_bytes = generate_certificate(c_name, c_rank, c_year)
                st.download_button("📥 Sartifiketii Buufadhu", pdf_bytes, f"{c_name}_Award.pdf", "application/pdf")
                st.balloons()

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

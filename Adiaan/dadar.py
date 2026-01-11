import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

USER_NAME = "admin"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "logo.png"  # Folder koodiin jiru keessa 'logo.png' kaayi

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
    .stButton>button {
        background-color: #1f4e78; color: white; border-radius: 8px; width: 100%;
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
    pdf.set_draw_color(31, 78, 120)
    pdf.set_line_width(2.5)
    pdf.rect(10, 10, 277, 190)

    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=133, y=15, w=30)
    
    pdf.ln(38)
    pdf.set_font('Arial', 'B', 26); pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 15, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', 'B', 18); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'ANNUAL AWARD CERTIFICATE', ln=True, align='C')
    
    pdf.ln(10); pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 16); pdf.cell(0, 10, f"Badhaasni kun ogeessa kabajamaa:", ln=True, align='C')
    pdf.set_font('Arial', 'B', 22); pdf.cell(0, 15, name.upper(), ln=True, align='C')
    
    pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 10, f"Waggaa {year} keessa tajaajila quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank}ffaa ta'uu keessaniif qophaa'e.", align='C')
    
    pdf.ln(20); pdf.set_font('Arial', 'B', 13); pdf.set_xy(30, 165)
    pdf.cell(100, 7, "__________________________", ln=True, align='L')
    pdf.set_x(30); pdf.cell(100, 7, "Obbo Aqiil Abdujaliil", ln=True, align='L')
    pdf.set_font('Arial', '', 10); pdf.set_x(30); pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa / Office Head", ln=True, align='L')

    return pdf.output(dest='S').encode('latin-1')

# --- 4. MAIN INTERFACE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN UI ---
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown('<div style="background:white; padding:30px; border-radius:15px; box-shadow:0 4px 10px rgba(0,0,0,0.1); margin-top:50px; text-align:center;">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.header("Dadar Land System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogooggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- APP NAVIGATION ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        st.title("Admin Panel")
        choice = st.radio("Filannoo:", ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Sartifiketii", "🚪 Logout"])

    # --- HEADER ---
    st.markdown(f'<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1><p>{to_ethiopian(datetime.now())}</p></div>', unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        st.subheader("Baga Nagaan Dhuftan")
        col1, col2, col3 = st.columns(3)
        col1.metric("Galmee Har'aa", "12", "+2")
        col2.metric("Ogeessota", "8", "Active")
        col3.metric("Tajaajila", "4", "Types")

    elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa")
        with st.form("galmee_form"):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
            bilbila = c1.text_input("Lakk. Bilbilaa")
            tajaajila = c2.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jijjiirraa Maqaa", "Lizio", "Gibira"])
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("Galmeessi"):
                if maqaa and bilbila:
                    st.success(f"{maqaa} galmeeffameera!")
                    st.balloons()
                else: st.warning("Guutuu galchi!")

    elif choice == "📊 Sartifiketii":
        st.subheader("🎓 Sartifiketii Ogeessaa Qopheessi")
        c_name = st.text_input("Maqaa Ogeessaa")
        c_rank = st.selectbox("Sadarkaa", ["1", "2", "3"])
        c_year = st.text_input("Waggaa (E.C)", "2018")
        if st.button("🎨 PDF QOPHEESSI"):
            if c_name:
                pdf_bytes = generate_certificate(c_name, c_rank, c_year)
                st.download_button("📥 Sartifiketii Buufadhu", pdf_bytes, f"{c_name}_Award.pdf", "application/pdf")
            else: st.error("Maqaa galchi!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

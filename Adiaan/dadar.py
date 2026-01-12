import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dadar Land System V9.9", layout="wide", page_icon="🏢")

USER_NAME, PASS_WORD = "admin", "1234"
DATA_FILE = "dadar_data.csv"
# Mirkaneessi: Logo-n kee maqaa 'logo.png' jedhuun folder koodii kana bira jiru keessa jiraachuu qaba.
LOGO_PATH = "logo.png" if os.path.exists("logo.png") else None

# --- 2. HELPER FUNCTIONS ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def generate_certificate(name, rank, year):
    # FPDF Landscape format
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Salphaa fi bareedaa)
    pdf.set_draw_color(31, 78, 120)
    pdf.set_line_width(2.5)
    pdf.rect(10, 10, 277, 190)
    
    # Border keessaa (Double line effect)
    pdf.set_line_width(0.5)
    pdf.rect(12, 12, 273, 186)

    # Logo
    if LOGO_PATH:
        pdf.image(LOGO_PATH, x=133, y=15, w=30)
    
    pdf.ln(40)
    
    # Title - Afaan Oromoo
    pdf.set_font('Times', 'B', 28)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 15, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    
    # Title - English
    pdf.set_font('Times', 'B', 18)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'ANNUAL AWARD CERTIFICATE', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    
    # Body Text
    pdf.set_font('Times', '', 16)
    pdf.cell(0, 10, f"Badhaasni kun ogeessa kabajamaa:", ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, name.upper(), ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font('Times', '', 15)
    pdf.multi_cell(0, 10, f"Waggaa {year} keessa tajaajila quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank} ta'uu keessaniif qophaa'e.", align='C')
    
    # Digital Seal / Badge Placeholder (Optional visual)
    # pdf.set_draw_color(184, 134, 11) # Gold color
    # pdf.ellipse(240, 150, 30, 30, 'D')

    # Signature Section
    pdf.set_font('Times', 'B', 14)
    pdf.set_xy(30, 160)
    pdf.cell(100, 7, "__________________________", ln=True, align='L')
    pdf.set_x(30)
    pdf.cell(100, 7, "Obbo Aqiil Abdujaliil", ln=True, align='L')
    pdf.set_font('Times', '', 11)
    pdf.set_x(30)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa / Office Head", ln=True, align='L')
    
    # Date in Certificate
    pdf.set_xy(200, 167)
    pdf.set_font('Times', '', 12)
    pdf.cell(60, 7, f"Guyyaa: {to_ethiopian(datetime.now())}", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .header-box { text-align: center; padding: 25px; background: linear-gradient(135deg, #1f4e78, #3b71a3); color: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #1f4e78; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA HANDLING ---
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Guyyaa", "Maqaa", "Bilbila", "Dhimma", "Kafaltii"])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

# --- 5. MAIN INTERFACE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div style="background:white; padding:30px; border-radius:15px; box-shadow:0 4px 10px rgba(0,0,0,0.1)">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=120)
        st.header("Dadar Land Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)
        st.divider()
        st.info(f"📅 {to_ethiopian(datetime.now())}")

    st.markdown('<div class="header-box

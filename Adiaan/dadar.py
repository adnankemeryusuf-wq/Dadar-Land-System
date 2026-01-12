import streamlit as st
import os
import requests
import pandas as pd
import qrcode
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send" 
DEVICE_ID = "1" 
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)
# --- 2. CSS STYLE (UI BAREEDAA) ---
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
    .login-card { 
        max-width: 450px; margin: auto; padding: 40px; 
        background: white; border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.15); 
        text-align: center;
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
    
    # Border (Double Frame)
    pdf.set_draw_color(31, 78, 120)
    pdf.set_line_width(2.5)
    pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(0.5)
    pdf.rect(12, 12, 273, 186)

    # --- 🖼️ LOGO SARTIFIKETII IRRATTII ---
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=135, y=15, w=28) # Gidduu gubbaatti
    
    pdf.ln(38)
    
    # Title - Bilingual
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 12, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'ANNUAL AWARD CERTIFICATE', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    
    # Content
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, f"Badhaasni kun ogeessa kabajamaa:", ln=True, align='C')
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 15, name.upper(), ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font('Arial', '', 14)
    txt_or = f"Waggaa {year} keessa tajaajila quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank}ffaa ta'uu keessaniif qophaa'e."
    pdf.multi_cell(0, 10, txt_or, align='C')
    
    # Signature: Obbo Aqiil Abdujaliil
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_xy(35, 165)
    pdf.cell(100, 7, "__________________________", ln=True, align='L')
    pdf.set_x(35)
    pdf.cell(100, 7, "Obbo Aqiil Abdujaliil", ln=True, align='L')
    pdf.set_font('Arial', '', 10)
    pdf.set_x(35)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa / Office Head", ln=True, align='L')

    return pdf.output(dest='S').encode('latin-1')

# --- 4. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- 🖼️ LOGIN PAGE WITH LOGO ---
    st.markdown('<br><br>', unsafe_allow_html=True)
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): 
            st.image(LOGO_PATH, width=120)
        st.header("Dadar Land System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI / LOGIN", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username/Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. MAIN INTERFACE ---
    
    # --- 🖼️ SIDEBAR WITH LOGO ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH): 
            st.image(LOGO_PATH, use_container_width=True)
        st.markdown("<h2 style='text-align: center;'>Dadar Land</h2>", unsafe_allow_html=True)
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Funaansa", menu)
        st.divider()
        st.info(f"📅 {to_ethiopian(datetime.now())}")

    # --- 🖼️ HEADER WITH LOGO ---
    st.markdown('<div class="header-box">', unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 6])
    with col_l:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
    with col_r:
        st.markdown("<h1 style='margin-bottom:0;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:1.2rem;'>Sistama Bulchiinsa Ragaa fi Galmee Ammayyaa</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- DASHBOARD ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            c1, c2, c3 = st.columns(3)
            c1.metric("👥 Abbootii Dhimmaa", len(df))
            c2.metric("💰 Galii Waligalaa", f"{df.iloc[:, -1].astype(float).sum():,.2f} ETB")
            c3.metric("📈 Status", "Hojirra Jira ✅")
            
            st.write("### 🕒 Galmeewwan Dhiyoo")
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("Ragaan galmaa'e hin jiru.")

    # --- GABAASA & CERTIFICATE ---
    elif choice == "📊 Gabaasa & Sartifiketii":
        st.subheader("🎓 Sartifiketii Badhaasaa Qopheessi")
        c_name = st.text_input("Maqaa Ogeessaa")
        c_rank = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
        c_year = st.text_input("Waggaa (E.C)", "2017")
        
        if st.button("🎨 SARTIFIKETII UUMI"):
            if c_name:
                pdf_bytes = generate_certificate(c_name, c_rank, c_year)
                st.download_button("📥 PDF Buufadhu", pdf_bytes, f"{c_name}_Award.pdf", "application/pdf")
                st.balloons()
            else: st.warning("Maaloo maqaa galchi.")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

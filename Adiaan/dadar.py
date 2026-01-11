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

# --- 2. CSS STYLE (UI HAWWATAO) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .header-box { 
        text-align: center; 
        padding: 30px; 
        background: linear-gradient(90deg, #1f4e78, #2e75b6); 
        color: white;
        border-radius: 15px; 
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #1f4e78;
    }
    .login-card { 
        max-width: 400px; margin: auto; padding: 40px; 
        background: white; border-radius: 15px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
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
    
    # Border Miidhagaa
    pdf.set_draw_color(31, 78, 120)
    pdf.set_line_width(3)
    pdf.rect(5, 5, 287, 200)
    pdf.set_line_width(1)
    pdf.rect(7, 7, 283, 196)

    # Logo
    if LOGO_PATH:
        pdf.image(LOGO_PATH, x=130, y=12, w=35)
    
    pdf.ln(40)
    
    # Title (Bilingual)
    pdf.set_font('Arial', 'B', 26)
    pdf.cell(0, 12, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, '(ANNUAL AWARD CERTIFICATE)', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    
    # Body Oromo
    pdf.set_font('Arial', '', 16)
    text_oromo = f"Badhaasni kun ogeessa kabajamaa {name.upper()}f waggaa {year} keessa tajaajila " \
                 f"quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank}ffaa waan ta'aniif kenname."
    pdf.multi_cell(0, 10, text_oromo, align='C')
    
    pdf.ln(5)
    
    # Body English
    pdf.set_font('Arial', 'I', 14)
    text_english = f"This certificate is awarded to {name.upper()} in recognition of their " \
                   f"outstanding performance and dedication, ranking {rank} in the year {year}."
    pdf.multi_cell(0, 10, text_english, align='C')
    
    # Signature Section
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "__________________________", ln=True, align='C')
    pdf.cell(0, 8, "Obbo Aqiil Abdujaliil", ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 6, "Itti Gaafatamaa Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.cell(0, 6, "(Head of Dadar City Land Administration Office)", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# --- 4. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<br><br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=100)
        st.header("Dadar Land System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI / LOGIN"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username/Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. MAIN INTERFACE ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.title("Dadar Land")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.sidebar.selectbox("Funaansa", menu)
        st.divider()
        st.write(f"📅 **Guyyaa:** {to_ethiopian(datetime.now())}")

    # Header section
    st.markdown(f"""
        <div class="header-box">
            <h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>
            <p>Sistama Bulchiinsa Gabaasa fi Galmee Ammayyaa</p>
        </div>
        """, unsafe_allow_html=True)

    # --- DASHBOARD (Hawwataa) ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            total_rev = df.iloc[:, -1].astype(float).sum()
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h3>👥 Abbootii Dhimmaa</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><h3>💰 Galii Waligalaa</h3><h2>{total_rev:,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h3>✅ Status</h3><h2>Hojirra jira</h2></div>', unsafe_allow_html=True)
            
            st.write("### 📈 Haala Hojii (Visual)")
            # Bar chart gabaabaa
            df_chart = df[5].value_counts()
            st.bar_chart(df_chart)

            st.write("### 🕒 Galmeewwan Dhiyoo")
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("Ragaan galmaa'e hin jiru.")

    # --- SARTIFIKETII SECTION ---
    elif choice == "📊 Gabaasa & Sartifiketii":
        st.subheader("📊 Gabaasa fi Sartifiketii Ogeessaa")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("Gabaasa Excel Telegram irratti erguuf:")
            if st.button("🚀 GABAASA EXCEL ERGI"):
                # (Logic kee kaniin duraa itti fufa...)
                st.success("Gabaasni ergameera!")
        
        with col2:
            st.info("Sartifiketii Ogeessa Waggaa:")
            name_og = st.text_input("Maqaa Ogeessaa")
            rank_og = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
            
            if st.button("🎓 SARTIFIKETII GENERATE"):
                if name_og:
                    cert_pdf = generate_certificate(name_og, rank_og, "2016/2017")
                    st.download_button("📥 Sartifiketii Buufadhu", cert_pdf, f"Sartifiketii_{name_og}.pdf", "application/pdf")
                    st.balloons()
                else:
                    st.warning("Maaloo maqaa ogeessaa galchi.")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

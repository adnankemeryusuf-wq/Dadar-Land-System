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

USER_NAME = "Lafa2026"
PASS_WORD = "Dadar@2026"
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

# --- 2. CSS CUSTOM STYLE (HALLUU FI MIIDHAGSITUU) ---
st.markdown("""
    <style>
    /* Background guutuu */
    .stApp { background-color: #f8fafc; }
    
    /* Header Box - Gradient Miidhagaa */
    .header-box { 
        text-align: center; padding: 50px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
        color: white; border-radius: 25px; margin-bottom: 40px;
        box-shadow: 0 15px 30px rgba(30, 58, 138, 0.2);
    }
    
    /* Metric Cards - Bifa Professional */
    .metric-card {
        background: white; padding: 30px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border-top: 5px solid ##15803d; /* Halluu Guldii (Gold) */
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-8px); }
    .metric-card h4 { color: #15803d; margin-bottom: 10px; font-size: 1.1rem; }
    .metric-card h2 { color: ##15803d; font-size: 2.2rem; font-weight: 800; }

    /* Login Card */
    .login-card { 
        max-width: 450px; margin: auto; padding: 60px; 
        background: white; border-radius: 30px; 
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15); 
        text-align: center; border: 1px solid #e2e8f0;
    }
    
    /* Buttons - Custom Style */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white; font-weight: bold; border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background: #1e40af; box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4); }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #f1f5f9; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKSHIINIIWWAN (HELPERS) ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # Border Miidhagaa (Navy & Gold)
    pdf.set_draw_color(30, 58, 138) 
    pdf.set_line_width(4)
    pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(212, 175, 55) # Gold
    pdf.set_line_width(1.5)
    pdf.rect(13, 13, 271, 184)

    if LOGO_PATH: pdf.image(LOGO_PATH, x=133, y=18, w=30)
    
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 36)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 15, 'SARTIFIKETII KABAJAA', ln=True, align='C')
    
    pdf.ln(15)
    pdf.set_font('Arial', '', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Badhaasni kun ogeessa gahumsa qabuuf kenname:', ln=True, align='C')
    
    pdf.ln(8)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(184, 134, 11) # Gold text
    pdf.cell(0, 20, name.upper(), ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    content = f"Waggaa {year} keessa tajaajila gaarii fi gahumsa qabuun hojjechuun badhaasa sadarkaa {rank}ffaa waan ta'aniif qophaa'e."
    pdf.multi_cell(0, 10, content, align='C')
    
    pdf.set_xy(180, 170)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(80, 7, "_______________________", ln=True, align='C')
    pdf.set_x(180)
    pdf.cell(80, 7, "Obbo Aqiil Abdujaliil", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SEENSA (AUTHENTICATION) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<br><br><br>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=120)
        st.markdown("<h2 style='color:#15803d; margin-top:15px;'>Dadar Land Administration Customer Registration system</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#15803d;'>Maaloo ragaa kee galchuun seeni</p>", unsafe_allow_html=True)
        u = st.text_input("Username", placeholder="Maqaa kee...")
        p = st.text_input("Password", type="password", placeholder="Fungulaa...")
        if st.button("SEENI / LOGIN"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. MAIN UI ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.markdown("<h3 style='text-align:center; color:#15803d;'>Dadar Land Administration Customer Registration system</h3>", unsafe_allow_html=True)
        st.divider()
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Menu Filadhu", menu)
        st.info(f"📅 Hardha: {to_ethiopian(datetime.now())}")

    # Header section
    st.markdown(f"""
        <div class="header-box">
            <h1 style='margin:0; font-weight:800; font-size:2.8rem;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>
            <p style='font-size:1.4rem; opacity:0.9; font-weight:300;'>Sistama Bulchiinsa Ragaa fi Galmee Ammayyaa</p>
        </div>
        """, unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            
            # Metric Cards Miidhagaa
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h4>👥 Abbootii Dhimmaa</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2:
                rev = df.iloc[:, -1].astype(float).sum()
                st.markdown(f'<div class="metric-card"><h4>💰 Galii Waligalaa</h4><h2>{rev:,.0f} <small style="font-size:1rem;">ETB</small></h2></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h4>✅ Status</h4><h2>Active</h2></div>', unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.subheader("🕒 Galmeewwan Dhiyoo")
                st.dataframe(df.tail(10), use_container_width=True)
            with col_r:
                st.subheader("📊 Gosa Tajaajilaa")
                st.bar_chart(df[5].value_counts(), color="#1e3a8a")
        else:
            st.info("Ragaan galmaa'e hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        st.markdown("<div style='background:white; padding:40px; border-radius:25px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        st.subheader("📝 Ragaa Abbaa Dhimmaa Galmeessi")
        with st.form("MyForm", clear_on_submit=True):
            cl1, cl2 = st.columns(2)
            with cl1:
                ad = st.text_input("👤 Maqaa Abbaa Dhimmaa")
                ar = st.text_input("📍 Araddaa")
                wi = st.text_input("🏢 Wirtuu")
            with cl2:
                gs = st.selectbox("🛠️ Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Gibira"])
                og = st.text_input("👨‍💼 Maqaa Ogeessaa")
                k_wal = st.number_input("💵 Kafaltii Waligalaa", 0.0)
            
            if st.form_submit_button("✅ GALMEE MIRKANEEESSI"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                line = f"{now}|{ad}|{ar}|{wi}|-|{gs}|{og}|-|Hardha|0|0|0|{k_wal}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                st.success(f"Ragaan '{ad}' milkiin galmaa'eera!")
                st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📄 Gabaasa Gurguddaa", "🎓 Sartifiketii Badhaasaa"])
        
        with tab1:
            st.subheader("Gabaasa Excel Buufadhu")
            if os.path.exists(DATA_FILE):
                df_view = pd.read_csv(DATA_FILE, sep="|", header=None)
                st.dataframe(df_view)
                st.button("🚀 GABAASA TELEGRAM-ITTI ERGI")
        
        with tab2:
            st.subheader("Sartifiketii Miidhagaa Uumi")
            c_name = st.text_input("Maqaa Ogeessaa")
            c_rank = st.selectbox("Sadarkaa Argatan", ["1ffaa", "2ffaa", "3ffaa"])
            c_year = st.text_input("Waggaa (E.C)", "2017")
            if st.button("🎨 SARTIFIKETII GENERATE"):
                if c_name:
                    pdf_out = generate_certificate(c_name, c_rank, c_year)
                    st.download_button("📥 Buufadhu (PDF)", pdf_out, f"{c_name}_Award.pdf")
                    st.balloons()

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()









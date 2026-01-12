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
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

# --- 2. CSS CUSTOM STYLE (MIIDHAGSITUU GURGUDDAA) ---
st.markdown("""
    <style>
    /* Background qulqulluu */
    .stApp { background-color: #f4f7f9; }
    
    /* Header bifa ammayyaa */
    .header-box { 
        text-align: center; padding: 45px; 
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); 
        color: white; border-radius: 25px; margin-bottom: 35px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    
    /* Card-wwan lakkoofsaa */
    .metric-card {
        background: white; padding: 30px; border-radius: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        border-top: 8px solid #1f4e78;
        text-align: center; transition: 0.3s;
    }
    .metric-card:hover { transform: scale(1.03); box-shadow: 0 12px 20px rgba(0,0,0,0.1); }

    /* Login Card */
    .login-card { 
        max-width: 480px; margin: auto; padding: 50px; 
        background: white; border-radius: 30px; 
        box-shadow: 0 20px 50px rgba(0,0,0,0.1); 
        text-align: center; border: 1px solid #ececec;
    }
    
    /* Button style */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(90deg, #1f4e78, #2e75b6);
        color: white; font-weight: bold; border: none;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
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
    pdf.set_line_width(4)
    pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(218, 165, 32) # Gold
    pdf.set_line_width(1.5)
    pdf.rect(13, 13, 271, 184)

    if LOGO_PATH: pdf.image(LOGO_PATH, x=133, y=18, w=30)
    
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 35)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 15, 'SARTIFIKETII KABAJAA', ln=True, align='C')
    
    pdf.ln(15)
    pdf.set_font('Arial', '', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Badhaasni kun ogeessa gahumsa qabuuf kenname:', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 30)
    pdf.set_text_color(184, 134, 11) # Gold
    pdf.cell(0, 20, name.upper(), ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 10, f"Waggaa {year} keessa tajaajila gaarii fi amanamummaa qabuun tajaajilaa waan turtaniif badhaasa sadarkaa {rank}ffaa argattanii jirtu.", align='C')
    
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
        if LOGO_PATH: st.image(LOGO_PATH, width=140)
        st.markdown("<h2 style='color:#1f4e78;'>Dadar Land System</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:gray;'>Maaloo ragaa kee galchi</p>", unsafe_allow_html=True)
        u = st.text_input("Username", placeholder="Maqaa ogeessaa...")
        p = st.text_input("Password", type="password", placeholder="Fungulaa...")
        if st.button("SEENI / LOGIN"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR & MENU ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.markdown("<h3 style='text-align:center;'>Dadar Admin</h3>", unsafe_allow_html=True)
        st.divider()
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Menu Filadhu", menu)
        st.info(f"📅 Hardha: {to_ethiopian(datetime.now())}")

    # Header Box
    st.markdown(f"""
        <div class="header-box">
            <h1 style='margin:0; font-size: 2.5rem;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>
            <p style='font-size:1.2rem; opacity:0.8;'>Sistama Bulchiinsa Ragaa fi Galmee Ammayyaa</p>
        </div>
        """, unsafe_allow_html=True)

    # --- DASHBOARD ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            
            # Metric Cards Miidhagaa
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h4 style="color:gray;">👥 Abbootii Dhimmaa</h4><h1 style="color:#1f4e78;">{len(df)}</h1></div>', unsafe_allow_html=True)
            with c2:
                rev = df.iloc[:, -1].astype(float).sum()
                st.markdown(f'<div class="metric-card"><h4 style="color:gray;">💰 Galii Waligalaa</h4><h1 style="color:#28a745;">{rev:,.0f} <small style="font-size:15px;">ETB</small></h1></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h4 style="color:gray;">✅ Status</h4><h1 style="color:#17a2b8;">Active</h1></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_l, col_r = st.columns([1.5, 1])
            with col_l:
                st.subheader("📊 Gabaasa Gosa Tajaajilaa")
                chart_data = df[5].value_counts()
                st.bar_chart(chart_data, color="#1f4e78")
            with col_r:
                st.subheader("🕒 Galmee Dhiyoo")
                st.dataframe(df.tail(8)[[1, 5, 12]].rename(columns={1: "Maqaa", 5: "Gosa", 12: "Kafaltii"}), use_container_width=True)
        else:
            st.warning("Ragaan galmaa'e hin jiru.")

    # --- GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        st.markdown("<div style='background:white; padding:40px; border-radius:20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        st.subheader("📝 Ragaa Abbaa Dhimmaa Galmeessi")
        with st.form("AddRecord", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                ad = st.text_input("👤 Maqaa Abbaa Dhimmaa")
                ar = st.text_input("📍 Araddaa")
                wi = st.text_input("🏢 Wirtuu")
            with f2:
                gs = st.selectbox("🛠️ Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Gibira", "Hacuufama"])
                og = st.text_input("👨‍💼 Maqaa Ogeessaa")
                k_wal = st.number_input("💵 Kafaltii Waligalaa (ETB)", min_value=0.0)
            
            if st.form_submit_button("✅ GALMEE MIRKANEEESSI"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                line = f"{now}|{ad}|{ar}|{wi}|-|{gs}|{og}|-|Hardha|0|0|0|{k_wal}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                st.success(f"Ragaan '{ad}' milkiin galmaa'eera!")
                st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- GABAASA & SARTIFIKETII ---
    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📁 Gabaasa Gurguddaa", "🎓 Sartifiketii Badhaasaa"])
        
        with tab1:
            st.subheader("Excel Gabaasa Buufadhu")
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE, sep="|", header=None)
                st.dataframe(df)
                st.button("🚀 GABAASA TELEGRAM-ITTI ERGI")
            
        with tab2:
            st.subheader("Sartifiketii Ogeessaa Qopheessi")
            c_name = st.text_input("Maqaa Ogeessaa")
            c_rank = st.selectbox("Sadarkaa Argatan", ["1ffaa", "2ffaa", "3ffaa"])
            c_year = st.text_input("Waggaa (E.C)", "2017")
            if st.button("🎨 SARTIFIKETII UUMI"):
                if c_name:
                    pdf_bytes = generate_certificate(c_name, c_rank, c_year)
                    st.download_button("📥 Sartifiketii PDF Buufadhu", pdf_bytes, f"{c_name}_Award.pdf")
                    st.balloons()
                else: st.error("Maaloo maqaa galchi!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

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
LOGO_PATH = "logo.png" 

# --- 2. CSS CUSTOM STYLE (MIIDHAGSITUU) ---
st.markdown("""
    <style>
    /* Bakka duubaa (Background) */
    .stApp { background-color: #f0f4f7; }
    
    /* Header Box */
    .header-box { 
        text-align: center; padding: 40px; 
        background: linear-gradient(135deg, #1f4e78, #2e75b6); 
        color: white; border-radius: 20px; margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] { font-size: 28px; color: #1f4e78; }
    .metric-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-bottom: 6px solid #1f4e78;
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); }

    /* Login Card */
    .login-card { 
        max-width: 450px; margin: auto; padding: 50px; 
        background: white; border-radius: 25px; 
        box-shadow: 0 15px 40px rgba(0,0,0,0.12); 
        text-align: center; border: 1px solid #ddd;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3em;
        background-color: #1f4e78; color: white; font-weight: bold;
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
    
    # Border Miidhagaa (Double Frame)
    pdf.set_draw_color(31, 78, 120) # Blue
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(218, 165, 32) # Gold
    pdf.set_line_width(1)
    pdf.rect(13, 13, 271, 184)

    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=133, y=18, w=30)
    
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 15, 'SARTIFIKETII BADHAASA OGEESSAA', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Badhaasni kun kabajaaf kan kenname ogeessa:', ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(184, 134, 11) # Dark Gold
    pdf.cell(0, 20, name.upper(), ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font('Arial', '', 16)
    pdf.set_text_color(0, 0, 0)
    content = f"Waggaa {year} keessa tajaajila gaarii fi gahumsa qabuun hojjechuun badhaasa sadarkaa {rank}ffaa waan ta'aniif qophaa'e."
    pdf.multi_cell(0, 10, content, align='C')
    
    # Signature: Obbo Aqiil Abdujaliil
    pdf.set_xy(180, 165)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(80, 7, "_______________________", ln=True, align='C')
    pdf.set_x(180)
    pdf.cell(80, 7, "Obbo Aqiil Abdujaliil", ln=True, align='C')
    pdf.set_font('Arial', '', 11)
    pdf.set_x(180)
    pdf.cell(80, 5, "Itti Gaafatamaa Waajjiraa", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# --- 4. SEENSA (AUTHENTICATION) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<br><br><br>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=130)
        st.markdown("<h2 style='color:#1f4e78;'>Dadar Land Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username", placeholder="Maqaa kee...")
        p = st.text_input("Password", type="password", placeholder="Fungulaa...")
        if st.button("SEENI / LOGIN"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maaloo ragaa sirrii galchi!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. MAIN UI ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        st.markdown("<h3 style='text-align:center;'>Dadar Administration</h3>", unsafe_allow_html=True)
        st.divider()
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Menu Filadhu", menu)
        st.info(f"📅 Hardha: {to_ethiopian(datetime.now())}")

    # Header section
    st.markdown(f"""
        <div class="header-box">
            <h1 style='margin:0;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>
            <p style='font-size:1.3rem; opacity:0.9;'>Sistama Bulchiinsa Ragaa fi Galmee Ammayyaa</p>
        </div>
        """, unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            
            # Metric Cards
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h4>👥 Abbootii Dhimmaa</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2:
                rev = df.iloc[:, -1].astype(float).sum()
                st.markdown(f'<div class="metric-card"><h4>💰 Galii Waligalaa</h4><h2>{rev:,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h4>✅ Status</h4><h2>Hojirra Jira</h2></div>', unsafe_allow_html=True)
            
            st.write("---")
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.subheader("🕒 Galmeewwan Dhiyoo")
                st.dataframe(df.tail(8), use_container_width=True)
            with col_r:
                st.subheader("📊 Gosa Tajaajilaa")
                st.bar_chart(df[5].value_counts())
        else:
            st.info("Ragaan galmaa'e hin jiru. Maaloo 'Galmee Haaraa' irra deemi.")

    elif choice == "📝 Galmee Haaraa":
        with st.container():
            st.markdown("<div style='background:white; padding:30px; border-radius:15px;'>", unsafe_allow_html=True)
            st.subheader("📝 Ragaa Haaraa Galmeessi")
            with st.form("MyForm", clear_on_submit=True):
                cl1, cl2 = st.columns(2)
                with cl1:
                    ad = st.text_input("Maqaa Abbaa Dhimmaa")
                    ar = st.text_input("Araddaa")
                    wi = st.text_input("Wirtuu")
                with cl2:
                    gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Gibira"])
                    og = st.text_input("Maqaa Ogeessaa")
                    k_wal = st.number_input("Kafaltii Waligalaa", 0.0)
                
                if st.form_submit_button("✅ GALMEESSI"):
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    line = f"{now}|{ad}|{ar}|{wi}|-|{gs}|{og}|-|Hardha|0|0|0|{k_wal}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    st.success(f"Ragaan {ad} milkiin galmaa'eera!")
            st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📄 Gabaasa Excel", "🎓 Sartifiketii Badhaasaa"])
        
        with tab1:
            st.subheader("Gabaasa Toora Telegram")
            if st.button("🚀 GABAASA TELEGRAM-ITTI ERGI"):
                st.toast("Gabaasni ergameera!", icon="✅")
        
        with tab2:
            st.subheader("Sartifiketii Miidhagaa Uumi")
            c_name = st.text_input("Maqaa Ogeessaa")
            c_rank = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
            c_year = st.text_input("Waggaa (E.C)", "2017")
            if st.button("🎨 SARTIFIKETII GENERATE"):
                if c_name:
                    pdf_out = generate_certificate(c_name, c_rank, c_year)
                    st.download_button("📥 Buufadhu (PDF)", pdf_out, f"{c_name}_Award.pdf")
                    st.balloons()

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
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


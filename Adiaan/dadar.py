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
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "logo.png" # Faayilli kun folder kee keessa jiraachuu qaba

# --- 2. CSS STYLE (MODERN & ATTRACTIVE) ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .header-box { 
        text-align: center; padding: 30px; 
        background: linear-gradient(135deg, #1f4e78, #2e75b6); 
        color: white; border-radius: 15px; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .stMetric { 
        background: white; padding: 20px; border-radius: 12px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-bottom: 5px solid #1f4e78;
    }
    .login-card { 
        max-width: 450px; margin: auto; padding: 40px; 
        background: white; border-radius: 20px; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.2); 
    }
    div.stButton > button:first-child {
        background-color: #1f4e78; color: white; border-radius: 8px;
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
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(0.5)
    pdf.rect(12, 12, 273, 186)

    # Logo on Certificate
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=135, y=15, w=25)
    
    pdf.ln(35)
    
    # Titles - Bilingual
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 12, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'ANNUAL AWARD CERTIFICATE', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    
    # Body Text - Afaan Oromoo
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, f"Badhaasni kun ogeessa kabajamaa:", ln=True, align='C')
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 15, name.upper(), ln=True, align='C')
    
    pdf.set_font('Arial', '', 14)
    txt_or = f"Waggaa {year} keessa tajaajila quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank} ta'uu keessaniif qophaa'e."
    pdf.multi_cell(0, 10, txt_or, align='C')
    
    # Body Text - English
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 12)
    txt_en = f"In recognition of your outstanding performance and dedicated service throughout the year {year}, ranking at level {rank}."
    pdf.multi_cell(0, 8, txt_en, align='C')
    
    # Signature: Obbo Aqiil Abdujaliil
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_xy(30, 160)
    pdf.cell(100, 7, "__________________________", ln=True, align='L')
    pdf.set_x(30)
    pdf.cell(100, 7, "Obbo Aqiil Abdujaliil", ln=True, align='L')
    pdf.set_font('Arial', '', 10)
    pdf.set_x(30)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa / Office Head", ln=True, align='L')

    return pdf.output(dest='S').encode('latin-1')

def send_telegram_file(file_data, file_name, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, files={'document': (file_name, file_data)})
    except: st.error("Telegram error!")

# --- 4. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<br><br>', unsafe_allow_html=True)
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.subheader("🏢 Dadar Land System Login")
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
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.sidebar.selectbox("Main Menu", menu)
        st.divider()
        st.info(f"📅 Guyyaa: {to_ethiopian(datetime.now())}")

    # Header Section
    st.markdown(f"""
        <div class="header-box">
            <h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>
            <p>Sistama Bulchiinsa Ragaa fi Galmee Ammayyaa</p>
        </div>
        """, unsafe_allow_html=True)

    # --- DASHBOARD ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            total_rev = df.iloc[:, -1].astype(float).sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("👥 Abbootii Dhimmaa", len(df))
            c2.metric("💰 Galii Waligalaa", f"{total_rev:,.2f} ETB")
            c3.metric("📈 Status", "Hojirra Jira ✅")
            
            st.write("### 🕒 Galmeewwan Dhiyoo")
            st.dataframe(df.tail(10), use_container_width=True)
            
            st.write("### 📊 Gosa Tajaajilaa")
            st.bar_chart(df[5].value_counts())
        else:
            st.info("Ragaan galmaa'e hin jiru.")

    # --- GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Haaraa Galchi")
        with st.form("RegForm", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                bad = st.text_input("Bilbila AD")
            with c2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Gibira"])
                og = st.text_input("Maqaa Ogeessaa")
                wi = st.text_input("Wirtuu")
            with c3:
                gb = st.date_input("Guyyaa Beellamaa")
                sb = st.time_input("Sa'aatii")
                k_tot = st.number_input("Kafaltii Waligalaa", 0.0)

            if st.form_submit_button("✅ GALMEESSI"):
                if ad and bad:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    line = f"{now_str}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|-|{gb} {sb}|0|0|0|{k_tot}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    
                    # QR Code
                    qr_data = f"AD: {ad}\nTajaajila: {gs}\nBeellama: {gb}\nKafaltii: {k_tot} ETB"
                    qr_img = qrcode.make(qr_data)
                    buf = BytesIO()
                    qr_img.save(buf, format="PNG")
                    st.image(buf.getvalue(), caption="QR Code Mirkaneessaa", width=200)
                    st.success(f"Galmee {ad} milkiin xumurameera!")
                else: st.warning("Maaloo maqaa fi bilbila galchi.")

    # --- GABAASA & CERTIFICATE ---
    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📊 Gabaasa Excel", "🎓 Sartifiketii Badhaasaa"])
        
        with tab1:
            st.write("Gabaasa Excel Telegram irratti erguuf ykn buufachuuf:")
            if st.button("🚀 GABAASA GENERATE GODHI"):
                if os.path.exists(DATA_FILE):
                    df = pd.read_csv(DATA_FILE, sep="|", header=None)
                    output = BytesIO()
                    df.to_excel(output, index=False)
                    send_telegram_file(output.getvalue(), "Gabaasa_Dadar.xlsx", "Gabaasa Galmee")
                    st.success("Gabaasni Telegram irratti ergameera!")
                else: st.error("Ragaan hin jiru.")

        with tab2:
            st.write("### Sartifiketii Ogeessa Waggaa Qopheessi")
            c_name = st.text_input("Maqaa Ogeessaa")
            c_rank = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
            c_year = st.text_input("Waggaa (E.C)", "2017")
            
            if st.button("🎨 SARTIFIKETII UUMI"):
                if c_name:
                    pdf_data = generate_certificate(c_name, c_rank, c_year)
                    st.download_button("📥 Sartifiketii Buufadhu (PDF)", pdf_data, f"{c_name}_Award.pdf")
                    st.balloons()
                else: st.error("Maaloo maqaa galchi!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

import streamlit as st
import os
import requests
import pandas as pd
import qrcode
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
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
        st.header("Dadar Land Administration Customer Registration System")
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
        st.title("Dadar Land Administration Customer Registration System")
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
import streamlit as st

# --- 1. QINDAA'INA STYLE (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 10px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (LOGIN CHECK) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

import streamlit as st
import pandas as pd
import os
import requests
import qrcode
from datetime import datetime, timedelta
from io import BytesIO
import openpyxl

# --- CONFIGURATION ---
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "logo.png" # Faayila logo kee asitti dabaladhu

# --- FUNCTIONS ---
def send_telegram_file(file_data, file_name, caption=""):
    """Telegram irratti faayila erga"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        files = {'document': (file_name, file_data)}
        payload = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
        requests.post(url, data=payload, files=files, timeout=20)
    except Exception as e:
        st.error(f"Telegram Error: {e}")

def get_data():
    """Daataa txt irraa gara Pandas DataFrame-tti jijjiira"""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    try:
        # Sararoota txt keessaa dubbisuu
        df = pd.read_csv(DATA_FILE, sep="|", header=None, encoding="utf-8")
        # Maqaa kutaalee (Columns) - Akka koodii kee isa duraatti
        df.columns = ["Guyyaa", "Maqaa_AD", "Araddaa", "Wirtuu", "Bilbila", "Tajaajila", 
                      "Ogeessa", "B_Ogeessa", "Beellama", "K_Kartaa", "K_User", "K_Jij", "Waligala"]
        return df
    except:
        return pd.DataFrame()

# --- MAIN UI ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN SCREEN ---
    st.title("🔐 Login - Dadar Land System")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("SEENI"):
        if u == "admin" and p == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Username ykn Password dogoggora!")
else:
    # --- APP NAVIGATION ---
    menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Telegram", "🔍 Barbaadi (Search)"]
    choice = st.sidebar.selectbox("Fula Filadhu", menu)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    df_main = get_data()

    # --- 1. DASHBOARD ---
    if choice == "🏠 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df_main.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Baay'ina Galmee", len(df_main))
            col2.metric("Waligala Galii", f"{df_main['Waligala'].sum():,.2f} ETB")
            col3.metric("Tajaajila Har'aa", len(df_main[df_main['Guyyaa'].str.contains(datetime.now().strftime("%Y-%m-%d"))]))
            
            st.subheader("Galmeewwan Dhihoo")
            st.dataframe(df_main.tail(10), use_container_width=True)
        else:
            st.info("Hamma ammaatti ragaan galmeeffame hin jiru.")

    # --- 2. GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        st.subheader("Galmee Abbaa Dhimmaa Haaraa")
        with st.form("RegForm", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                wi = st.text_input("Wirtuu")
                bad = st.text_input("Bilbila AD")
            with c2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizio", "TOT", "Gibira"])
                og = st.text_input("Maqaa Ogeessa")
                gb = st.date_input("Guyyaa Beellamaa")
                sb = st.time_input("Sa'aatii")
            
            st.write("--- Kafaltiiwwan ---")
            k1 = st.number_input("Kafaltii Kartaa", min_value=0.0)
            k2 = st.number_input("Kafaltii User", min_value=0.0)
            k3 = st.number_input("Kafaltii Jijjiirraa", min_value=0.0)
            
            if st.form_submit_button("Galmeessi"):
                waligala = k1 + k2 + k3
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                # Save to Text File
                line = f"{now_str}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|'-'|{gb} {sb}|{k1}|{k2}|{k3}|{waligala}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(line)
                
                # Generate QR for Display
                qr_img = qrcode.make(f"AD: {ad}, Kafaltii: {waligala} ETB")
                buf = BytesIO()
                qr_img.save(buf, format="PNG")
                
                st.success("Milkiin galmeeffameera!")
                st.image(buf.getvalue(), caption=f"QR Code {ad}", width=200)

    # --- 3. GABAASA & TELEGRAM ---
    elif choice == "📊 Gabaasa & Telegram":
        st.subheader("Gabaasa Excel Uumi & Ergi")
        if not df_main.empty:
            # Excel Buffer
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_main.to_excel(writer, index=False, sheet_name='Gabaasa')
            excel_data = output.getvalue()

            st.download_button(label="📥 Excel Buufadhu", data=excel_data, 
                               file_name=f"Gabaasa_{datetime.now().date()}.xlsx")
            
            if st.button("🚀 Gabaasa Telegram-itti Ergi"):
                send_telegram_file(excel_data, "Gabaasa_Dadar.xlsx", f"Gabaasa Guyyaa: {datetime.now().date()}")
                st.success("Gabaasni hoggantatti ergameera!")
        else:
            st.warning("Ragaan erguuf jiru hin jiru.")

    # --- 4. SEARCH ---
    elif choice == "🔍 Barbaadi (Search)":
        st.subheader("🔍 Barbaadi")
        search_term = st.text_input("Maqaa ykn Bilbila galchi:")
        if search_term:
            results = df_main[df_main.apply(lambda row: search_term.lower() in row.astype(str).str.lower().values, axis=1)]
            st.write(f"Bu'aa {len(results)} argameera:")
            st.dataframe(results)










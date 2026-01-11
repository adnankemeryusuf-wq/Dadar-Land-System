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
import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill
import plotly.express as px

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System V8", layout="wide", page_icon="🏢")

# Credential-ota kee
USER_NAME, PASS_WORD = "admin", "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
TRACCAR_URL = "http://localhost:8082/" # Localhost yoo ta'e server irratti jijjiirama
SMS_TOKEN = "08a96817-22ab-4660-b866-b7647dbcbf82"
DB_FILE = "galmee_abbaa_dhimmaa.txt"
LOGO_PATH = "logo.png"

# --- 2. FUNKSHIINIIWWAN GARGAARTUU ---

def load_data():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    data_list = []
    with open(DB_FILE, "r") as f:
        for line in f:
            parts = [x.split(":")[1].strip() for x in line.split("|")]
            data_list.append(parts)
    cols = ["ID", "Guyyaa", "Maqaa", "Bilbila", "Araddaa", "Wirtuu", "Dhimma", "Kartaa", "Lizi", "Beellama", "Ogeessa", "Status"]
    return pd.DataFrame(data_list, columns=cols)

def send_ethio_sms(bilbila, ergaa):
    if bilbila.startswith('0'): bilbila = "+251" + bilbila[1:]
    headers = {"Authorization": SMS_TOKEN, "Content-Type": "application/json"}
    payload = {"to": bilbila, "message": ergaa}
    try:
        requests.post(TRACCAR_URL, json=payload, headers=headers, timeout=5)
        return True
    except: return False

def send_telegram_file(file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as doc:
            requests.post(url, files={'document': doc}, data={'chat_id': CHAT_ID_MANAGER, 'caption': "Gabaasa Excel"})
    except: pass

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-header { background: #1f4e78; color: white; padding: 25px; border-radius: 15px; text-align: center; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #1f4e78; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.subheader("Seensa Systemii")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogooggora!")
else:
    # Sidebar
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = st.radio("HOJJEDHU", ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa & Telegram", "🚪 Logout"])
        st.info(f"System V8.0\nUser: {USER_NAME}")

    df = load_data()

    if menu == "🏠 Dashboard":
        st.markdown('<div class="header-header"><h1>Waajjira Lafaa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)
        st.write("")
        
        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card">Total Galmee<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2: 
            rev = df['Kartaa'].astype(float).sum() + df['Lizi'].astype(float).sum() if not df.empty else 0
            st.markdown(f'<div class="metric-card">Total Galii<br><h2>{rev:,.0f} ETB</h2></div>', unsafe_allow_html=True)
        with c3:
            pend = len(df[df['Status'] == 'Pending']) if not df.empty else 0
            st.markdown(f'<div class="metric-card">Harka Irra Jiru<br><h2>{pend}</h2></div>', unsafe_allow_html=True)
        with c4:
            fin = len(df[df['Status'] == 'Finished']) if not df.empty else 0
            st.markdown(f'<div class="metric-card">Xumuraman<br><h2>{fin}</h2></div>', unsafe_allow_html=True)

        if not df.empty:
            col_left, col_right = st.columns(2)
            with col_left:
                fig = px.pie(df, names='Dhimma', title="Gosa Tajaajilaa", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            with col_right:
                st.subheader("Galmee dhiyoo")
                st.table(df[['ID', 'Maqaa', 'Dhimma', 'Status']].tail(5))

    elif menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Fi Ogeessaa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
                bilbila_a = st.text_input("Bilbila AD")
                araddaa = st.text_input("Araddaa")
                wirtuu = st.text_input("Wirtuu")
            with col2:
                dhimma = st.selectbox("Dhimma", ["Kartaa", "Lizi", "Jijjiirraa Maqaa", "Safara", "Gibira"])
                beellama = st.date_input("Guyyaa Beellamaa")
                kartaa = st.number_input("Kafaltii Kartaa", value=0.0)
                lizi = st.number_input("Kafaltii Lizi", value=0.0)
            
            ogeessa = st.text_input("Maqaa Ogeessaa (Safaraaf yoo ta'e)")
            bilbila_o = st.text_input("Bilbila Ogeessaa")

            if st.form_submit_button("Galmeessi & SMS Ergi"):
                guyyaa_ammaa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                id_sys = datetime.now().strftime("%f")[:4]
                
                # Save to Text File
                dataa = (f"ID:{id_sys} | Guyyaa:{guyyaa_ammaa} | Maqaa:{maqaa} | Bilbila:{bilbila_a} | "
                         f"Araddaa:{araddaa} | Wirtuu:{wirtuu} | Dhimma:{dhimma} | Kartaa:{kartaa} | "
                         f"Lizi:{lizi} | Beellama:{beellama} | Ogeessa:{ogeessa} | Status:Pending\n")
                
                with open(DB_FILE, "a") as f: f.write(dataa)
                
                # SMS to Ogeessa if Safara
                if "safara" in dhimma.lower() and bilbila_o:
                    msg_o = f"Kabajamaa {ogeessa}, Ajaja Safaraa AD {maqaa}, Bilbila: {bilbila_a} isiniif kennameera."
                    send_ethio_sms(bilbila_o, msg_o)
                
                st.success(f"Galmeeffameera! ID: {id_sys}")
                st.balloons()

    elif menu == "✅ Xumurame Beeksisi":
        st.subheader("Dhimma Xumurame Beeksisi")
        id_input = st.text_input("ID Abbaa Dhimmaa Galchi:")
        if st.button("Xumurameera jedhi"):
            if not df.empty:
                rows = []
                found = False
                with open(DB_FILE, "r") as f:
                    lines = f.readlines()
                for line in lines:
                    if f"ID:{id_input}" in line and "Status:Pending" in line:
                        parts = [x.split(":")[1].strip() for x in line.split("|")]
                        # parts[2]=Maqaa, parts[3]=Bilbila, parts[6]=Dhimma
                        msg = f"Kabajamaa {parts[2]}, Dhimmi keessan ({parts[6]}) xumurameera. Guyyaa beellamaa dhuftanii fudhadhaa. Dadar Land."
                        send_ethio_sms(parts[3], msg)
                        line = line.replace("Status:Pending", "Status:Finished")
                        found = True
                    rows.append(line)
                with open(DB_FILE, "w") as f: f.writelines(rows)
                if found: st.success("SMS ergameera, Status 'Finished' jedhameera.")
                else: st.warning("ID hin argamne ykn duraan xumurameera.")

    elif menu == "📊 Gabaasa & Telegram":
        st.subheader("Excel & Telegram Report")
        if st.button("Excel Uumi & Telegram-itti Ergi"):
            if not df.empty:
                f_name = f"gabaasa_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx"
                df.to_excel(f_name, index=False)
                send_telegram_file(f_name)
                st.success(f"Gabaasni {f_name} uumamee Telegram irratti ergameera!")
            else: st.error("Data'n hin jiru.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

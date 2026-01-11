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
def uumi_excel_gabaasa():
    if not os.path.exists(DB_FILE): 
        print("[!] Data'n hin jiru.")
        return
        
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Gabaasa Galii"
    
    # Mata duree (Headers)
    headers = ["ID", "Guyyaa", "Maqaa", "Bilbila", "Araddaa", "Wirtuu", "Dhimma", "Kartaa", "Lizi", "Beellama", "Ogeessa", "Status"]
    sheet.append(headers)
    
    # Style mata duree (Header styling)
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")

    total_kartaa = 0
    total_lizi = 0
    guyyaa_arraa = datetime.now().strftime("%Y-%m-%d")

    with open(DB_FILE, "r") as f:
        for line in f:
            # Data hiraa (Parsing)
            parts = [x.split(":")[1].strip() for x in line.split("|")]
            
            # Galmee guyyaa arraa qofa calaluu yoo barbaadde (Optional)
            # if guyyaa_arraa not in parts[1]: continue

            sheet.append(parts)
            
            # Herrega Iddaamaa (Calculation)
            # parts[7] = Kartaa, parts[8] = Lizi
            try:
                total_kartaa += float(parts[7])
                total_lizi += float(parts[8])
            except:
                pass # Yoo lakkoofsa hin taane irra darba

    # Sarara Iddaama Waliigalaa (Total Row) dabaluu
    sheet.append([]) # Sarara duwwaa tokko dhiisuuf
    total_row = ["", "", "", "", "", "", "IDDAAMA WALIIGALAA:", total_kartaa, total_lizi, "", "", ""]
    sheet.append(total_row)

    # Style sarara iddaamaa (Make it bold)
    last_row = sheet.max_row
    for cell in sheet[last_row]:
        cell.font = Font(bold=True)
        if cell.column in [7, 8, 9]: # Iddaama qofa irratti halluu dibuuf
            cell.fill = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")

    file_name = f"gabaasa_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    wb.save(file_name)
    send_telegram_report(file_name)
    print(f"[✓] Gabaasni galii waliin qophaa'eera: {file_name}")
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

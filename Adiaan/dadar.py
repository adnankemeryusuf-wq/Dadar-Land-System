import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dadar Land System V9.8", layout="wide", page_icon="🏢")

USER_NAME, PASS_WORD = "admin", "1234"
DATA_FILE = "dadar_data.csv"
LOGO_PATH = "logo.png" if os.path.exists("logo.png") else None

# --- 2. HELPER FUNCTIONS ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(31, 78, 120)
    pdf.set_line_width(2.5)
    pdf.rect(10, 10, 277, 190)

    if LOGO_PATH:
        pdf.image(LOGO_PATH, x=133, y=15, w=30)
    
    pdf.ln(40)
    pdf.set_font('Arial', 'B', 26)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 15, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'ANNUAL AWARD CERTIFICATE', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, f"Badhaasni kun ogeessa kabajamaa:", ln=True, align='C')
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 15, name.upper(), ln=True, align='C')
    
    pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 10, f"Waggaa {year} keessa tajaajila quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank}ffaa ta'uu keessaniif qophaa'e.", align='C')
    
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_xy(30, 165)
    pdf.cell(100, 7, "__________________________", ln=True, align='L')
    pdf.cell(100, 7, "Obbo Aqiil Abdujaliil", ln=True, align='L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa / Office Head", ln=True, align='L')

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
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1.5,1])
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
            else: st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)
        st.divider()
        st.info(f"📅 {to_ethiopian(datetime.now())}")

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    df = load_data()

    if choice == "🏠 Dashboard":
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><h3>👥 Galmee</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h3>💰 Galii</h3><h2>{df["Kafaltii"].sum():,.2f}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><h3>📅 Guyyaa</h3><h2>{to_ethiopian(datetime.now())[:5]}</h2></div>', unsafe_allow_html=True)
        
        if not df.empty:
            st.write("### 📈 Haala Hojii")
            st.bar_chart(df['Dhimma'].value_counts())
        else:
            st.info("Ragaan galmaa'e hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa")
        with st.form("galmee_form", clear_on_submit=True):
            m_name = st.text_input("Maqaa Guutuu")
            m_phone = st.text_input("Bilbila")
            m_dhimma = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jijjiirraa Maqaa", "Safara", "Lizi"])
            m_price = st.number_input("Kafaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("Galmeessi"):
                new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), m_name, m_phone, m_dhimma, m_price]], 
                                        columns=["Guyyaa", "Maqaa", "Bilbila", "Dhimma", "Kafaltii"])
                new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.success(f"{m_name} galmeeffameera!")
                st.balloons()

    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📊 Gabaasa Mamiilaa", "🎓 Sartifiketii Ogeessaa"])
        
        with tab1:
            st.dataframe(df, use_container_width=True)
            st.download_button("Download Excel", df.to_csv().encode('utf-8'), "gabaasa.csv", "text/csv")
        
        with tab2:
            st.subheader("🎓 Sartifiketii Qopheessi")
            
            c_name = st.text_input("Maqaa Ogeessaa")
            c_rank = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
            c_year = st.text_input("Waggaa (E.C)", "2018")
            
            if st.button("🎨 GENERATE PDF"):
                if c_name:
                    pdf_bytes = generate_certificate(c_name, c_rank, c_year)
                    st.download_button("📥 Sartifiketii Buufadhu", pdf_bytes, f"{c_name}_Award.pdf", "application/pdf")
                    st.balloons()
                else: st.warning("Maaloo maqaa galchi.")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
        import streamlit as st
import os
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. CONFIGURATION (STRICTLY FIRST) ---
st.set_page_config(page_title="Dadar Land System V9.5", layout="wide", page_icon="🏢")

# Credentials & Paths
USER_NAME, PASS_WORD = "admin", "1234"
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send" 
DEVICE_ID = "1" 
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "logo.png" if os.path.exists("logo.png") else None

# --- 2. HELPER FUNCTIONS ---

def to_eth_date(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def send_sms(phone, message):
    try:
        if phone.startswith('0'): phone = "+251" + phone[1:]
        payload = {'token': SMS_TOKEN, 'device': DEVICE_ID, 'to': phone, 'message': message}
        res = requests.post(SMS_URL, data=payload, timeout=7)
        return res.status_code == 200
    except: return False

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # Border
    pdf.set_draw_color(31, 78, 120)
    pdf.set_line_width(3)
    pdf.rect(5, 5, 287, 200)
    # Header
    pdf.set_font('Arial', 'B', 26)
    pdf.ln(30)
    pdf.cell(0, 15, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    pdf.set_font('Arial', 'I', 18)
    pdf.cell(0, 10, '(ANNUAL PERFORMANCE AWARD)', ln=True, align='C')
    pdf.ln(20)
    # Body
    pdf.set_font('Arial', '', 16)
    pdf.multi_cell(0, 10, f"Badhaasni kun ogeessa kabajamaa {name.upper()}f waggaa {year} keessa \n"
                         f"tajaajila quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank}ffaa \n"
                         f"waan ta'aniif kenname.", align='C')
    # Signature
    pdf.ln(30)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "__________________________", ln=True, align='C')
    pdf.cell(0, 10, "Itti Gaafatamaa Waajjiraa", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box { text-align: center; padding: 25px; background: linear-gradient(90deg, #1f4e78, #2e75b6); color: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .metric-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #1f4e78; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIN LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1.2,1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=120)
        st.subheader("Login - Dadar Land System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.title("Main Menu")
        menu = st.radio("Filaa:", ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa & Sartifiketii", "🚪 Logout"])
        st.divider()
        st.info(f"📅 Guyyaa: {to_eth_date(datetime.now())}")
        if menu == "🚪 Logout":
            st.session_state.logged_in = False
            st.rerun()

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1><p>Systemii Bulchiinsa Gabaasa fi Galmee</p></div>', unsafe_allow_html=True)

    # Load Data
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ["Yeroo", "Maqaa", "Araddaa", "Wirtuu", "Bilbila", "Dhimma", "Ogeessa", "B_Ogeessa", "Beellama", "Kartaa", "Lizi", "TOT", "Waligala"]
        except: df = pd.DataFrame()
    else: df = pd.DataFrame()

    # --- ROUTING ---
    if menu == "🏠 Dashboard":
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card">👤 Abbootii Dhimmaa<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card">💰 Galii Waliigalaa<br><h2>{df["Waligala"].sum():,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card">📅 Guyyaa Har\'aa<br><h2>{to_eth_date(datetime.now())[:5]}</h2></div>', unsafe_allow_html=True)
            
            st.write("### 📈 Raawwii Tajaajilaa")
            fig = px.bar(df[5].value_counts(), title="Gosa Tajaajilaa Baay'inaan", labels={'value':'Baay\'ina', 'index':'Gosa'})
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Ragaan galmaa'e hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Haaraa")
        with st.form("RegForm", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ad, bad = st.text_input("Maqaa Abbaa Dhimmaa"), st.text_input("Bilbila AD")
                ar, wi = st.text_input("Araddaa"), st.text_input("Wirtuu")
            with col2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Lizi", "Jijjiirraa Maqaa", "Safara", "Gibira"])
                og, bog = st.text_input("Maqaa Ogeessaa"), st.text_input("Bilbila Ogeessaa")
                beellama = st.text_input("Beellama (Fkn: 2026-02-10)")

            st.write("💰 Kafaltiiwwan")
            k1, k2, k3 = st.columns(3)
            v_k, v_l, v_t = k1.number_input("Kartaa"), k2.number_input("Lizi"), k3.number_input("TOT")

            if st.form_submit_button("✅ GALMEESSI FI SMS ERGI"):
                if ad and bad:
                    total = v_k + v_l + v_t
                    new_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|{bog}|{beellama}|{v_k}|{v_l}|{v_t}|{total}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(new_line)
                    send_sms(bad, f"Kabajamaa {ad}, tajaajila {gs}af galmeeffamtaniittu. Beellama: {beellama}. Dadar Land.")
                    st.success("Milkiin Galmaa'eera!")
                else: st.error("Maaloo ragaa guuti!")

    elif menu == "✅ Xumurame Beeksisi":
        st.subheader("✅ Tajaajila Xumurame Beeksisi")
        if not df.empty:
            search_name = st.selectbox("Maqaa Filadhu", df["Maqaa"].unique())
            mamiila = df[df["Maqaa"] == search_name].iloc[-1]
            if st.button("SMS Xumuraa Ergi"):
                msg = f"Kabajamaa {mamiila['Maqaa']}, tajaajilli keessan ({mamiila['Dhimma']}) xumurameera. Fudhachuu dandeessu. Dadar Land."
                if send_sms(str(mamiila['Bilbila']), msg): st.success("SMS Ergameera!")
                else: st.error("SMS erguun hin danda'amne.")

    elif menu == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📊 Gabaasa Daataa", "🎓 Sartifiketii Ogeessaa"])
        
        with tab1:
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", data=csv, file_name="gabaasa_dadar.csv")
            else: st.info("Ragaan hin jiru.")
            
        with tab2:
            st.write("### Sartifiketii Ogeessa Waggaa Qopheessi")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                name_og = st.text_input("Maqaa Ogeessa Badhaafamu")
                rank_og = st.selectbox("Sadarkaa Badhaasaa", ["1ffaa", "2ffaa", "3ffaa"])
            with col_c2:
                year_og = st.text_input("Waggaa (Fkn: 2017 E.C)", value="2017 E.C")
            
            if st.button("🎓 SARTIFIKETII GENERATE"):
                if name_og:
                    pdf_bytes = generate_certificate(name_og, rank_og, year_og)
                    st.download_button(f"📥 Sartifiketii {name_og} Buufadhu", pdf_bytes, f"Sartifiketii_{name_og}.pdf", "application/pdf")
                    st.balloons()
                else: st.warning("Maaloo maqaa galchi.")

import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

# Constants (Missing in your original code)
USER_NAME, PASS_WORD = "admin", "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "logo.png"
DB_FILE = "dadar_database.txt" # File ragaan itti kuufamu
SMS_TOKEN = "YOUR_SMS_TOKEN_HERE" # Token kee as galchi
TRACCAR_URL = "http://YOUR_SMS_GATEWAY_URL" # URL SMS kee

# --- 2. HELPER FUNCTIONS ---

def load_data():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    data_list = []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                # Seeraan addaan baasuu
                parts = [x.split(":")[1].strip() for x in line.split("|") if ":" in x]
                # Column 15 (Kafaltiiwwan hunda dabalatee)
                if len(parts) == 15:  
                    data_list.append(parts)
            except: continue
    cols = ["ID", "Guyyaa", "Maqaa", "Bilbila", "Araddaa", "Wirtuu", "Dhimma", 
            "Itti_Fay", "Kartaa", "J_Maqaa", "Lizi", "TOT", "Biro", "Beellama", "Ogeessa", "Status"]
    # Column-oonni koodii kee wajjiin akka walsimuuf (16 columns total with status)
    return pd.DataFrame(data_list, columns=cols[:15] + ["Status"])

def send_ethio_sms(bilbila, ergaa):
    if not bilbila: return False
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
            requests.post(url, files={'document': doc}, data={'chat_id': CHAT_ID_MANAGER, 'caption': "Gabaasa Excel Haaraa"})
    except Exception as e:
        st.error(f"Telegram Error: {e}")

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-header { background: #1f4e78; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .metric-card { background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #1f4e78; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.subheader("Seensa Systemii")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = st.radio("HOJJEDHU", ["🏠 Dashboard", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa & Telegram", "🚪 Logout"])
        st.divider()
        st.info(f"Version: 8.1\nAdmin: {USER_NAME}")

    df = load_data()

    if menu == "🏠 Dashboard":
        st.markdown('<div class="main-header"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)
        
        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        if not df.empty:
            total_rev = pd.to_numeric(df['Kartaa'], errors='coerce').sum() + pd.to_numeric(df['Lizi'], errors='coerce').sum()
            with c1: st.markdown(f'<div class="metric-card">Total Galmee<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card">Total Galii<br><h2>{total_rev:,.0f}</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card">Pending<br><h2>{len(df[df["Status"]=="Pending"])}</h2></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="metric-card">Finished<br><h2>{len(df[df["Status"]=="Finished"])}</h2></div>', unsafe_allow_html=True)

        st.divider()
        if not df.empty:
            col_l, col_r = st.columns(2)
            with col_l:
                fig = px.pie(df, names='Dhimma', title="Gosa Tajaajilaa", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            with col_r:
                st.subheader("Galmeewwan Dhihoo")
                st.table(df[['ID', 'Maqaa', 'Dhimma', 'Status']].tail(5))

    elif menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Haaraa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
                bilbila_a = st.text_input("Bilbila AD")
                araddaa = st.text_input("Araddaa")
                wirtuu = st.text_input("Wirtuu")
                ogeessa = st.text_input("Maqaa Ogeessaa")
                bilbila_o = st.text_input("Bilbila Ogeessaa")
            with col2:
                dhimma = st.selectbox("Dhimma", ["Kartaa", "Jijjiirraa Maqaa", "Lizi", "Safara", "Dangaa"])
                beellama = st.date_input("Guyyaa Beellamaa")
                v_itti = st.number_input("Kafaltii Itti Fayyadam", 0.0)
                v_kartaa = st.number_input("Kafaltii Kartaa", 0.0)
                v_j_maqaa = st.number_input("Kafaltii Jijjirraa Maqaa", 0.0)
                v_lizi = st.number_input("Kafaltii Lizi", 0.0)
                v_tot = st.number_input("Kafaltii TOT", 0.0)
                v_biro = st.number_input("Kafaltii Biro", 0.0)

            if st.form_submit_button("Galmeessi & SMS Ergi"):
                id_sys = datetime.now().strftime("%H%M%S")[-4:]
                guyyaa = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Ragaa hunda walitti qabuu
                dataa = (f"ID:{id_sys} | Guyyaa:{guyyaa} | Maqaa:{maqaa} | Bilbila:{bilbila_a} | "
                         f"Araddaa:{araddaa} | Wirtuu:{wirtuu} | Dhimma:{dhimma} | Itti:{v_itti} | "
                         f"Kartaa:{v_kartaa} | JMaqaa:{v_j_maqaa} | Lizi:{v_lizi} | TOT:{v_tot} | "
                         f"Biro:{v_biro} | Beellama:{beellama} | Ogeessa:{ogeessa} | Status:Pending\n")
                
                with open(DB_FILE, "a", encoding="utf-8") as f: f.write(dataa)
                
                # SMS Ogeessaaf (Safara yoo ta'e)
                if "safara" in dhimma.lower() and bilbila_o:
                    send_ethio_sms(bilbila_o, f"Ajaja Safaraa: AD {maqaa}, Bilbila: {bilbila_a}")
                
                st.success(f"Galmee Milkiidhaan xumurameera! ID: {id_sys}")

    elif menu == "✅ Xumurame Beeksisi":
        st.subheader("✅ Dhimma Xumurame Beeksisi")
        id_search = st.text_input("ID Abbaa Dhimmaa Galchi:")
        if st.button("Xumurameera Jedhi"):
            if os.path.exists(DB_FILE):
                lines = []
                found = False
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                with open(DB_FILE, "w", encoding="utf-8") as f:
                    for line in lines:
                        if f"ID:{id_search}" in line and "Status:Pending" in line:
                            line = line.replace("Status:Pending", "Status:Finished")
                            # SMS erguu (Bilbila bakka 4ffaa irra jiru basuun)
                            parts = [x.split(":")[1].strip() for x in line.split("|")]
                            send_ethio_sms(parts[3], f"Kabajamaa {parts[2]}, dhimmi keessan xumurameera.")
                            found = True
                        f.write(line)
                
                if found: st.success("Status jijjiiramee SMS ergameera!")
                else: st.warning("ID hin argamne ykn duraan xumurameera.")

    elif menu == "📊 Gabaasa & Telegram":
        st.subheader("Gabaasa Excel & Telegram")
        if st.button("Gabaasa Ergi"):
            if not df.empty:
                f_name = f"gabaasa_{datetime.now().strftime('%Y%m%d')}.xlsx"
                df.to_excel(f_name, index=False)
                send_telegram_file(f_name)
                st.success("Gabaasni Telegram-itti ergameera!")
            else: st.error("Data'n hin jiru.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
                    



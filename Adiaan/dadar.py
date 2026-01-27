import streamlit as st
import pandas as pd
import os, io, requests
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
LOGO_FILE = "logo_waajjiraa.png" 

# TELEGRAM CONFIG
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #2e7d32; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            text-align: center; border-top: 5px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================

def load_data():
    COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Nagahee_Img']
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(df):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Gabaasa_Dadar')
        output.seek(0)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        files = {'document': ('Gabaasa_Lafa_Dadar.xlsx', output, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        payload = {'chat_id': CHAT_ID_MANAGER, 'caption': f"📊 Gabaasa Hojii Waajjira Lafaa Dadar\nGuyyaa: {datetime.now().strftime('%d/%m/%Y')}"}
        response = requests.post(url, data=payload, files=files)
        return response.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, 12, 12, 25)
        pdf.image(LOGO_FILE, 172, 12, 25)
    
    pdf.set_y(15); pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "WAAJJIRA LAFAA BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(10)
    
    e_date = EthiopianDateConverter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Lakk: DAD/WL/{e_date[0]}/____ \t\t\t\t\t\t Guyyaa: {e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}", ln=True)
    
    pdf.ln(5); pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 12)
    body = (f"Waraqaan ragaa kun Obbo/Adde {data['maqaa'].upper()} Araddaa {data['araddaa']} "
            f"keessatti Lakk. Iddoo (Plot) {data['lakk_iddoo']}, Lakk. Manaa {data['lakk_manaa']} "
            f"fi Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha. "
            f"Maamilli kun kaffaltii gibira waggaa hanga bara {data['bara']} E.C "
            f"guutummaatti kaffalaniiru. Qabiyyeen kun dhorkaa murtii kamirrayyuu "
            f"bilisa ta'uu isaa waajjira keenyaan qulqullaa'ee mirkanaa'eera.")
    pdf.multi_cell(0, 10, body)
    
    pdf.set_y(240); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Itti Gaafatamaa: {data['head_name']}", ln=True)
    pdf.cell(0, 10, "Mallattoo: _________________", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = None

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=150)
        st.title("🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni", use_container_width=True):
            if u == "DAD" and p == "2026": 
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    if os.path.exists(LOGO_FILE): st.sidebar.image(LOGO_FILE, width=100)
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📜 CLEARANCE", "📈 Gabaasa", "Ba'i"])

    # --- CLEARANCE ---
    if menu == "📜 CLEARANCE":
        st.header("📜 Qophii Waraqaa Qulqullinaa")
        if st.session_state.pdf_ready:
            st.success("✅ Waraqaan Qophaa'eera!")
            st.download_button("📥 PDF Buufadhu", st.session_state.pdf_ready, "Clearance_Dadar.pdf", "application/pdf")
            if st.button("🔄 Haaraa Jalqabi"):
                st.session_state.pdf_ready = None
                st.rerun()

        with st.form("clearance_form_updated"):
            c1, c2 = st.columns(2)
            c_name = c1.text_input("Maqaa Maamilaa *")
            c_ara = c2.text_input("Araddaa / Ganda *")
            c_iddoo = c1.text_input("Lakk. Iddoo (Plot No) *") # Dirree haaraa dabalame
            c_mana = c2.text_input("Lakk. Manaa *")
            c_kaartaa = c1.text_input("Lakk. Kaartaa *")
            c_bara = c2.text_input("Bara Gibiraa (E.C) *")
            c_head = st.text_input("Maqaa Itti Gaafatamaa *")
            
            if st.form_submit_button("📄 PDF UUMI"):
                if c_name and c_iddoo and c_kaartaa:
                    clr_data = {
                        'maqaa': c_name, 'araddaa': c_ara, 'lakk_iddoo': c_iddoo,
                        'lakk_manaa': c_mana, 'kaartaa': c_kaartaa, 
                        'bara': c_bara, 'head_name': c_head
                    }
                    st.session_state.pdf_ready = create_clearance_pdf(clr_data)
                    st.rerun()
                else: st.warning("Maaloo dirree '*' qaban guuti!")

    # --- GABAASA & TELEGRAM ---
    elif menu == "📈 Gabaasa":
        st.header("📋 Gabaasa Galmeewwan Hundi")
        if not df.empty:
            st.dataframe(df.drop(columns=['Nagahee_Img']), use_container_width=True)
            if st.button("📤 Gabaasa Telegram-atti Ergi", type="primary"):
                res = send_to_telegram(df)
                if res.get("ok"): st.success("✅ Gabaasni Telegram-atti ergameera!")
                else: st.error("Rakkoo Telegram!")
        else: st.info("Data'n hin jiru.")

    # --- DASHBOARD & OTHERS ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            st.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            fig = px.bar(df, x='Guyyaa', y='Kafaltii_Taj', title="Raawwii Galii")
            st.plotly_chart(fig, use_container_width=True)

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

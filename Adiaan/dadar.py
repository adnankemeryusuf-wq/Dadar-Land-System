import streamlit as st
import pandas as pd
import sqlite3
import os, io, requests, threading, time
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(
    page_title="Dadar Land Administration",
    page_icon="🏢",
    layout="wide"
)

DB_FILE = "dadar.db"
NAGAHEE_DIR = "nagahee_scan"
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID_MANAGER = "YOUR_CHAT_ID"

SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Kaartaa Lafa Qoonnaa"
    ],
    "🏗 Pilaanii & Ijaarsa": [
      "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
       "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo)"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa",
        "Kaffaltii Seeressuu (Regularization)",
        "Adabbii Faallaa Pilaanii"
    ],
}
# ================= DIRECTORY =================
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# ================= CSS =================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg,#f4f7f9,#ffffff); }
div.stForm { background: white; border-radius:15px; padding:25px; box-shadow:0 4px 15px rgba(0,0,0,0.1); }
.stButton button { background-color:#2e7d32; color:white; border:none; padding:8px 15px; border-radius:8px; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# ================= DATABASE =================
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS records(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guyyaa TEXT,
    maqaa TEXT,
    araddaa TEXT,
    qaxana TEXT,
    gosa_taj TEXT,
    ogeessa TEXT,
    kafaltii REAL
)
""")
conn.commit()

# ================= HELPERS =================
def load_data():
    return pd.read_sql_query("SELECT * FROM records", conn)

def save_record(row):
    c.execute("""
    INSERT INTO records(guyyaa, maqaa, araddaa, qaxana, gosa_taj, ogeessa, kafaltii)
    VALUES (?,?,?,?,?,?,?)
    """, row)
    conn.commit()

def get_ec_date():
    # Simplified: just return Gregorian date (replace with EthiopianDateConverter if available)
    now = datetime.now()
    return now.strftime("%d/%m/%Y")

def create_clearance_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.cell(0,10,"MOOTUMMAA NAANNOO OROMIYAA",ln=True,align="C")
    pdf.cell(0,10,"BULCHIINSA MAGAALAA DADAR - WAAJJIRA LAFAA",ln=True,align="C")
    pdf.ln(10)
    pdf.multi_cell(0,8,
        f"Maqaa: {data['maqaa']}\n"
        f"Araddaa: {data['araddaa']}  Qaxana: {data['qaxana']}\n"
        f"Kaartaa: {data['kaartaa']}\n"
        f"Dhimma: {data['dhimma']}\n"
        f"Itti Gaafatamaa: {data['head']}\n"
        f"Guyyaa: {get_ec_date()}"
    )
    return pdf.output(dest="S").encode("latin-1")

def create_excel_report(df, mode):
    df['Date'] = pd.to_datetime(df['guyyaa'], format='%d/%m/%Y', errors='coerce')
    if mode=="daily":
        df = df[df['Date'].dt.date==datetime.now().date()]
        fname="Daily_Report.xlsx"
    else:
        df = df[(df['Date'].dt.month==datetime.now().month)&(df['Date'].dt.year==datetime.now().year)]
        fname="Monthly_Report.xlsx"
    if df.empty: return None
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    out.seek(0)
    return out, fname

def send_to_telegram(file_bytes, filename, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {"document":(filename,file_bytes)}
    data = {"chat_id":CHAT_ID_MANAGER,"caption":caption}
    requests.post(url, files=files, data=data)

# ================= SESSION =================
if 'role' not in st.session_state: st.session_state.role=None
if 'pdf_bytes' not in st.session_state: st.session_state.pdf_bytes=None
if 'pdf_name' not in st.session_state: st.session_state.pdf_name=""

# ================= LOGIN =================
if not st.session_state.role:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    role = st.selectbox("Role",["Admin","Staff"])
    if st.button("Seeni"):
        # example credentials
        if (u=="DAD" and p=="2026" and role=="Admin") or (u=="staff" and p=="1234" and role=="Staff"):
            st.session_state.role=role
            st.success(f"Login {role}")
            st.rerun()
        else:
            st.error("Dogoggora login")

# ================= MAIN APP =================
else:
    st.sidebar.title(f"👤 {st.session_state.role}")
    menu = st.sidebar.radio("MENU", ["📊 Dashboard","📝 Galmee Haaraa","📄 Clearance","📤 Telegram Report"])

    df = load_data()

    # ---------- DASHBOARD ----------
    if menu=="📊 Dashboard":
        st.header("📊 Dashboard")
        if df.empty:
            st.info("Ragaan hin jiru")
        else:
            c1,c2,c3 = st.columns(3)
            c1.metric("💰 Galii",f"{df['kafaltii'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota",len(df))
            c3.metric("👷 Ogeeyyii",df['ogeessa'].nunique())
            fig = px.bar(df.groupby("ogeessa")["kafaltii"].sum().reset_index(), x="ogeessa", y="kafaltii")
            st.plotly_chart(fig,use_container_width=True)

    # ---------- GALMEE HAAARAA ----------
    elif menu=="📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("reg_form"):
            name = st.text_input("Maqaa")
            araddaa = st.text_input("Araddaa")
            qaxana = st.text_input("Qaxana")
            ogeessa = st.text_input("Ogeessa")
            services = st.multiselect("Tajaajila", sum(SERVICE_STRUCTURE.values(),[]))
            fee = st.number_input("Kafaltii", min_value=0.0)
            nagahee = st.file_uploader("Nagahee Scan", type=['jpg','png'])
            if st.form_submit_button("Galmeessi"):
                if name.strip()=="" or not services:
                    st.error("Maqaa fi tajaajila dirqamaa guuti!")
                else:
                    if nagahee:
                        path=os.path.join(NAGAHEE_DIR,f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(path,"wb") as f: f.write(nagahee.getbuffer())
                    row=[datetime.now().strftime('%d/%m/%Y'),name,araddaa,qaxana,", ".join(services),ogeessa,fee]
                    save_record(row)
                    st.success("Galmeeffameera!")

    # ---------- CLEARANCE ----------
    elif menu=="📄 Clearance":
        st.header("📄 Clearance PDF")
        with st.form("clr_form"):
            maqaa = st.text_input("Maqaa")
            araddaa = st.text_input("Araddaa")
            qaxana = st.text_input("Qaxana")
            kaartaa = st.text_input("Kaartaa")
            dhimma = st.text_input("Dhimma")
            head = st.text_input("Itti Gaafatamaa")
            if st.form_submit_button("PDF UUMI"):
                pdf_bytes = create_clearance_pdf({"maqaa":maqaa,"araddaa":araddaa,"qaxana":qaxana,"kaartaa":kaartaa,"dhimma":dhimma,"head":head})
                st.download_button("⬇️ PDF Buusi",pdf_bytes,f"Clearance_{maqaa}.pdf")
                # Telegram
                send_to_telegram(pdf_bytes,f"Clearance_{maqaa}.pdf","📄 Clearance PDF")

    # ---------- TELEGRAM REPORT ----------
    elif menu=="📤 Telegram Report":
        st.header("📤 Telegram Excel Reports")
        if st.button("📊 Daily Excel → Telegram"):
            res = create_excel_report(df,"daily")
            if res:
                send_to_telegram(*res,"📊 Daily Report")
                st.success("Ergameera")
            else:
                st.warning("Ragaan hin jiru")
        if st.button("📈 Monthly Excel → Telegram"):
            res = create_excel_report(df,"monthly")
            if res:
                send_to_telegram(*res,"📈 Monthly Report")
                st.success("Ergameera")
            else:
                st.warning("Ragaan hin jiru")

# ================= AUTO DAILY REPORT THREAD =================
def auto_daily_report():
    while True:
        now=datetime.now()
        if now.hour==0 and now.minute==0:
            df = load_data()
            res = create_excel_report(df,"daily")
            if res:
                send_to_telegram(*res,"📊 Auto Daily Report")
            time.sleep(60)
        time.sleep(30)

threading.Thread(target=auto_daily_report,daemon=True).start()


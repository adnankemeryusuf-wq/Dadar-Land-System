import streamlit as st
import pandas as pd
import sqlite3
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

DB_FILE = "dadar_land_pro.db"
NAGAHEE_DIR = "nagahee_scan"
# Telegram Config
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# CSS Custom Styling
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 15px; padding: 20px; border: 1px solid #2e7d32; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; border-top: 4px solid #2e7d32; }
    .stButton>button { background: #2e7d32; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. DATABASE & HELPERS =================
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS galmee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guyyaa TEXT, maqaa TEXT, araddaa TEXT, qaxana TEXT,
            gosa_taj TEXT, ogeessa TEXT, kafaltii REAL, nagahee_path TEXT
        )
    """)
    conn.commit()
    return conn

def get_ec_date(g=None):
    if g is None: g = datetime.now()
    ec = EthiopianDateConverter.to_ethiopian(g.year, g.month, g.day)
    return f"{ec.day:02d}/{ec.month:02d}/{ec.year}"

def load_data():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM galmee", conn)
    conn.close()
    return df

# ================= 3. PDF & TELEGRAM FUNCTIONS =================
def create_clearance_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align="C")
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR - WAAJJIRA LAFAA", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    
    text = (f"Waraqaan ragaa qulqullinaa kun Obbo/Adde {data['maqaa']}tiif kennameera.\n\n"
            f"Araddaa: {data['araddaa']} | Qaxana: {data['qaxana']}\n"
            f"Dhimma: {data['dhimma']}\n"
            f"Itti Gaafatamaa: {data['head']}\n"
            f"Guyyaa (E.C): {get_ec_date()}")
    
    pdf.multi_cell(0, 10, text)
    return pdf.output(dest="S").encode("latin-1", "replace")

def send_to_telegram(file_bytes, filename, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        res = requests.post(url, files={"document": (filename, file_bytes)}, data={"chat_id": CHAT_ID_MANAGER, "caption": caption})
        return res.status_code == 200
    except: return False

# ================= 4. MAIN APP LOGIC =================
if 'logged' not in st.session_state: st.session_state.logged = False
if 'pdf_bytes' not in st.session_state: st.session_state.pdf_bytes = None

if not st.session_state.logged:
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if (u == "admin" or u == "staff") and p == "2026":
            st.session_state.logged = True
            st.session_state.user = u
            st.rerun()
        else: st.error("Username ykn Password dogoggora!")

else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "📄 Clearance", "📤 Telegram Report", "Ba'i"])

    # ---------- DASHBOARD ----------
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Raawwii Hojii")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['kafaltii'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Walitti qabaa</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['ogeessa'].nunique()}</h2><p>Hojii irra jiran</p></div>", unsafe_allow_html=True)
            
            fig = px.bar(df.groupby("ogeessa")['kafaltii'].sum().reset_index(), x="ogeessa", y="kafaltii", title="Galii Ogeessaan")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)
        else: st.info("Ragaan galmeeffame hin jiru.")

    # ---------- REGISTRATION ----------
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        with st.form("reg_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            og = c2.text_input("Ogeessa Raawwate *")
            taj = st.multiselect("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa", "Jijjiirraa Maqaa", "Adabbii"])
            fee = st.number_input("Kafaltii (ETB)", min_value=0.0)
            nagahee = st.file_uploader("Nagahee Scan (JPG/PNG)", type=["jpg", "png"])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and og:
                    path = ""
                    if nagahee:
                        path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    conn = get_conn()
                    conn.cursor().execute("INSERT INTO galmee (guyyaa, maqaa, araddaa, qaxana, gosa_taj, ogeessa, kafaltii, nagahee_path) VALUES (?,?,?,?,?,?,?,?)",
                                         (datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(taj), og, fee, path))
                    conn.commit(); conn.close()
                    st.success("✅ Galmeeffameera!"); st.balloons()
                else: st.error("Maaloo odeeffannoo dirqamaa (*) guuti")

    # ---------- CLEARANCE ----------
    elif menu == "📄 Clearance":
        st.header("📄 Waraqaa Qulqullinaa (Clearance)")
        with st.form("clr_form"):
            c1, c2 = st.columns(2)
            m_maqaa = c1.text_input("Maqaa Maamilaa")
            m_ara = c2.text_input("Araddaa")
            m_qax = c1.text_input("Qaxana")
            m_dhimma = c2.selectbox("Dhimma", ["Gurgurtaa", "Liqii Bankii", "Kennaa"])
            m_head = st.text_input("Maqaa Itti Gaafatamaa")
            
            if st.form_submit_button("📄 PDF UUMI"):
                st.session_state.pdf_bytes = create_clearance_pdf({"maqaa":m_maqaa, "araddaa":m_ara, "qaxana":m_qax, "dhimma":m_dhimma, "head":m_head})
                st.success("PDF qophaa'eera!")
        
        if st.session_state.pdf_bytes:
            st.download_button("⬇️ PDF Buusi", st.session_state.pdf_bytes, f"Clearance_{datetime.now().second}.pdf", "application/pdf")

    # ---------- TELEGRAM REPORT ----------
    elif menu == "📤 Telegram Report":
        st.header("📤 Gabaasa Telegram tti Ergi")
        if not df.empty:
            if st.button("📊 Daily Excel → Telegram"):
                out = io.BytesIO()
                df.to_excel(out, index=False)
                if send_to_telegram(out.getvalue(), "Gabaasa_Dadar.xlsx", f"Gabaasa Guyyaa: {get_ec_date()}"):
                    st.success("✅ Gabaasaan ergameera!")
                else: st.error("❌ Erguun hin danda'amne.")
        else: st.warning("Ragaan ergaamu hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged = False
        st.rerun()

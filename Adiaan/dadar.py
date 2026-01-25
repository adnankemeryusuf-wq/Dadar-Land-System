import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
CLR_FILE = "clearance_history.txt"
NAGAHEE_DIR = "nagahee_scan"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# Directories uumuu
for folder in [NAGAHEE_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

st.set_page_config(
    page_title="Dadar Land Administration System", 
    page_icon="🏢", 
    layout="wide"
)

# Halluu fi Style (Custom CSS)
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    h1, h2 { color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

COL_NAMES = ['Guyyaa', 'Maqaa', 'Araddaa', 'Qaxana', 'Tajaajila', 'Ogeessa', 'Kafaltii']

# ================= 2. SERVICE LIST (GOSA TAJAAJILAA) =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Kaartaa Lafa Qonnaa"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", "Adabbii Faallaa Pilaanii"
    ],
}

# ================= 3. FUNCTIONS (DATA & PDF) =================
def load_data(f, cols):
    if not os.path.exists(f) or os.stat(f).st_size == 0:
        return pd.DataFrame(columns=cols)
    return pd.read_csv(f, sep="|", names=cols, header=None, encoding='utf-8')

def save_data(df, f):
    df.to_csv(f, sep="|", index=False, header=False, encoding="utf-8")

def create_itemized_receipt(data, items):
    pdf = FPDF(unit='mm', format=(100, 150))
    pdf.add_page()
    pdf.rect(5, 5, 90, 140)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "NAGAHEE KAFFALTII", ln=True, align='C')
    pdf.set_font('Arial', '', 9); pdf.cell(0, 6, f"Maqaa: {data['maqaa']}", ln=True)
    pdf.cell(0, 6, f"Guyyaa: {data['guyyaa']}", ln=True); pdf.ln(5)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(55, 8, " Tajaajila", 1, 0, 'L', True); pdf.cell(25, 8, " ETB", 1, 1, 'R', True)
    for k, v in items.items():
        pdf.cell(55, 8, f" {k[:25]}", 1); pdf.cell(25, 8, f" {v:,.2f}", 1, 1, 'R')
    pdf.set_font('Arial', 'B', 10); pdf.cell(55, 10, " Waliigala", 1, 0, 'R', True); pdf.cell(25, 10, f" {data['total']:,.2f}", 1, 1, 'R', True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN INTERFACE =================
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login - Dadar Land System")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.auth = True; st.rerun()
            else: st.error("Iccitii dogoggora!")
else:
    menu = st.sidebar.radio("📋 DUBBII GURGUDDAA", ["📊 Dashboard", "📝 Galmee & Nagahee", "📄 Clearance", "🏆 Badhaasa", "🔍 Manage"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard & Analytics")
        df = load_data(DATA_FILE, COL_NAMES)
        if not df.empty:
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Maamilaa", len(df))
            c3.metric("📅 Guyyaa Har'aa", datetime.now().strftime('%d/%m/%Y'))
            
            top5 = df.groupby('Tajaajila')['Kafaltii'].sum().sort_values(ascending=False).head(5).reset_index()
            st.plotly_chart(px.bar(top5, x='Kafaltii', y='Tajaajila', orientation='h', title="Tajaajiloota Galii Olaanaa", color='Kafaltii'))
            st.dataframe(df, use_container_width=True)

    # --- REGISTRATION ---
    elif menu == "📝 Galmee & Nagahee":
        st.header("📝 Galmee Maamilaa Haaraa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            m_maqaa = col1.text_input("👤 Maqaa Maamilaa")
            m_ara = col1.text_input("📍 Araddaa")
            m_qax = col2.text_input("🧭 Qaxana")
            m_og = col2.text_input("👷 Maqaa Ogeessaa")
            
            st.markdown("---")
            gosa_gurguddaa = st.selectbox("📂 Gosa Tajaajilaa Filadhu", list(SERVICE_STRUCTURE.keys()))
            t_filatame = st.selectbox("🎯 Tajaajila Tarreeffamaa", SERVICE_STRUCTURE[gosa_gurguddaa])
            m_fee = st.number_input("💸 Kaffaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 GALMEESSI & NAGAHEE UUMI"):
                if m_maqaa:
                    d_now = datetime.now().strftime('%d/%m/%Y')
                    new_rec = [d_now, m_maqaa, m_ara, m_qax, t_filatame, m_og, m_fee]
                    df = load_data(DATA_FILE, COL_NAMES)
                    df = pd.concat([df, pd.DataFrame([new_rec], columns=COL_NAMES)], ignore_index=True)
                    save_data(df, DATA_FILE)
                    
                    pdf = create_itemized_receipt({"maqaa":m_maqaa, "guyyaa":d_now, "total":m_fee}, {t_filatame: m_fee})
                    st.success(f"Galmeen {m_maqaa} milkaayinaan kuufameera!")
                    st.download_button("📥 Nagahee PDF Buufadhu", pdf, f"Nagahee_{m_maqaa}.pdf")

    # --- TELEGRAM REPORT ---
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Gabaasa Excel (Telegram)"):
        df_all = load_data(DATA_FILE, COL_NAMES)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as wr: df_all.to_excel(wr, index=False)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID_MANAGER}, files={'document': ("Report.xlsx", out.getvalue())})
        st.sidebar.success("Gabaasni ergameera!")

import streamlit as st
import pandas as pd
import os, io, requests, uuid
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
# CHAPA_AUTH: Key kee isa 'Secret Key' (chapa.co) irraa argattu asitti galchi
CHAPA_AUTH = "CHASECK_TEST-xxxxxxxxxxxxxxxxxxxx" 
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa', 'Araddaa', 'Qaxana', 'Tajaajila', 'Ogeessa', 'Kafaltii', 'Ref_ID']

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #ddd; }
    .pay-box { background-color:#e1f5fe; padding:20px; border-radius:10px; text-align:center; border: 1px solid #b3e5fc; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. SERVICE LIST =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Waliigaltee Liqii Baankii", "Dhimma Dhala"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"]
}

# ================= 3. FUNCTIONS =================
def load_data(f, cols):
    if not os.path.exists(f) or os.stat(f).st_size == 0:
        return pd.DataFrame(columns=cols)
    return pd.read_csv(f, sep="|", names=cols, header=None, encoding='utf-8')

def save_data(df, f):
    df.to_csv(f, sep="|", index=False, header=False, encoding="utf-8")

def initialize_chapa(amount, name, tx_ref):
    """Linkii kaffaltii Telebirr/CBE/Card uumuu"""
    url = "https://api.chapa.co/v1/transaction/initialize"
    headers = {"Authorization": f"Bearer {CHAPA_AUTH}", "Content-Type": "application/json"}
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": "customer@dadarland.gov.et",
        "first_name": name,
        "tx_ref": tx_ref,
        "callback_url": "https://chapa.co",
        "customization[title]": "Kaffaltii Tajaajila Lafaa Dadar"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res = response.json()
        if response.status_code == 200 and res.get('status') == 'success':
            return res['data']['checkout_url']
        return None
    except: return None

def create_pdf_receipt(data, taj, fee):
    pdf = FPDF(unit='mm', format=(100, 150))
    pdf.add_page()
    pdf.rect(5, 5, 90, 140)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "NAGAHEE KAFFALTII", ln=True, align='C')
    pdf.set_font('Arial', '', 9); pdf.cell(0, 6, f"Maqaa: {data['maqaa']}", ln=True)
    pdf.cell(0, 6, f"Guyyaa: {data['guyyaa']}", ln=True)
    pdf.cell(0, 6, f"Lakk (Ref): {data['ref']}", ln=True); pdf.ln(5)
    pdf.cell(55, 8, f" {taj[:25]}", 1); pdf.cell(25, 8, f" {fee:,.2f}", 1, 1, 'R')
    pdf.set_font('Arial', 'B', 10); pdf.cell(55, 10, " Waliigala", 1, 0, 'R'); pdf.cell(25, 10, f" {fee:,.2f}", 1, 1, 'R')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP =================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = None

if not st.session_state.auth:
    st.title("🔐 Login - Dadar Land System")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "123": st.session_state.auth = True; st.rerun()
        else: st.error("Iccitii dogoggora!")

else:
    menu = st.sidebar.radio("📋 MENU", ["📊 Dashboard", "📝 Galmee & Online Payment", "🔍 Manage"])

    if menu == "📊 Dashboard":
        st.header("📊 Analytics Dashboard")
        df = load_data(DATA_FILE, COL_NAMES)
        if not df.empty:
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            st.metric("💰 Waliigala Galii (ETB)", f"{df['Kafaltii'].sum():,.2f}")
            st.plotly_chart(px.pie(df, values='Kafaltii', names='Tajaajila', title="Gosa Tajaajilaa fi Galii"))
            st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee & Online Payment":
        st.header("📝 Galmee fi Kaffaltii")
        with st.form("reg_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            m_maqaa = c1.text_input("👤 Maqaa Maamilaa")
            m_ara = c1.text_input("📍 Araddaa")
            gosa = st.selectbox("📂 Gosa Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
            taj = st.selectbox("🎯 Tajaajila Filatame", SERVICE_STRUCTURE[gosa])
            fee = st.number_input("💸 Kaffaltii (ETB)", min_value=1.0)
            pay_method = st.radio("💳 Akkaataa Kaffaltii", ["Harkaan (Cash)", "Online (Telebirr/CBE/Card)"])
            submitted = st.form_submit_button("💾 GALMEESSI")

        if submitted and m_maqaa:
            tx_ref = f"DADAR-{uuid.uuid4().hex[:6].upper()}"
            d_now = datetime.now().strftime('%d/%m/%Y')
            
            if pay_method == "Online (Telebirr/CBE/Card)":
                checkout_url = initialize_chapa(fee, m_maqaa, tx_ref)
                if checkout_url:
                    st.markdown(f"""
                        <div class="pay-box">
                            <h4>Kaffaltii Telebirr/CBE Birr Raawwachuuf</h4>
                            <a href="{checkout_url}" target="_blank" style="background-color:#0288d1; color:white; padding:10px 25px; text-decoration:none; border-radius:5px; font-weight:bold;">AMMA KAFFALI</a>
                        </div>
                    """, unsafe_allow_html=True)
                else: st.error("Kaffaltii Online jalqabsiisuun hin danda'amne. Key kee check godhi!")

            # Save Data
            new_rec = [d_now, m_maqaa, m_ara, "-", taj, "Admin", fee, tx_ref]
            df = load_data(DATA_FILE, COL_NAMES)
            save_data(pd.concat([df, pd.DataFrame([new_rec], columns=COL_NAMES)]), DATA_FILE)
            
            pdf = create_pdf_receipt({"maqaa":m_maqaa, "guyyaa":d_now, "ref":tx_ref}, taj, fee)
            st.session_state.pdf_ready = {"data": pdf, "name": f"Nagahee_{tx_ref}.pdf"}
            st.success(f"Galmeen {m_maqaa} milkaayinaan kuufameera!")

        if st.session_state.pdf_ready:
            st.download_button("📥 Nagahee (Receipt) PDF Buufadhu", st.session_state.pdf_ready["data"], st.session_state.pdf_ready["name"])

    # --- TELEGRAM REPORT ---
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Excel Gara Telegram"):
        df_all = load_data(DATA_FILE, COL_NAMES)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as wr: df_all.to_excel(wr, index=False)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID_MANAGER}, files={'document': ("Report.xlsx", out.getvalue())})
        st.sidebar.success("Ergameera!")

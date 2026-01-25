import streamlit as st
import pandas as pd
import os, io, requests, uuid
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
# HUBADHU: Key kee isa Chapa.co irraa argattu asitti galchi
CHAPA_AUTH = "CHASECK_TEST-xxxxxxxxxxxxxxxxxxxx" 
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa', 'Araddaa', 'Qaxana', 'Tajaajila', 'Ogeessa', 'Kafaltii', 'Ref_ID']

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .pay-box { background-color:#e1f5fe; padding:20px; border-radius:10px; text-align:center; border: 1px solid #b3e5fc; margin-top: 15px; }
    h1, h2 { color: #1E3A8A; }
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

# ================= 3. CORE FUNCTIONS =================
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
    pdf.rect(5, 5, 90, 140) # Border
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "NAGAHEE KAFFALTII", ln=True, align='C')
    pdf.set_font('Arial', '', 9); pdf.cell(0, 6, f"Maqaa: {data['maqaa']}", ln=True)
    pdf.cell(0, 6, f"Guyyaa: {data['guyyaa']}", ln=True)
    pdf.cell(0, 6, f"Lakk (Ref): {data['ref']}", ln=True); pdf.ln(5)
    pdf.cell(55, 8, f" {taj[:25]}", 1); pdf.cell(25, 8, f" {fee:,.2f}", 1, 1, 'R')
    pdf.set_font('Arial', 'B', 10); pdf.cell(55, 10, " Waliigala (Total)", 1, 0, 'R'); pdf.cell(25, 10, f" {fee:,.2f}", 1, 1, 'R')
    pdf.ln(10); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 5, "Nagaheen kun sirnaan kan qophaa'e dha.", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP INTERFACE =================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = None

if not st.session_state.auth:
    st.title("🔐 Login - Dadar Land System")
    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.auth = True; st.rerun()
            else: st.error("Iccitii dogoggora!")

else:
    menu = st.sidebar.radio("📋 MENU", ["📊 Dashboard", "📝 Galmee & Online Payment", "🔍 Manage/Search"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Analytics Dashboard")
        df = load_data(DATA_FILE, COL_NAMES)
        if not df.empty:
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Galmee", len(df))
            c3.metric("📅 Guyyaa", datetime.now().strftime('%d/%m/%Y'))
            
            st.plotly_chart(px.bar(df.groupby('Tajaajila')['Kafaltii'].sum().reset_index(), 
                                   x='Kafaltii', y='Tajaajila', orientation='h', title="Galii Gosa Tajaajilaan"))
            st.dataframe(df, use_container_width=True)

    # --- REGISTRATION & PAYMENT ---
    elif menu == "📝 Galmee & Online Payment":
        st.header("📝 Galmee Maamilaa fi Kaffaltii")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            m_maqaa = col1.text_input("👤 Maqaa Maamilaa")
            m_ara = col1.text_input("📍 Araddaa")
            gosa = st.selectbox("📂 Gosa Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
            taj = st.selectbox("🎯 Tajaajila Filatame", SERVICE_STRUCTURE[gosa])
            fee = st.number_input("💸 Kaffaltii (ETB)", min_value=1.0)
            pay_method = st.radio("💳 Akkaataa Kaffaltii", ["Harkaan (Cash)", "Online (Telebirr/CBE/Card)"])
            submitted = st.form_submit_button("💾 GALMEESSI")

        if submitted and m_maqaa:
            tx_ref = f"DADAR-{uuid.uuid4().hex[:6].upper()}"
            d_now = datetime.now().strftime('%d/%m/%Y')
            
            # Kaffaltii Online
            if pay_method == "Online (Telebirr/CBE/Card)":
                checkout_url = initialize_chapa(fee, m_maqaa, tx_ref)
                if checkout_url:
                    st.markdown(f"""
                        <div class="pay-box">
                            <h4>Kaffaltii Telebirr/CBE Birr Raawwachuuf</h4>
                            <a href="{checkout_url}" target="_blank" style="background-color:#0288d1; color:white; padding:10px 25px; text-decoration:none; border-radius:5px; font-weight:bold;">AMMA KAFFALI</a>
                        </div>
                    """, unsafe_allow_html=True)
                else: st.error("Chapa API Error: Key kee check godhi!")

            # Save to Data File
            new_rec = [d_now, m_maqaa, m_ara, "-", taj, "Admin", fee, tx_ref]
            df = load_data(DATA_FILE, COL_NAMES)
            df = pd.concat([df, pd.DataFrame([new_rec], columns=COL_NAMES)], ignore_index=True)
            save_data(df, DATA_FILE)
            
            # Create PDF
            pdf_bytes = create_pdf_receipt({"maqaa":m_maqaa, "guyyaa":d_now, "ref":tx_ref}, taj, fee)
            st.session_state.pdf_ready = {"data": pdf_bytes, "name": f"Nagahee_{tx_ref}.pdf"}
            st.success(f"Galmeen {m_maqaa} milkaayinaan raawwatameera!")

        # Nagahee Formi Alatti (Error akka hin uumamneef)
        if st.session_state.pdf_ready:
            st.download_button("📥 Nagahee (Receipt) PDF Buufadhu", 
                               st.session_state.pdf_ready["data"], 
                               st.session_state.pdf_ready["name"],
                               mime="application/pdf")

    # --- MANAGE / SEARCH ---
    elif menu == "🔍 Manage/Search":
        st.header("🔍 Barbaadi fi Sirreessi")
        df_m = load_data(DATA_FILE, COL_NAMES)
        if not df_m.empty:
            search = st.text_input("Maqaa maamilaan barbaadi...")
            if search:
                df_m = df_m[df_m['Maqaa'].str.contains(search, case=False)]
            st.dataframe(df_m, use_container_width=True)

    # --- TELEGRAM REPORT ---
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Excel Gara Telegram"):
        df_all = load_data(DATA_FILE, COL_NAMES)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
            df_all.to_excel(wr, index=False)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", 
                      data={'chat_id': CHAT_ID_MANAGER}, 
                      files={'document': ("Gabaasa_Dadar.xlsx", out.getvalue())})
        st.sidebar.success("Gabaasni Telegram-itti ergameera!")

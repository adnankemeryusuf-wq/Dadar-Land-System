import streamlit as st
import pandas as pd
import os, io, requests, uuid
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
DATA_FILE = "dadar_final_report.txt"
# API Chapa (Kee asitti galchi - chapa.co irraa kan argattu)
CHAPA_AUTH = "CHASECK_TEST-xxxxxxxxxxxxxxxxxxxx" 
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa', 'Araddaa', 'Qaxana', 'Tajaajila', 'Ogeessa', 'Kafaltii', 'Payment_ID']

st.set_page_config(page_title="Dadar Land System", layout="wide")

# ================= 2. ONLINE PAYMENT LOGIC =================
def initialize_chapa(amount, name, tx_ref):
    """Linkii kaffaltii Chapa uumuu"""
    url = "https://api.chapa.co/v1/transaction/initialize"
    headers = {"Authorization": f"Bearer {CHAPA_AUTH}"}
    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": "customer@dadarland.gov.et",
        "first_name": name,
        "tx_ref": tx_ref,
        "callback_url": "https://chapa.co", # Gara app keetti deebi'uuf
        "customization[title]": "Kaffaltii Tajaajila Lafaa",
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except:
        return None

# ================= 3. PDF & DATA FUNCTIONS =================
def load_data(f, cols):
    if not os.path.exists(f) or os.stat(f).st_size == 0:
        return pd.DataFrame(columns=cols)
    return pd.read_csv(f, sep="|", names=cols, header=None, encoding='utf-8')

def save_data(df, f):
    df.to_csv(f, sep="|", index=False, header=False, encoding="utf-8")

def create_receipt(data, item, fee):
    pdf = FPDF(unit='mm', format=(100, 150))
    pdf.add_page()
    pdf.rect(5, 5, 90, 140)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "NAGAHEE KAFFALTII", ln=True, align='C')
    pdf.set_font('Arial', '', 9); pdf.cell(0, 6, f"Maqaa: {data['maqaa']}", ln=True)
    pdf.cell(0, 6, f"Guyyaa: {data['guyyaa']}", ln=True)
    pdf.cell(0, 6, f"Ref: {data['ref']}", ln=True); pdf.ln(5)
    pdf.cell(55, 8, f" {item}", 1); pdf.cell(25, 8, f" {fee:,.2f}", 1, 1, 'R')
    pdf.set_font('Arial', 'B', 10); pdf.cell(55, 10, " Waliigala", 1, 0, 'R'); pdf.cell(25, 10, f" {fee:,.2f}", 1, 1, 'R')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. UI INTERFACE =================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = None

if not st.session_state.auth:
    st.title("🔐 Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "123": st.session_state.auth = True; st.rerun()
else:
    menu = st.sidebar.radio("📋 MENU", ["📊 Dashboard", "📝 Galmee & Online Payment", "🔍 Manage"])

    if menu == "📝 Galmee & Online Payment":
        st.header("📝 Galmee Maamilaa fi Kaffaltii")
        with st.form("reg_form"):
            m_maqaa = st.text_input("👤 Maqaa Maamilaa")
            taj = st.selectbox("🎯 Tajaajila", ["Gibira Manaa", "Liizii Waggaa", "Kaartaa Haaraa"])
            fee = st.number_input("💸 Kaffaltii (ETB)", min_value=1.0)
            pay_type = st.radio("Akkaataa Kaffaltii", ["Harkaan (Cash)", "Online (Telebirr/CBE/Card)"])
            submitted = st.form_submit_button("💾 GALMEESSI")

        if submitted and m_maqaa:
            tx_ref = f"DADAR-{uuid.uuid4().hex[:6].upper()}"
            d_now = datetime.now().strftime('%d/%m/%Y')
            
            if pay_type == "Online (Telebirr/CBE/Card)":
                res = initialize_chapa(fee, m_maqaa, tx_ref)
                if res and res.get('status') == 'success':
                    st.success(f"Linkiin kaffaltii uumameera! Lakk: {tx_ref}")
                    st.markdown(f"### [🔗 Kaffaltii Raawwachuuf As Tuqi]({res['data']['checkout_url']})")
                else:
                    st.error("Kaffaltii online jalqabsiisuun hin danda'amne.")
            
            # Galmeessuu (Data Saving)
            new_rec = [d_now, m_maqaa, "Dadar", "-", taj, "Admin", fee, tx_ref]
            df = load_data(DATA_FILE, COL_NAMES)
            save_data(pd.concat([df, pd.DataFrame([new_rec], columns=COL_NAMES)]), DATA_FILE)
            
            pdf = create_receipt({"maqaa":m_maqaa, "guyyaa":d_now, "ref":tx_ref}, taj, fee)
            st.session_state.pdf_ready = {"data": pdf, "name": f"Nagahee_{tx_ref}.pdf"}
            st.info("Galmeen kuufameera. Kaffaltii erga xumurtee nagahee buufadhu.")

        if st.session_state.pdf_ready:
            st.download_button("📥 Nagahee PDF Buufadhu", st.session_state.pdf_ready["data"], st.session_state.pdf_ready["name"])

    elif menu == "📊 Dashboard":
        st.header("📈 Gabaasa Waliigalaa")
        df = load_data(DATA_FILE, COL_NAMES)
        if not df.empty:
            st.metric("💰 Waliigala Galii", f"{pd.to_numeric(df['Kafaltii']).sum():,.2f} ETB")
            st.dataframe(df, use_container_width=True)

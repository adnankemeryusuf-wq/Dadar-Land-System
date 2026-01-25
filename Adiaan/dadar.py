import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & SETUP =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

# Styling
st.markdown("""
    <style>
    .stApp { background: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #064e3b !important; }
    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); text-align: center; border-top: 5px solid #10b981; }
    div.stForm { background: white; border-radius: 15px; padding: 30px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'User'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def create_clearance_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277) # Border
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "WAAJJIRA LAFAA FI MANNEENII", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    text = f"Maamilli keenya {data['maqaa']}, Araddaa {data['araddaa']}, Qaxana {data['qaxana']} tajaajila '{data['dhimma']}' xumuraniiru."
    pdf.multi_cell(0, 10, text)
    pdf.ln(20)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(0, 10, "Mallattoo Itti Gaafatamaa: ________________", ln=True)
    return pdf.output(dest='S').encode('latin-1')

def send_to_telegram(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': ('Gabaasa_Dadar.xlsx', output.getvalue())}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': f"📊 Gabaasa Guyyaa {datetime.now().strftime('%d/%m/%Y')}"}
    return requests.post(url, files=files, data=data)

# ================= 3. SIDEBAR & AUTH =================
df = load_data()

with st.sidebar:
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
    st.title("Main Menu")
    menu = st.radio("Fili:", ["🏠 Dashboard", "📝 Galmeessi", "🔍 Barbaadi/Edit", "📄 Clearance", "📤 Telegram"])
    
    st.divider()
    pin = st.text_input("Admin PIN", type="password")
    role = "admin" if pin == "2026" else "staff"
    st.caption(f"Role: {role.upper()}")

# ================= 4. PAGES =================

# --- DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("📈 Dashboard Gabaasaa")
    m1, m2, m3 = st.columns(3)
    m1.metric("Maamiltoota", len(df))
    if role == "admin":
        m2.metric("Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
    
    if not df.empty:
        fig = px.pie(df, names='Gosa_Tajajjilaa', title="Gosa Tajaajilaa")
        st.plotly_chart(fig)

# --- REGISTRATION ---
elif menu == "📝 Galmeessi":
    st.header("📝 Galmee Maamilaa Haaraa")
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
        ara = c2.text_input("Araddaa")
        qax = c1.text_input("Qaxana")
        ogeessa = c2.text_input("Maqaa Ogeessaa")
        gosa = st.selectbox("Gosa Tajaajilaa", ["Jijjiirraa Maqaa", "Kaartaa Haaraa", "Waraqaa Qulqullinaa", "Kireessuun"])
        kaffaltii = st.number_input("Kafaltii (ETB)", min_value=0.0)
        file = st.file_uploader("Nagahee Scan (Image)", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("Save Data"):
            if maqaa and ogeessa:
                # Save Image
                if file:
                    with open(os.path.join(NAGAHEE_DIR, f"{maqaa[:10]}_{file.name}"), "wb") as f:
                        f.write(file.getbuffer())
                
                new_data = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, gosa, ogeessa, kaffaltii, role]
                df.loc[len(df)] = new_data
                save_data(df)
                st.success("✅ Galmeeffameera!")

# --- SEARCH & EDIT ---
elif menu == "🔍 Barbaadi/Edit":
    st.header("🔍 Barbaadi fi Sirreessi")
    q = st.text_input("Maqaa Barbaadi...")
    if q:
        res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
        for idx, row in res.iterrows():
            with st.expander(f"{row['Maqaa_Abbaa_Dhimmaa']}"):
                if role == "admin":
                    new_n = st.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"e_{idx}")
                    if st.button("💾 Update", key=f"u_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_n
                        save_data(df); st.rerun()
                    if st.button("🗑 Haqi", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()
                else:
                    st.write(f"Tajaajila: {row['Gosa_Tajajjilaa']} | Ogeessa: {row['Maqaa_Ogeessa']}")

# --- CLEARANCE ---
elif menu == "📄 Clearance":
    st.header("📄 Qophii Clearance")
    with st.form("clr"):
        m = st.text_input("Maqaa"); a = st.text_input("Araddaa"); q = st.text_input("Qaxana"); d = st.text_input("Dhimma")
        if st.form_submit_button("PDF Uumi"):
            pdf = create_clearance_pdf({"maqaa":m, "araddaa":a, "qaxana":q, "dhimma":d})
            st.download_button("📥 PDF Buufadhu", pdf, f"Clearance_{m}.pdf")

# --- TELEGRAM ---
elif menu == "📤 Telegram":
    st.header("📤 Gabaasa Mana Hojiitti Ergi")
    if st.button("✈️ Excel Telegramitti Ergi"):
        if send_to_telegram(df): st.success("✅ Gabaasni Maanajaraatti ergameera!")

import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# Tajaajiloota hunda iddoo tokkotti (List qofa)
ALL_SERVICES = [
    "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa",
    "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Kaffaltii Kiiraa Manaa",
    "TOT (Turnover Tax)", "Jijjiirraa Maqaa (Gift/Sale)",
    "Kaartaa Haaraa (Liizii)", "Kaartaa Haaraa (Kiiraa)", "Kaartaa Bakka Bu'aa",
    "Kaartaa Kadastaaraa", "Sirreeffama Daangaa", "Kaartaa Lafa Qonnaa",
    "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa",
    "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii",
    "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)",
    "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo",
    "Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", "Adabbii Faallaa Pilaanii"
]

# ================= 2. DATA FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF GENERATOR (CLEARANCE) =================
def create_clearance_pdf(data, logo_l=None, logo_r=None):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277) # Outer Border
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273) # Inner Border
    if logo_l: pdf.image(logo_l, x=15, y=15, w=25)
    if logo_r: pdf.image(logo_r, x=170, y=15, w=25)
    pdf.set_y(20); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 7, "WAAJJIRA TAJAAJILA LAFAA", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'BU', 13); pdf.cell(0, 10, "WARAQAA QULQULLUMMAA", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    txt = f"Maqaan: {data['m']}\nAraddaa: {data['a']}\nQaxana: {data['q']}\nGosa: {data['g']}\nDhimma: {data['d']}\n\nKaffaltii gibiraa fi tajaajilaa kamirraayyuu bilisa ta'uu isaa ni mirkaneessina."
    pdf.multi_cell(170, 10, txt)
    pdf.ln(20); pdf.cell(0, 10, f"Itti Gaafatamaa: {data['h']}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. UI INTERFACE =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "123":
            st.session_state.auth = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("📋 MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "📄 Clearance", "🔍 Barbaadi/Haqi", "Ba'i"])

    if menu == "Ba'i":
        st.session_state.auth = False
        st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("📅 Har'a", len(df[df['Guyyaa'] == datetime.now().strftime('%d/%m/%Y')]))
        fig = px.pie(df, names='Gosa_Tajajjilaa', values='Kafaltii_Taj', title="Galii Gosa Tajaajilaan")
        st.plotly_chart(fig, use_container_width=True)

    # --- GALMEE HAARAA (SINGLE SELECT) ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            # Tajaajila hunda iddoo tokkotti filachuuf
            service = st.selectbox("Tajaajila Filadhu", ALL_SERVICES)
            og = c2.text_input("Ogeessa")
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and service:
                    new = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, service, og, fee]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!")

    # --- CLEARANCE ---
    elif menu == "📄 Clearance":
        st.header("📄 Waraqaa Qulqullummaa")
        l_bita = st.file_uploader("Logo Bitaa", type=['png','jpg'], key="cl1")
        l_mirga = st.file_uploader("Logo Mirgaa", type=['png','jpg'], key="cl2")
        with st.form("clr"):
            c1, c2 = st.columns(2)
            d = {"m": c1.text_input("Maqaa Maamilaa"), "a": c2.text_input("Araddaa"), "q": c1.text_input("Qaxana"), 
                 "g": st.selectbox("Gosa Qabiyyee", ["Liizii", "Kiiraa"]), "d": c2.text_input("Dhimma"), 
                 "h": st.text_input("Itti Gaafatamaa"), "bara": "2018"}
            if st.form_submit_button("📄 PDF UUMI"):
                pdf = create_clearance_pdf(d, l_bita, l_mirga)
                st.download_button("📥 Buufadhu", pdf, f"Clearance_{d['m']}.pdf")

    # --- SEARCH & DELETE ---
    elif menu == "🔍 Barbaadi/Haqi":
        st.header("🔍 Barbaadi fi Haqi")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            idx = st.number_input("Index Galmee Haquuf", min_value=0, max_value=len(df)-1 if len(df)>0 else 0)
            if st.button("🗑 Haqi"):
                df = df.drop(df.index[int(idx)])
                save_data(df); st.warning("Haqameera!"); st.rerun()

    # --- TELEGRAM ---
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Excel Gara Telegram"):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df[COL_NAMES].to_excel(wr, index=False)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", 
                      data={'chat_id': CHAT_ID_MANAGER, 'caption': f"Gabaasa Dadar: {df['Kafaltii_Taj'].sum():,.2f} ETB"}, 
                      files={'document': ("Gabaasa.xlsx", buf.getvalue())})
        st.sidebar.success("Telegram-itti ergameera!")

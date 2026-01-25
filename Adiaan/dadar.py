import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
DATA_FILE = "dadar_final_report.txt"
CLR_HISTORY_FILE = "clearance_history.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
CLR_COLS = ['Guyyaa', 'Maqaa', 'Araddaa', 'Gosa', 'Kaartaa', 'Dhimma', 'I/G']

SERVICE_LIST = [
    "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa",
    "Kaffaltii Liizii Waggaa", "Kaffaltii Kiiraa Manaa", "TOT (Turnover Tax)",
    "Jijjiirraa Maqaa (Gift/Sale)", "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa",
    "Kaartaa Kadastaaraa", "Waraqaa Ragaa (Clearance)", "Adabbii Ijaarsa Seeraan Alaa"
]

# ================= 2. DATA FUNCTIONS =================
def load_data(file, cols):
    if not os.path.exists(file) or os.stat(file).st_size == 0:
        return pd.DataFrame(columns=cols)
    return pd.read_csv(file, sep="|", names=cols, header=None, encoding='utf-8')

def save_data(df, file):
    df.to_csv(file, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF GENERATORS =================
def create_clearance_pdf(data, logo_l=None, logo_r=None):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)
    if logo_l: pdf.image(logo_l, x=15, y=15, w=25)
    if logo_r: pdf.image(logo_r, x=170, y=15, w=25)
    pdf.set_y(25); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.set_font('Arial', 'BU', 13); pdf.ln(10)
    pdf.cell(0, 10, "WARAQAA QULQULLUMMAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    txt = f"Maqaan: {data['maqaa']}\nIddoo: Araddaa {data['araddaa']}, Qaxana {data['qaxana']}\nGosa: {data['gosa']}\nLakk. Kaartaa: {data['kaartaa']}\nDhimma: {data['dhimma']}\n\nKaffaltii gibiraa fi tajaajilaa bara {data['bara']}tti xumuruu isaa ni mirkaneessina."
    pdf.multi_cell(170, 10, txt)
    pdf.ln(20); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Itti Gaafatamaa: {data['head']}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'replace')

def create_award_certificate(name, reason, date_str):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(218, 165, 32); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_y(40); pdf.set_font('Arial', 'B', 30); pdf.set_text_color(0, 80, 0)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 35); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 25, name.upper(), ln=True, align='C')
    pdf.set_font('Arial', '', 15); pdf.cell(0, 10, f"Sababa: {reason}", ln=True, align='C')
    pdf.set_y(160); pdf.cell(0, 10, f"Guyyaa: {date_str}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN UI =================
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
    menu = st.sidebar.radio("📋 MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "📄 Clearance", "🏆 Badhaasa", "🔍 Barbaadi/Haqi", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Analytics")
        df = load_data(DATA_FILE, COL_NAMES)
        if not df.empty:
            df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce')
            c1, c2 = st.columns(2)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f}")
            c2.metric("👥 Maamiltoota", len(df))
            fig = px.pie(df, values='Kafaltii_Taj', names='Gosa_Tajajjilaa', title="Qoodinsa Galii")
            st.plotly_chart(fig)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("reg"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c2.text_input("Araddaa")
            ser = st.selectbox("Tajaajila", SERVICE_LIST)
            fee = st.number_input("Kaffaltii", min_value=0.0)
            og = st.text_input("Ogeessa")
            if st.form_submit_button("💾 Galmeessi"):
                df = load_data(DATA_FILE, COL_NAMES)
                new = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", ser, og, fee]
                df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)])
                save_data(df, DATA_FILE); st.success("Galmeeffameera!")

    elif menu == "📄 Clearance":
        st.header("📄 Clearance & History")
        up_l = st.file_uploader("Logo Bitaa", type=['png', 'jpg'])
        up_r = st.file_uploader("Logo Mirgaa", type=['png', 'jpg'])
        with st.form("clr"):
            c1, c2 = st.columns(2)
            d = {"maqaa": c1.text_input("Maqaa"), "araddaa": c2.text_input("Araddaa"), "qaxana": c1.text_input("Qaxana"),
                 "kaartaa": c2.text_input("Lakk. Kaartaa"), "gosa": st.selectbox("Gosa", ["Liizii", "Kiiraa"]),
                 "bara": c1.text_input("Bara Gibiraa", "2018"), "dhimma": c2.text_input("Dhimma"), "head": st.text_input("I/G")}
            if st.form_submit_button("📄 PDF UUMI"):
                pdf = create_clearance_pdf(d, up_l, up_r)
                h_df = load_data(CLR_HISTORY_FILE, CLR_COLS)
                new_h = [datetime.now().strftime('%d/%m/%Y'), d['maqaa'], d['araddaa'], d['gosa'], d['kaartaa'], d['dhimma'], d['head']]
                h_df = pd.concat([h_df, pd.DataFrame([new_h], columns=CLR_COLS)])
                save_data(h_df, CLR_HISTORY_FILE)
                st.download_button("📥 Buufadhu", pdf, f"Clearance_{d['maqaa']}.pdf")
        
        st.subheader("📜 Galmee Hordoffii")
        st.dataframe(load_data(CLR_HISTORY_FILE, CLR_COLS))

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeessaa")
        with st.form("award"):
            e_name = st.text_input("Maqaa Ogeessaa")
            e_reason = st.text_input("Sababa Badhaasaa")
            if st.form_submit_button("🎨 Sartiifiketa Uumi"):
                pdf = create_award_certificate(e_name, e_reason, datetime.now().strftime('%d/%m/%Y'))
                st.download_button("📥 Buufadhu", pdf, "Certificate.pdf")

    if st.sidebar.button("🚀 Excel Gara Telegram"):
        df_all = load_data(DATA_FILE, COL_NAMES)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as wr: df_all.to_excel(wr, index=False)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID_MANAGER}, files={'document': ("Gabaasa.xlsx", output.getvalue())})
        st.sidebar.success("Telegram-itti ergameera!")

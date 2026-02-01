import streamlit as st
import pandas as pd
import os
import io
import requests
import tempfile
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

MONTH_ORDER = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

st.markdown("""
    <style>
    div[data-testid="stSidebarUserContent"] .stRadio label {
        background-color: #10b981 !important;
        color: #000000 !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 15px 25px !important;
        margin-bottom: 10px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(12, 173, 120, 0.4) !important;
        display: block;
        cursor: pointer;
    }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-left: 5px solid #10b981; }
    .metric-value { font-size: 2rem; font-weight: 900; color: #10b981; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    df['Date_Temp'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Ji\'a'] = df['Date_Temp'].dt.month_name()
    df['Kurmaana'] = df['Date_Temp'].dt.quarter.map({1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"})
    return df

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date.day:02d}/{e_date.month:02d}/{e_date.year}"

# ================= 3. PDF GENERATORS =================

def create_receipt_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "NAGAHEE KAFFALTII TAJAAJILAA", ln=True, align='C')
    pdf.ln(10); pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Guyyaa: {data[0]}", ln=True)
    pdf.cell(0, 10, f"Maqaa: {data[1]}", ln=True)
    pdf.cell(0, 10, f"Tajaajila: {data[4]}", ln=True)
    pdf.cell(0, 10, f"Kaffaltii: {data[6]:,.2f} ETB", ln=True)
    return pdf.output(dest='S').encode('latin-1')

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_y(30); pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 12)
    body = f"Waraqaan ragaa kun Obbo/Adde {data['maqaa']} Araddaa {data['araddaa']} Lakk. Kaartaa {data['kaartaa']} qabaniif dhimma {data['dhimma']} kaffaltii bara {data['bara_gibiraa']} xumuruu isaanii ni mirkaneessina."
    pdf.set_x(20); pdf.multi_cell(170, 10, body)
    pdf.set_y(240); pdf.set_x(20); pdf.cell(0, 10, f"Itti Gaafatamaa: {data['head_name']}")
    return pdf.output(dest='S').encode('latin-1')

def create_pdf_cert(name, count, rank, logo_left, logo_right):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = colors.get(rank, (0, 0, 0))
    pdf.set_draw_color(r, g, b); pdf.set_line_width(5); pdf.rect(10, 10, 277, 190)
    
    for logo, pos in [(logo_left, 20), (logo_right, 247)]:
        if logo:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(logo.getvalue())
                pdf.image(tmp.name, pos, 20, 30)
            os.unlink(tmp.name)

    pdf.set_y(60); pdf.set_font("Arial", 'B', 30); pdf.set_text_color(r, g, b)
    pdf.cell(0, 20, "SARTIIFIIKEETA BADHAASAA", ln=True, align='C')
    pdf.set_font("Arial", 'B', 35); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 30, name.upper(), ln=True, align='C')
    pdf.set_font("Arial", '', 16); pdf.cell(0, 10, f"Dhimma {count} raawwachuun sadarkaa {rank}ffaa argataniif.", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login"):
            st.title("Admin Login")
            u, p = st.text_input("Username"), st.text_input("Password", type="password")
            if st.form_submit_button("SEENI"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Ragaan dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        menu = st.radio("Filannoo", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📜 Clearance (Ragaa)", "📈 Gabaasa Galii", "🏆 Badhaasa", "🚪 Logout"])

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df.empty else "-"
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Cimaa</p><p class='metric-value' style='font-size:1.2rem;'>{top_og}</p></div>", unsafe_allow_html=True)

    elif menu == "📝 Galmee Tajaajilaa":
        st.header("📝 Galmee Haaraa Galchi")
        GATII_DICT = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
            "📜 Kaartaa": ["Kaartaa Haaraa", "Jijjiirraa Maqaa (Sale)", "Kaartaa Bakka Bu'aa"],
            "🏗 Pilaanii": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa"]
        }
        sel_main = st.multiselect("Ramaddii Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        if sel_main:
            for g in sel_main:
                subs = st.multiselect(f"Tajaajila ({g})", GATII_DICT[g])
                for s in subs:
                    fee = st.number_input(f"Gatii {s}", min_value=0.0, key=f"f_{s}")
                    details.append(s); d_fees[s] = fee
                    if any(x in s for x in ["TOT", "Sale"]): is_tot = True
        
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            if is_tot:
                name = f"G: {c1.text_input('Gurguraa')} / B: {c2.text_input('Bitataa')}"
                ara = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
            else:
                name, ara = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")
            qaxana = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 GALMEESSI"):
                if name and details:
                    total = sum(d_fees.values())
                    new_row = [datetime.now().strftime('%d/%m/%Y %H:%M'), name, ara, qaxana, ", ".join(details), ogeessa, total]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!")
                    st.download_button("📥 Nagahee PDF", create_receipt_pdf(new_row), f"Nagahee_{name}.pdf")

    elif menu == "📜 Clearance (Ragaa)":
        st.header("📜 Waraqaa Ragaa Qulqullinaa")
        with st.form("c_form"):
            m_data = {
                'maqaa': st.text_input("Maqaa Maamilaa"),
                'araddaa': st.text_input("Araddaa"),
                'kaartaa': st.text_input("Lakk. Kaartaa"),
                'bara_gibiraa': st.text_input("Bara Gibiraa"),
                'dhimma': st.text_input("Dhimma Maaliif"),
                'head_name': st.text_input("Maqaa Itti Gaafatamaa")
            }
            if st.form_submit_button("📄 PDF UUMI"):
                if m_data['maqaa']:
                    st.download_button("📥 Clearance Buufadhu", create_clearance_pdf(m_data), f"Clearance_{m_data['maqaa']}.pdf")

    elif menu == "📈 Gabaasa Galii":
        st.header("📈 Gabaasa Waliigalaa")
        search = st.text_input("🔍 Barbaadi (Maqaa/Araddaa):")
        f_df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        st.dataframe(f_df, use_container_width=True)
        
        buf = io.BytesIO()
        f_df.to_excel(buf, index=False)
        if st.button("✈️ Telegram-itti Ergi"):
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", 
                          data={'chat_id': CHAT_ID_MANAGER}, 
                          files={'document': ("Gabaasa_Dadar.xlsx", buf.getvalue())})
            st.success("Gabaasni Ergameera!")

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        if not df.empty:
            l_up = st.file_uploader("Logo Bitaa", type=['png','jpg'])
            r_up = st.file_uploader("Logo Mirgaa", type=['png','jpg'])
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>Sadarkaa {i+1}</h3><b>{name}</b><br>{count} Dhimma</div>", unsafe_allow_html=True)
                    if st.button(f"Sartiifikeeta Uumi ({i+1})", key=f"cert_{i}"):
                        cert_pdf = create_pdf_cert(name, count, i+1, l_up, r_up)
                        st.download_button(f"📥 Download {name.split()[0]}", cert_pdf, f"Badhaasa_{name}.pdf")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False; st.rerun()

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

st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 900; color: #10b981; text-align: center; }
    div[data-testid="stSidebarUserContent"] .stRadio label {
        background-color: #10b981 !important;
        color: #000000 !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        margin-bottom: 8px !important;
        font-weight: 700 !important;
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
    pdf.cell(0, 10, "WAAJJIRA LAFAA MAGAALAA DADAR", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "NAGAHEE KAFFALTII", ln=True, align='C')
    pdf.ln(10); pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Guyyaa: {data[0]}", ln=True)
    pdf.cell(0, 8, f"Maqaa: {data[1]}", ln=True)
    pdf.cell(0, 8, f"Araddaa: {data[2]} | Qaxana: {data[3]}", ln=True)
    pdf.cell(0, 8, f"Tajaajila: {data[4]}", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Kaffaltii Waliigalaa: {data[6]:,.2f} ETB", ln=True)
    pdf.ln(10); pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, f"Ogeessa: {data[5]}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 18, 23)
    pdf.set_y(22); pdf.set_font('Times', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Times', 'B', 14); pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)
    guyyaa_ec = get_ethiopian_date_str()
    pdf.ln(12); pdf.set_font('Times', '', 12); pdf.set_x(20)
    pdf.write(5, f"Lakk. Galmee: DAD/WL/{datetime.now().year}/____"); pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {guyyaa_ec}"); pdf.ln(18)
    pdf.set_font('Times', 'B', 14); pdf.cell(0, 10, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C'); pdf.ln(8)
    pdf.set_font('Times', '', 12); pdf.set_x(20)
    pdf.write(9, f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} Qaxana {data['qaxana']} Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\n")
    pdf.write(9, f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} guutummaatti kaffalaniiru.\n")
    pdf.write(9, f"2. Kaffaltii {data['gosa_qabiyyee']} hunda xumuraniiru.\n")
    pdf.write(9, "3. Qabiyyeen kun DHORKAA kamirrayyuu bilisa ta'uu mirkaneessina.\n\n")
    pdf.write(9, f"Dhimma {data['dhimma']} raawwachuuf mormii hin qabnu.")
    pdf.set_y(235); pdf.set_x(20); pdf.set_font('Times', 'B', 12)
    pdf.write(8, f"Maqaa Itti Gaafatamaa: {data['head_name']}\nMallattoo: _________________")
    return pdf.output(dest='S').encode('latin-1')

def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(16, 185, 129); pdf.set_line_width(5); pdf.rect(10, 10, 277, 190)
    pdf.set_y(60); pdf.set_font("Arial", 'B', 30)
    pdf.cell(0, 20, "SARTIIFIIKEETA BADHAASAA", ln=True, align='C')
    pdf.set_font("Arial", 'B', 35); pdf.cell(0, 30, name.upper(), ln=True, align='C')
    pdf.set_font("Arial", '', 18); pdf.cell(0, 10, f"Dhimma {count} milkiin raawwachuun sadarkaa {rank}ffaa argataniif.", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=180)
        st.markdown("<h1 class='main-title'>Dadar Land Admin</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u, p = st.text_input("Username"), st.text_input("Password", type="password")
            if st.form_submit_button("SEENI"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        st.markdown("<h3 style='text-align:center;'>Magaalaa Dadar</h3>", unsafe_allow_html=True)
        st.divider()
        menu = st.radio("Filannoo", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📜 Clearance (Ragaa)", "📈 Gabaasa Galii", "🏆 Badhaasa", "🚪 Logout"])

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df.empty else "-"
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Cimaa</p><p class='metric-value' style='font-size:1.3rem;'>{top_og}</p></div>", unsafe_allow_html=True)
            st.divider()
            st.subheader("Ji'aan Maamiltoota Galmaa'an")
            df['Guyyaa_DT'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y %H:%M', errors='coerce')
            st.line_chart(df['Guyyaa_DT'].dt.date.value_counts())

    elif menu == "📝 Galmee Tajaajilaa":
        st.header("📝 Galmee Haaraa Galchi")
        GATII_DICT = {
            "🏷 Gibira": ["Gibira Baaxii Gooroo", "Kaffaltii Liizii Waggaa", "Turnover Tax (TOT)"],
            "📜 Kaartaa": ["Kaartaa Haaraa", "Jijjiirraa Maqaa", "Kaartaa Bakka Bu'aa"],
            "🏗 Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa"]
        }
        sel_main = st.multiselect("Ramaddii Filadhu", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if sel_main:
            for g in sel_main:
                subs = st.multiselect(f"Tajaajila ({g})", GATII_DICT[g])
                for s in subs:
                    fee = st.number_input(f"Gatii {s}", min_value=0.0, key=f"f_{s}")
                    details.append(s); d_fees[s] = fee

        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa *")
            ara = c2.text_input("Araddaa")
            qaxana = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa *")
            if st.form_submit_button("💾 GALMEESSI"):
                if name and details and ogeessa:
                    total = sum(d_fees.values())
                    new_row = [datetime.now().strftime('%d/%m/%Y %H:%M'), name, ara, qaxana, ", ".join(details), ogeessa, total]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Milkiin Galmeeffameera!")
                    st.download_button("📥 Nagahee PDF", create_receipt_pdf(new_row), f"Nagahee_{name}.pdf")
                else: st.error("Maaloo odeeffannoo guuti!")

    elif menu == "📜 Clearance (Ragaa)":
        st.header("📜 Waraqaa Qulqullinaa")
        if 'pdf_to_download' in st.session_state:
            st.success(f"✅ PDF {st.session_state.pdf_name} Qophaa'eera!")
            st.download_button("📥 Buufadhu", st.session_state.pdf_to_download, st.session_state.pdf_name)
            if st.button("🔄 Haaraa Uumi"): del st.session_state.pdf_to_download; st.rerun()
        else:
            with st.form("clearance"):
                c1, c2 = st.columns(2)
                m = {'maqaa': c1.text_input("Maqaa"), 'araddaa': c2.text_input("Araddaa"), 'qaxana': c1.text_input("Qaxana"), 'kaartaa': c2.text_input("Kaartaa"), 'gosa_qabiyyee': c1.selectbox("Gosa", ["Liizii", "Permit"]), 'bara_gibiraa': c2.text_input("Bara Gibiraa"), 'dhimma': c1.selectbox("Dhimma", ["Gurgurtaa", "Liqii", "Kennaa"]), 'head_name': st.text_input("Itti Gaafatamaa")}
                if st.form_submit_button("📄 PDF UUMI"):
                    if m['maqaa']:
                        st.session_state.pdf_to_download = create_clearance_pdf(m)
                        st.session_state.pdf_name = f"Clearance_{m['maqaa']}.pdf"; st.rerun()

    elif menu == "📈 Gabaasa Galii":
        st.header("📈 Gabaasa & Ergaa")
        search = st.text_input("🔍 Barbaadi:")
        f_df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        st.dataframe(f_df, use_container_width=True)
        buf = io.BytesIO(); f_df.to_excel(buf, index=False)
        c1, c2 = st.columns(2)
        c1.download_button("📥 Excel Buufadhu", buf.getvalue(), "Gabaasa.xlsx")
        if c2.button("✈️ Telegram-itti Ergi"):
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID_MANAGER}, files={'document': ("Gabaasa.xlsx", buf.getvalue())})
            st.success("Gabaasni hoggansatti ergameera!")

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        if not df.empty:
            stats = df['Maqaa_Ogeessa'].value_counts()
            for i, (name, count) in enumerate(stats.head(3).items()):
                st.write(f"Sadarkaa {i+1}: **{name}** ({count} Dhimma)")
                if st.button(f"Sartiifikeeta {name}"):
                    st.download_button("📥 Buufadhu", create_pdf_cert(name, count, i+1), f"Cert_{name}.pdf")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False; st.rerun()

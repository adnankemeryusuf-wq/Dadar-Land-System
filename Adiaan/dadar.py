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

# ... (Kutaa Import fi Configuration duraan ture) ...

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Double line) - Akkuma ati barbaaddetti
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Logos - Yoo jiraatan qofa
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 18, 23)

    # --- Header Section ---
    pdf.set_y(22)
    pdf.set_font('Times', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    # Header Underline
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)

    # Date and Ref No logic
    pdf.ln(12); pdf.set_font('Times', '', 12)
    guyyaa_ec = get_ethiopian_date_str()
    converter = EthiopianDateConverter()
    now_ec = converter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)

    pdf.set_x(20)
    pdf.write(5, "Lakk. Galmee: ")
    pdf.set_font('Times', 'B', 12) 
    pdf.write(5, f"DAD/WL/{now_ec.year}/____")
    pdf.set_font('Times', '', 12)
    pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {guyyaa_ec}")
    pdf.ln(18)

    # Subject
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8)

    # Body Section
    pdf.set_font('Times', '', 12); pdf.set_x(20)
    pdf.write(9, "Waraqaan ragaa kun Obbo/Adde/Dhaabbata ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['maqaa'].upper()}")
    pdf.set_font('Times', '', 12); pdf.write(9, " Araddaa ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['araddaa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " Qaxana ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['qaxana']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " keessatti mana/lafa Lakk. Kaartaa ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['kaartaa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " qabaniif kan kennameedha.\n\n")

    pdf.write(9, "Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n")

    # Itemized Points
    pdf.write(9, "1. Kaffaltii Gibira waggaa hanga bara ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['bara_gibiraa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " guutummaatti kaffalaniiru.\n")

    if data.get('gosa_qabiyyee') == "Liizii":
        pdf.write(9, "2. Kaffaltii "); pdf.set_font('Times', 'B', 12); pdf.write(9, "Liizii")
        pdf.set_font('Times', '', 12); pdf.write(9, " waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")
    else:
        pdf.write(9, "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")

    pdf.write(9, "3. Lafni/Manni kun "); pdf.set_font('Times', 'B', 12); pdf.write(9, "DHORKAA MANA MURTII")
    pdf.set_font('Times', '', 12); pdf.write(9, " ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n")

    pdf.write(9, "Kanaafuu, maamilli kun dhimma "); pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['dhimma']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina.")

    # --- Signature ---
    pdf.set_y(235); pdf.set_x(20)
    pdf.set_font('Times', '', 12); pdf.write(8, "Maqaa Itti Gaafatamaa: ")
    pdf.set_font('Times', 'B', 12); pdf.write(8, f"{data['head_name']}")
    pdf.ln(8); pdf.set_x(20); pdf.write(8, "Mallattoo: _________________")
    
    # Stamp Area
    pdf.set_y(243); pdf.set_x(120); pdf.set_font('Times', 'B', 11)
    pdf.cell(70, 8, "(Chaappaa Waajjiraa)", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')

# --- Kutaa UI (Filannoo menu irratti kan dhiyaatu) ---
if menu == "📜 Clearance (Ragaa)":
    st.header("📜 Sirna Qophii Waraqaa Qulqullinaa (Clearance)")
    
    # Check if PDF was generated in previous run to show download button
    if 'pdf_to_download' in st.session_state:
        st.success(f"✅ Clearance {st.session_state.pdf_name} qophaa'eera!")
        st.download_button(
            label="📥 Waraqaa Qulqullinaa Buufadhu",
            data=st.session_state.pdf_to_download,
            file_name=st.session_state.pdf_name,
            mime="application/pdf"
        )
        if st.button("🔄 Haaraa Qopheessi"):
            del st.session_state.pdf_to_download
            st.rerun()
    else:
        with st.form("clearance_form"):
            c1, c2 = st.columns(2)
            m_maqaa = c1.text_input("Maqaa Maamilaa *")
            m_araddaa = c2.text_input("Araddaa *")
            m_qaxana = c1.text_input("Lakk. Qaxana *")
            m_kaartaa = c2.text_input("Lakk. Kaartaa *")
            m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii (Permit)"])
            m_bara = c2.text_input("Bara Gibiraa Xumurame (Fkn: 2017)")
            m_dhimma = c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
            st.markdown("---")
            m_head = st.text_input("Maqaa Itti Gaafatamaa *")
            m_dhorkaa_bilisa = st.checkbox("Qabiyyeen kun dhorkaa irraa bilisa ta'uu nan mirkaneessa.")

            if st.form_submit_button("💾 PDF UUMI"):
                if all([m_maqaa, m_kaartaa, m_head, m_dhorkaa_bilisa]):
                    data_map = {
                        'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 
                        'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 
                        'gosa_qabiyyee': m_gosa, 'head_name': m_head
                    }
                    st.session_state.pdf_to_download = create_clearance_pdf(data_map)
                    st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
                    st.rerun()
                else:
                    st.error("Maaloo odeeffannoo guuti akkasumas dhorkaa irraa bilisa ta'uu mirkaneessi!")
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


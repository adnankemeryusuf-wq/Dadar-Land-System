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

def create_clearance_pdf(data, logo_l, logo_r):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    if logo_l:
        ext_l = logo_l.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext_l}") as tmp:
            tmp.write(logo_l.getbuffer()); pdf.image(tmp.name, 15, 18, 23)
        os.unlink(tmp.name)
    if logo_r:
        ext_r = logo_r.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext_r}") as tmp:
            tmp.write(logo_r.getbuffer()); pdf.image(tmp.name, 172, 18, 23)
        os.unlink(tmp.name)

    pdf.set_y(22); pdf.set_font('Times', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Times', 'B', 14); pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)
    
    guyyaa_ec = get_ethiopian_date_str()
    pdf.ln(12); pdf.set_font('Times', '', 12); pdf.set_x(20)
    pdf.write(5, f"Lakk. Galmee: DAD/WL/{datetime.now().year}/____"); pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {guyyaa_ec}"); pdf.ln(18)
    
    pdf.set_font('Times', 'B', 16); pdf.cell(0, 15, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C'); pdf.ln(5)
    
    pdf.set_font('Times', '', 12); pdf.set_x(20)
    pdf.write(9, "Waraqaan ragaa kun bu'uura qajeelfama bulchiinsa lafaatiin Obbo/Adde/Dhaabbata ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['maqaa'].upper()} "); pdf.set_font('Times', '', 12)
    pdf.write(9, f"Araddaa {data['araddaa']}, Qaxana {data['qaxana']} keessatti qabiyyee qaban ")
    
    pdf.set_font('Times', 'B', 13); pdf.write(9, f"LAKK. KAARTAA {str(data['kaartaa'])} "); pdf.set_font('Times', '', 12)
    pdf.write(9, "irratti kan kennameedha.\n\n")
    
    pdf.set_font('Times', 'B', 12); pdf.write(9, "Ragaaleen armaan gadiis mirkanaa'aniiru:\n"); pdf.set_font('Times', '', 12)
    pdf.write(9, f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} guutummaatti xumuraniiru.\n")
    pdf.write(9, f"2. Kaffaltii tajaajilaa {data['gosa_qabiyyee']} kamirrayyuu bilisa ta'uun isaanii mirkanaa'eera.\n")
    pdf.write(9, "3. Qabiyyeen kun dhorkaa kamirrayyuu (Mana Murtii fi Baankii) bilisa.\n\n")
    
    pdf.set_font('Times', 'I', 12)
    pdf.write(9, f"Kanaafuu, dhimma {data['dhimma']} barbaadaniif ragaan kun akka tajaajiluuf ni mirkaneessina.")
    
    pdf.set_y(245); pdf.set_font('Times', 'B', 12)
    pdf.set_x(20); pdf.cell(90, 10, f"Itti Gaafatamaa: {data['head_name']}", ln=0, align='L')
    pdf.set_x(120); pdf.cell(70, 10, "Mallattoo: _________________", ln=1, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

def create_pdf_cert(name, count, rank, logo_l, logo_r, head_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(16, 185, 129); pdf.set_line_width(5); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(218, 165, 32); pdf.set_line_width(1); pdf.rect(13, 13, 271, 184)

    if logo_l:
        ext_l = logo_l.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext_l}") as tmp:
            tmp.write(logo_l.getbuffer()); pdf.image(tmp.name, 20, 18, 25)
        os.unlink(tmp.name)
    if logo_r:
        ext_r = logo_r.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext_r}") as tmp:
            tmp.write(logo_r.getbuffer()); pdf.image(tmp.name, 252, 18, 25)
        os.unlink(tmp.name)

    pdf.set_y(55); pdf.set_font("Arial", 'B', 32); pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 20, "SARTIIFIIKEETA KABAJAA FI BADHAASAA", ln=True, align='C')
    pdf.set_y(85); pdf.set_font("Arial", 'I', 18); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Sartiifikeetiin kun kan kennameef:", ln=True, align='C')
    pdf.set_font("Arial", 'B', 40); pdf.set_text_color(184, 134, 11)
    pdf.cell(0, 25, name.upper(), ln=True, align='C')
    pdf.set_font("Arial", '', 16); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, f"Waajjira Lafaa Magaalaa Dadar keessatti tajaajila qulqulluu fi saffisa qabu maamiltootaaf kennuun,\ndhimmoota {count} milkiin xumurtanii sadarkaa {rank}ffaa waan qabattaniif galata guddaa qabna.", align='C')
    
    pdf.set_y(170); pdf.set_font("Arial", 'B', 12)
    pdf.set_x(30); pdf.cell(100, 10, f"Itti Gaafatamaa: {head_name}", ln=0, align='L')
    pdf.set_x(180); pdf.cell(80, 10, "Mallattoo: ___________________", ln=1, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=180)
        st.markdown("<h1 class='main-title'>Dadar Land Customer Registration System</h1>", unsafe_allow_html=True)
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

    elif menu == "📝 Galmee Tajaajilaa":
        st.header("📝 Galmee Haaraa Galchi")
        GATII_DICT = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
            "🏗 Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
            "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
            "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"]
        }
        sel_main = st.multiselect("Ramaddii Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        if sel_main:
            for g in sel_main:
                subs = st.multiselect(f"Tajaajila ({g})", GATII_DICT[g])
                for s in subs:
                    fee = st.number_input(f"Gatii {s} (ETB)", min_value=0.0, key=f"f_{s}")
                    details.append(s); d_fees[s] = fee
                    if any(x in s for x in ["TOT", "Sale", "Gift"]): is_tot = True

        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            if is_tot:
                name = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
            else:
                name, ara = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")
            
            qaxana = c1.text_input("Lakk. Qaxana (Lakkofsa Qofa)")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 GALMEESSI"):
                if name and details and ogeessa and qaxana:
                    if not qaxana.isdigit():
                        st.error("⚠️ Dogoggora: Lakk. Qaxana keessatti lakkofsa qofa galchi!")
                    else:
                        total = sum(d_fees.values())
                        new_row = [datetime.now().strftime('%d/%m/%Y %H:%M'), name, ara, qaxana, ", ".join(details), ogeessa, total]
                        df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                        save_data(df); st.success("✅ Galmeeffameera!")
                        
    elif menu == "📜 Clearance (Ragaa)":
        st.header("📜 Waraqaa Qulqullinaa")
        up_col1, up_col2 = st.columns(2)
        cl_l = up_col1.file_uploader("Logo Bitaa", type=['png', 'jpg', 'jpeg'], key="cl_l")
        cl_r = up_col2.file_uploader("Logo Mirgaa", type=['png', 'jpg', 'jpeg'], key="cl_r")

        with st.form("clearance"):
            c1, c2 = st.columns(2)
            m = {
                'maqaa': c1.text_input("Maqaa Abbaa Qabiyyee"), 
                'araddaa': c2.text_input("Araddaa"), 
                'qaxana': c1.text_input("Lakk. Qaxana (Lakkofsa Qofa)"), 
                'kaartaa': c2.text_input("Lakk. Kaartaa (Lakkofsa Qofa)"), 
                'gosa_qabiyyee': c1.selectbox("Gosa Qabiyyee", ["Liizii", "Permit"]), 
                'bara_gibiraa': c2.text_input("Bara Gibiraa (Lakkofsa Qofa)"), 
                'dhimma': c1.selectbox("Dhimma Barbaadame", ["Gurgurtaa", "Liqii", "Kennaa"]), 
                'head_name': st.text_input("Maqaa Itti Gaafatamaa")
            }
            if st.form_submit_button("📄 PDF UUMI"):
                # SIRREEFFAMA: Lakkofsa qofa ta'uu isaanii mirkaneessuuf
                if not (m['qaxana'].isdigit() and m['kaartaa'].isdigit() and m['bara_gibiraa'].isdigit()):
                    st.error("⚠️ Dogoggora: Qaxana, Kaartaa fi Bara Gibiraa keessatti Lakkofsa qofa galchi!")
                elif m['maqaa'] and m['head_name']:
                    st.session_state.pdf_to_download = create_clearance_pdf(m, cl_l, cl_r)
                    st.session_state.pdf_name = f"Clearance_{m['maqaa']}.pdf"
                    st.rerun()
                else:
                    st.warning("Maaloo bayyee isaa guuti!")

        if 'pdf_to_download' in st.session_state:
            st.download_button("📥 PDF BUUFADHU", st.session_state.pdf_to_download, st.session_state.pdf_name)

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
        up_c1, up_c2 = st.columns(2)
        cert_logo_l = up_c1.file_uploader("Logo Bitaa Sartiifikeetaa", type=['png', 'jpg', 'jpeg'], key="cert_l")
        cert_logo_r = up_c2.file_uploader("Logo Mirgaa Sartiifikeetaa", type=['png', 'jpg', 'jpeg'], key="cert_r")
        h_name = st.text_input("Maqaa Itti Gaafatamaa (Badhaasaaf)")
        
        if not df.empty:
            stats = df['Maqaa_Ogeessa'].value_counts()
            for i, (name, count) in enumerate(stats.head(3).items()):
                st.divider()
                st.write(f"Sadarkaa {i+1}: **{name}** ({count} Dhimma)")
                if h_name:
                    st.download_button(
                        label=f"📥 Sartiifikeeta {name} Buufadhu", 
                        data=create_pdf_cert(name, count, i+1, cert_logo_l, cert_logo_r, h_name), 
                        file_name=f"Cert_{name}.pdf",
                        key=f"btn_{name}"
                    )

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False; st.rerun()







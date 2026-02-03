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
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)"],
            "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
            "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"]
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
                        st.download_button("📥 Nagahee PDF", create_receipt_pdf(new_row), f"Nagahee_{name}.pdf")

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



import streamlit as st
import os
import requests
import pandas as pd
import qrcode
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land Customer Registration System", layout="wide", page_icon="🏢")

USER_NAME = "admin"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

# --- 2. CSS CUSTOM STYLE (HALLUU FI MIIDHAGSITUU) ---
st.markdown("""
    <style>
    /* Background guutuu */
    .stApp { background-color: #ffffff; }
    
    /* Header Box - Gradient Miidhagaa */
    .header-box { 
        text-align: center; padding: 50px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
        color: white; border-radius: 25px; margin-bottom: 40px;
        box-shadow: 0 15px 30px rgba(30, 58, 138, 0.2);
    }
    
    /* Metric Cards - Bifa Professional */
    .metric-card {
        background: white; padding: 30px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border-top: 5px solid #d4af37; /* Halluu Guldii (Gold) */
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-8px); }
    .metric-card h4 { color: #64748b; margin-bottom: 10px; font-size: 1.1rem; }
    .metric-card h2 { color: #1e3a8a; font-size: 2.2rem; font-weight: 800; }

    /* Login Card */
    .login-card { 
        max-width: 450px; margin: auto; padding: 60px; 
        background: white; border-radius: 30px; 
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15); 
        text-align: center; border: 1px solid #e2e8f0;
    }
    
    /* Buttons - Custom Style */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white; font-weight: bold; border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background: #22c55e; box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4); }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #f1f5f9; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKSHIINIIWWAN (HELPERS) ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # Border Miidhagaa (Navy & Gold)
    pdf.set_draw_color(30, 58, 138) 
    pdf.set_line_width(4)
    pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(212, 175, 55) # Gold
    pdf.set_line_width(1.5)
    pdf.rect(13, 13, 271, 184)

    if LOGO_PATH: pdf.image(LOGO_PATH, x=133, y=18, w=30)
    
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 36)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 15, 'SARTIFIKETII KABAJAA', ln=True, align='C')
    
    pdf.ln(15)
    pdf.set_font('Arial', '', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Badhaasni kun ogeessa gahumsa qabuuf kenname:', ln=True, align='C')
    
    pdf.ln(8)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(184, 134, 11) # Gold text
    pdf.cell(0, 20, name.upper(), ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    content = f"Waggaa {year} keessa tajaajila gaarii fi gahumsa qabuun hojjechuun badhaasa sadarkaa {rank}ffaa waan ta'aniif qophaa'e."
    pdf.multi_cell(0, 10, content, align='C')
    
    pdf.set_xy(180, 170)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(80, 7, "_______________________", ln=True, align='C')
    pdf.set_x(180)
    pdf.cell(80, 7, "Obbo Aqiil Abdujaliil", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SEENSA (AUTHENTICATION) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<br><br><br>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=120)
        st.markdown("<h2 style='color:#22c55e; margin-top:15px;'>Dadar Land Administration Customer Registration System</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#22c55e;'>Maaloo ragaa kee galchuun seeni</p>", unsafe_allow_html=True)
        u = st.text_input("Username", placeholder="Maqaa kee...")
        p = st.text_input("Password", type="password", placeholder="Fungulaa...")
        if st.button("SEENI / LOGIN"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. MAIN UI ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.markdown("<h3 style='text-align:center; color:#22c55e;'>Dadar Land Administration Customer Registration System</h3>", unsafe_allow_html=True)
        st.divider()
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Menu Filadhu", menu)
        st.info(f"📅 Hardha: {to_ethiopian(datetime.now())}")

    # Header section
    st.markdown(f"""
        <div class="header-box">
            <h1 style='margin:0; font-weight:800; font-size:2.8rem;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>
            <p style='font-size:1.4rem; opacity:0.9; font-weight:300;'>Sistama Bulchiinsa Ragaa fi Galmee Ammayyaa</p>
        </div>
        """, unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            
            # Metric Cards Miidhagaa
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h4>👥 Abbootii Dhimmaa</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2:
                rev = df.iloc[:, -1].astype(float).sum()
                st.markdown(f'<div class="metric-card"><h4>💰 Galii Waligalaa</h4><h2>{rev:,.0f} <small style="font-size:1rem;">ETB</small></h2></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h4>✅ Status</h4><h2>Active</h2></div>', unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.subheader("🕒 Galmeewwan Dhiyoo")
                st.dataframe(df.tail(10), use_container_width=True)
            with col_r:
                st.subheader("📊 Gosa Tajaajilaa")
                st.bar_chart(df[5].value_counts(), color="#1e3a8a")
        else:
            st.info("Ragaan galmaa'e hin jiru.")

elif choice == "📝 Galmee Haaraa":
        st.markdown("<div style='background:white; padding:40px; border-radius:25px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        st.subheader("📝 Ragaa Abbaa Dhimmaa Galmeessi")
        with st.form("MyForm", clear_on_submit=True):
            cl1, cl2 = st.columns(2)
            with cl1:
                ad = st.text_input("👤 Maqaa Abbaa Dhimmaa")
                ar = st.text_input("📍 Araddaa")
                wi = st.text_input("🏢 Wirtuu")
            with cl2:
                gs = st.selectbox("🛠 Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Gibira"])
                og = st.text_input("👨‍💼 Maqaa Ogeessaa")
                k_wal = st.number_input("💵 Kafaltii Waligalaa", 0.0)
            
            if st.form_submit_button("✅ GALMEE MIRKANEEESSI"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                line = f"{now}|{ad}|{ar}|{wi}|-|{gs}|{og}|-|Hardha|0|0|0|{k_wal}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                st.success(f"Ragaan '{ad}' milkiin galmaa'eera!")
                st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📄 Gabaasa Gurguddaa", "🎓 Sartifiketii Badhaasaa"])
        
        with tab1:
            st.subheader("Gabaasa Excel Buufadhu")
            if os.path.exists(DATA_FILE):
                df_view = pd.read_csv(DATA_FILE, sep="|", header=None)
                st.dataframe(df_view)
                st.button("🚀 GABAASA TELEGRAM-ITTI ERGI")
        
        with tab2:
            st.subheader("Sartifiketii Miidhagaa Uumi")
            c_name = st.text_input("Maqaa Ogeessaa")
            c_rank = st.selectbox("Sadarkaa Argatan", ["1ffaa", "2ffaa", "3ffaa"])
            c_year = st.text_input("Waggaa (E.C)", "2017")
            if st.button("🎨 SARTIFIKETII GENERATE"):
                if c_name:
                    pdf_out = generate_certificate(c_name, c_rank, c_year)
                    st.download_button("📥 Buufadhu (PDF)", pdf_out, f"{c_name}_Award.pdf")
                    st.balloons()

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()


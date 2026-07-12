import streamlit as st
import pandas as pd
import os
import io
import requests
import tempfile
from datetime import datetime, timedelta
from fpdf import FPDF

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

# ================= 2. DATA MANAGEMENT & TELEGRAM =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    df['Date_Temp'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Ji\'a'] = df['Date_Temp'].dt.month_name()
    df['Kurmaana'] = df['Date_Temp'].dt.quarter.map({1: "Q1 (Jan-Mar)", 2: "Q2 (Apr-Jun)", 3: "Q3 (Jul-Sep)", 4: "Q4 (Oct-Dec)"})
    return df

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

def send_telegram_report(file_bytes, filename):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (filename, file_bytes)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': f"📊 Gabaasa Galii Dadar\n📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}"}
    try:
        response = requests.post(url, data=data, files=files)
        return response.json()
    except Exception as e:
        return str(e)

def create_pdf_cert(name, count, rank, logo_left, logo_right):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluu sadarkaa
    colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = colors.get(rank, (0, 0, 0))
    pdf.set_draw_color(r, g, b)
    pdf.set_line_width(5)
    pdf.rect(10, 10, 277, 190)
    
    # Logo Bitaa
    if logo_left is not None:
        try:
            # Extension isaa addaan baasuuf (jpg ykn png)
            ext = logo_left.name.split('.')[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                tmp.write(logo_left.getvalue())
                tmp_path = tmp.name
            pdf.image(tmp_path, 20, 20, 30)
            os.unlink(tmp_path) # File yeroo gabaabaa hukkumuu
        except:
            pass

    # Logo Mirgaa
    if logo_right is not None:
        try:
            ext = logo_right.name.split('.')[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                tmp.write(logo_right.getvalue())
                tmp_path = tmp.name
            pdf.image(tmp_path, 247, 20, 30)
            os.unlink(tmp_path)
        except:
            pass

# Barreeffama sartiifiikeetaa
    pdf.set_y(45)
    pdf.set_font("Arial", 'B', 30)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 20, "SARTIIFIIKEETA BADHAASAA", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Kun kan kennameef:", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 35)
    pdf.cell(0, 25, name.upper(), ln=True, align='C')
    
    pdf.set_font("Arial", '', 16)
    pdf.multi_cell(0, 10, f"Ogeessa bara kana keessa tajaajila addaa kennuun dhimmoota {count} \nraawwachuun sadarkaa {rank}ffaa argataniif.", align='C')
    
    pdf.set_y(165)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "__________________________", ln=True, align='C')
    pdf.cell(0, 10, "Itti Gaafatamaa Mana Hojii", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        with st.form("login_form"):
            st.markdown("<h2 style='text-align: center;'>Admin Login</h2>", unsafe_allow_html=True)
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI", use_container_width=True):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Ragaan galchaa sirrii miti!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("<h3 style='text-align:center;'>Wajjira Lafaa Bul/Magaalaa Dadar</h3>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("Filannoo", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🏆 Badhaasa Ogeeyyii", "🚪 Logout"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        h_c1, h_c2 = st.columns([0.1, 0.9])
        with h_c1: 
            if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=70)
        with h_c2: st.title("Dashboard Waliigalaa")
        if not df.empty:
            f1, f2, f3 = st.columns(3)
            with f1: period = st.selectbox("Yeroon Calali:", ["Hunda", "Torban Darbe", "Ji'aan", "Kurmaanaan"])
            display_df = df.copy()
            if period == "Torban Darbe":
                display_df = display_df[display_df['Date_Temp'] >= (datetime.now() - timedelta(days=7))]
            elif period == "Ji'aan":
                with f2:
                    sel_m = st.multiselect("Ji'a Filadhu:", MONTH_ORDER)
                    if sel_m: display_df = display_df[display_df['Ji\'a'].isin(sel_m)]
            elif period == "Kurmaanaan":
                with f3:
                    sel_q = st.multiselect("Kurmaana Filadhu:", ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dec)"])
                    if sel_q: display_df = display_df[display_df['Kurmaana'].isin(sel_q)]
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{display_df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(display_df)}</p></div>", unsafe_allow_html=True)
            with c3: 
                top_og = display_df['Maqaa_Ogeessa'].mode()[0] if not display_df.empty else "-"
                st.markdown(f"<div class='card'><p>🏆 Ogeessa Filatamaa</p><p class='metric-value' style='font-size:1.4rem;'>{top_og}</p></div>", unsafe_allow_html=True)
        else: st.info("Datiin galmaa'e hin jiru.")

# --- REGISTRATION ---
    elif menu == "📝 Galmee Tajaajilaa":
        h_c1, h_c2 = st.columns([0.1, 0.9])
        with h_c1:
            if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=65)
        with h_c2: st.markdown("<h2 style='margin-top:10px;'>Galmee Haaraa Galchi</h2>", unsafe_allow_html=True)
        GATII_DICT = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
            "🏗 Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
            "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
            "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"]
        }
        sel_main = st.multiselect("🟢 Ramaddii Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        if sel_main:
            for g in sel_main:
                subs = st.multiselect(f"Filadhu ({g}):", GATII_DICT[g], key=f"s_{g}")
                if subs:
                    sub_cols = st.columns(len(subs))
                    for idx, s in enumerate(subs):
                        with sub_cols[idx]:
                            fee = st.number_input(f"Gatii {s}", min_value=0.0, key=f"v_{idx}_{s}")

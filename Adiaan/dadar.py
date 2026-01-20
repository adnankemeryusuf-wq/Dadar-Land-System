import streamlit as st
import pandas as pd
import sqlite3
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
import plotly.express as px

# ================= 1. CONFIGURATION (Si'a tokko qofa) =================
# Wide layout yoo barbaadde "wide" godhi, yoo kaardii qofa ta'e "centered" filadhu
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

# ================= 2. STYLE & HIDING ELEMENTS =================
st.markdown("""
    <style>
    /* 1. Background Kaalara */
    .stApp { background-color: #f0f2f5; }
    
    /* 2. Dhokstuu (Header, Footer, Menu, Deploy) */
    [data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; visibility: hidden !important; }
    .stDeployButton, .stAppDeployButton { display: none !important; visibility: hidden !important; }
    #MainMenu { display: none !important; visibility: hidden !important; }
    div[data-testid="stFooterContainer"] { display: none !important; }

    /* 3. Metric Cards Style */
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border-top: 10px solid #006400;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .card h3 { margin: 0; color: #444; font-size: 16px; font-weight: bold; }
    .card h2 { margin: 10px 0 0 0; color: #006400; font-size: 32px; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. PATHS & VARIABLES =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
MONTH_ORDER = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# 3. Library-wwan biroo (Si'a tokko qofa asitti walitti qabi)
import pandas as pd
import sqlite3
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
import plotly.express as px
# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
# Tartiba ji'ootaa gabaasaaf
MONTH_ORDER = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", layout="wide")

st.markdown("""
    <style>
    /* 1. Koodii CSS kan ati duraan qabdu (Background & Cards) */
    .stApp { background-color: #f0f2f5; }
    
    /* 2. Sararoota dhokstuu (Isan amma siif ibse) */
    [data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; visibility: hidden !important; }
    .stDeployButton, .stAppDeployButton { display: none !important; }
    #MainMenu { visibility: hidden; }
    div[data-testid="stFooterContainer"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Data Variables
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Ji\'a']
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Dhimma Dhala (Inheritance)"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"]
}

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
        df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df_to_save):
    df_to_save.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf_cert(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    # Note: logo images handling would need extra logic if passed as BytesIO
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. NAVIGATION & LOGIN =================
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        st.title("🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "1234":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO:", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "🔍 Barbaadi/Edit", "Ba'i"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #1b5e20;'>📊 Dashboard Raawwii Hojii</h2>", unsafe_allow_html=True)
        
        st.markdown("### 🔍 Calaltuu Guyyaa")
        with st.container():
            c1, c2, c3 = st.columns([2, 2, 1])
            start_date = c1.date_input("Irraa:", datetime(2024, 1, 1))
            end_date = c2.date_input("Hanga:", datetime.now())
            if c3.button("Filter"):
                st.success("Data'n yeroof calalameera!") 
        
        st.divider()

        if not df.empty:
            st.markdown("#### 📂 Dashboard Waliigalaa")
            m1, m2, m3, m4 = st.columns(4)
            
            total_apps = len(df)
            total_rev = df['Kafaltii_Taj'].sum()
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else "-"
            
            m1.markdown(f"<div class='card'><h3>Applications</h3><h2>{total_apps}</h2></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='card'><h3>Galii (ETB)</h3><h2>{total_rev:,.0f}</h2></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='card'><h3>Ogeessa</h3><h2 style='font-size:18px;'>{top_og}</h2></div>", unsafe_allow_html=True)
            m4.markdown(f"<div class='card'><h3>Certificates</h3><h2>32</h2></div>", unsafe_allow_html=True)
            
            st.write("##")

            col_left, col_right = st.columns([3, 2])
            with col_left:
                st.subheader("📈 Graphical Report")
                # Pie chart based on Services
                fig_data = df['Gosa_Tajajjilaa'].value_counts().reset_index()
                fig_data.columns = ['Service', 'Count']
                fig = px.pie(fig_data, values='Count', names='Service', hole=0.5)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_right:
                st.subheader("📑 Tabular Report")
                st.dataframe(fig_data, use_container_width=True, hide_index=True)
                st.markdown("---")
                st.caption("Trendii Galii Ji'aan")
                if 'Ji\'a' in df.columns:
                    trend = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
                    st.line_chart(trend)
        else:
            st.info("Data'n galmeeffame hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa Filadhu:", list(SERVICE_STRUCTURE.keys()))
        final_services, total_fee = [], 0
        
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    subs = st.multiselect(f"{cat}:", SERVICE_STRUCTURE[cat], key=cat)
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"f_{s}")
                        final_services.append(s); total_fee += fee

        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services:
                    now = datetime.now()
                    new_row = [now.strftime('%d/%m/%Y'), name, ara, "-", ", ".join(final_services), ogeessa, total_fee, now.strftime('%B')]
                    new_df = pd.DataFrame([new_row], columns=COL_NAMES)
                    df = pd.concat([df, new_df], ignore_index=True)
                    save_data(df)
                    st.success("Milkaa'inaan Galmeeffameera!")
                else: st.error("Odeeffannoo guuti!")

    # --- OTHER MENUS ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.title("📈 Gabaasa Bal'aa")
        st.dataframe(df, use_container_width=True)
        st.metric("Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")

    elif menu == "🏆 Badhaasa":
        st.title("🏆 Sartiifiikeeta Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            l_left = st.file_uploader("Logo Bita", type=["png","jpg"])
            l_right = st.file_uploader("Logo Mirga", type=["png","jpg"])
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>Sadarkaa {i+1}</h3><h2>{name}</h2><p>{count} Hojii</p></div>", unsafe_allow_html=True)
                    if st.button(f"Sartiifiikeeta {name}"):
                        pdf_bytes = create_pdf_cert(name, count, i+1)
                        st.download_button("Download PDF", pdf_bytes, f"{name}_Cert.pdf")

    elif menu == "🔍 Barbaadi/Edit":
        st.title("🔍 Barbaadi / Edit")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()












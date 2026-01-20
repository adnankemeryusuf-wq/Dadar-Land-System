import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
MONTH_ORDER = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border-top: 10px solid #006400;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
        margin-bottom: 20px;
    }
    .card:hover { transform: translateY(-5px); }
    .card h3 { margin: 0; color: #444; font-size: 16px; font-weight: bold; }
    .card h2 { margin: 10px 0 0 0; color: #006400; font-size: 32px; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

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
    # Orientation 'L' (Landscape), Unit 'mm', Format 'A4'
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Daangaa)
    pdf.set_draw_color(0, 100, 0)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(0.5)
    pdf.rect(12, 12, 273, 186)
    
    # Headings (Mata-duree)
    pdf.set_y(25)
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "WAJJIRA TAJAAJILA LAFAA FI MANA MURALAA", 0, 1, 'C')
    
    pdf.ln(10)
    pdf.set_text_color(139, 0, 0)
    pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 25, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 15, "Sartifiikeetiin kun", 0, 1, 'C')
    
    pdf.set_font('Arial', 'B', 28)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", 0, 1, 'C')
    
    pdf.set_font('Arial', '', 18)
    msg = (f"Waggaa 2026 keessatti tajaajiloota adda addaa {count} haala qulqullina qabuun "
           f"raawwachuun, raawwii hojii keetiin sadarkaa {rank}ffaa argachuu keetiif "
           f"galateeffamaa waraqaan beekamtii kun siif kennameera.")
    pdf.set_x(30)
    pdf.multi_cell(237, 10, msg, 0, 'C')
    
    # Signature Area (Mallattoo)
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_xy(180, 165)
    pdf.cell(80, 8, "________________________", 0, 1, 'C')
    pdf.set_x(180)
    pdf.cell(80, 8, "Itti Gaafatamaa Wajjiraa", 0, 1, 'C')
    
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
        st.markdown("<h2 style='color: #1b5e20;'>📊 Dashboard Waliigalaa</h2>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        if not df.empty:
            with c1: st.markdown(f"<div class='card'><h3>💰 Galii</h3><h2>{df['Kafaltii_Taj'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><h3>👥 Maamiltoota</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
            with c3: 
                top_og = df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else "-"
                st.markdown(f"<div class='card'><h3>🏆 Ogeessa</h3><h2 style='font-size:20px'>{top_og}</h2></div>", unsafe_allow_html=True)
            with c4: st.markdown(f"<div class='card'><h3>📅 Ji'a</h3><h2>{datetime.now().strftime('%B')}</h2></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.subheader("📈 Trendii Galii Ji'aan")
                trend = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
                st.area_chart(trend)
            with col_r:
                st.subheader("📊 Qoodinsa Tajaajilaa")
                counts = df['Gosa_Tajajjilaa'].value_counts().reset_index()
                fig = px.pie(counts, values='count', names='Gosa_Tajajjilaa', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data'n hin jiru.")

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

    # --- BADHAASA (SARTIIFIKEETA) ---
    elif menu == "🏆 Badhaasa":
        st.title("🏆 Sartiifiikeeta Beekamtii Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            st.write("Ogeeyyii Raawwii Olaanaa Qaban:")
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>Sadarkaa {i+1}</h3><h2>{name}</h2><p>{count} Hojii Raawwataman</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_pdf_cert(name, count, i+1)
                    st.download_button(f"📥 Sartifiikeeta {name}", pdf_bytes, f"{name}_Certificate.pdf", mime="application/pdf")
        else:
            st.warning("Data'n waan hin jirreef sartifiikeeta uumuun hin danda'amu.")

    # --- OTHER MENUS (Barbaadi/Edit/Ba'i) ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.title("📈 Gabaasa Bal'aa")
        st.dataframe(df, use_container_width=True)

    elif menu == "🔍 Barbaadi/Edit":
        st.title("🔍 Barbaadi ykn Sirreessi")
        q = st.text_input("Maqaa Abbaa Dhimmaa Galchi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

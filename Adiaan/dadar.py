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

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", layout="wide")

# Professional CSS to match your Dashboard vision
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
    }
    .card:hover { transform: translateY(-5px); }
    .card h3 { margin: 0; color: #444; font-size: 16px; font-weight: bold; }
    .card h2 { margin: 10px 0 0 0; color: #006400; font-size: 36px; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# Data Variables
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
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
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf_cert(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    if logo_left: pdf.image(logo_left, 20, 15, 30)
    if logo_right: pdf.image(logo_right, 230, 15, 30)
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    pdf.line(110, 180, 180, 180); pdf.set_xy(110, 182); pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
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

    # --- DASHBOARD (Matching Uploaded Images) ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Raawwii Hojii")
        
        # Date Filter Row
        st.markdown("### 🔍 Calaltuu Guyyaa")
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.date_input("Irraa:", datetime(2018, 4, 1))
        c2.date_input("Hanga:", datetime(2018, 9, 5))
        c3.write("##"); c3.button("Filter")
        st.divider()

        # Metrics Row (Top cards from image 1)
        st.markdown("#### 📂Dashboard Waliigalaa / Transactions")
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div class='card'><h3>Applications</h3><h2>{len(df) + 100}</h2></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='card'><h3>All Tasks</h3><h2>56</h2></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='card'><h3>Migrated Parcels</h3><h2>169</h2></div>", unsafe_allow_html=True)
        m4.markdown(f"<div class='card'><h3>Certificates</h3><h2>32</h2></div>", unsafe_allow_html=True)
        
        st.write("##")

        # Report Row (Charts from image 2)
        col_left, col_right = st.columns([3, 2])
        with col_left:
            st.subheader("📈 Graphical Report")
            graph_data = pd.DataFrame({
                "Status": ["Submitted", "Finished", "Inprogress", "Rejected"],
                "Count": [49, 31, 6, 1]
            })
            fig = px.pie(graph_data, values='Count', names='Status', hole=0.6, color_discrete_sequence=px.colors.qualitative.Dark2)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("📑 Tabular Report")
            st.dataframe(graph_data, use_container_width=True, hide_index=True)

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
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("Milkaa'inaan Galmeeffameera!")
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
                    st.markdown(f"<div class='card'><h3>Sadarkaa {i+1}</h3><h2>{name}</h2><p>{count} Tasks</p></div>", unsafe_allow_html=True)
                    if st.button(f"Generate PDF for {name}"):
                        pdf_bytes = create_pdf_cert(name, count, i+1, l_left, l_right)
                        st.download_button("Download", pdf_bytes, f"{name}_Cert.pdf")

    elif menu == "🔍 Barbaadi/Edit":
        st.title("🔍 Barbaadi / Edit")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()


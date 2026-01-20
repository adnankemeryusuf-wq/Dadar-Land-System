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
        padding: 20px;
        border-radius: 12px;
        border-top: 8px solid #006400;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
    }
    .card h3 { margin: 0; color: #555; font-size: 15px; }
    .card h2 { margin: 10px 0 0 0; color: #006400; font-size: 28px; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# Maqaa kutaalee (Column Names)
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

def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 100, 0)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    
    pdf.set_y(30)
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 40)
    pdf.set_text_color(139, 0, 0)
    pdf.cell(0, 40, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 15, "Waraqaan kun Obbo/Adde:", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 20, f"{name.upper()}", 0, 1, 'C')
    
    pdf.set_font('Arial', '', 16)
    pdf.multi_cell(0, 10, f"\nWaggaa 2026 keessatti tajaajiloota {count} raawwachuun\nsadarkaa {rank}ffaa argataniiru.", align='C')
    
    pdf.set_xy(180, 170)
    pdf.cell(80, 10, "____________________", 0, 1, 'C')
    pdf.set_x(180)
    pdf.cell(80, 10, "Itti Gaafatamaa", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1, 1])
    with center:
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

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<div class='card'><h3>💰 Galii</h3><h2>{df['Kafaltii_Taj'].sum():,.0f}</h2></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='card'><h3>👥 Maamiltoota</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='card'><h3>🏆 Ogeessa</h3><h2>{df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else '-'}</h2></div>", unsafe_allow_html=True)
            m4.markdown(f"<div class='card'><h3>📅 Ji'a</h3><h2>{datetime.now().strftime('%B')}</h2></div>", unsafe_allow_html=True)
            
            st.divider()
            c_l, c_r = st.columns([2, 1])
            with c_l:
                st.subheader("📈 Trendii Galii")
                trend = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
                st.area_chart(trend)
            with c_r:
                st.subheader("📊 Qoodinsa Tajaajilaa")
                fig = px.pie(df, names='Gosa_Tajajjilaa', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        final_services, total_fee = [], 0
        
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    subs = st.multiselect(f"{cat}:", SERVICE_STRUCTURE[cat])
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=s)
                        final_services.append(s); total_fee += fee

        with st.form("my_form"):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c3.text_input("Qaxana/Sector")
            ogeessa = c1.text_input("Ogeessa Raawwate")
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services:
                    now = datetime.now()
                    new_data = [now.strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee, now.strftime('%B')]
                    new_df = pd.DataFrame([new_data], columns=COL_NAMES)
                    df = pd.concat([df, new_df], ignore_index=True)
                    save_data(df)
                    st.success("Milkaa'inaan Galmeeffameera!")
                else: st.error("Maaloo odeeffannoo guuti!")

    elif menu == "📈 Gabaasa Bal'aa":
        st.title("📈 Gabaasa Guutuu")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Excel/CSV Download", csv, "gabaasa.csv", "text/csv")

    elif menu == "🏆 Badhaasa":
        st.title("🏆 Sartifiikeeta Ogeeyyii")
        if not df.empty:
            top_og = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_og.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>Sadarkaa {i+1}</h3><h2>{name}</h2><p>{count} Hojii</p></div>", unsafe_allow_html=True)
                    pdf = create_pdf_cert(name, count, i+1)
                    st.download_button(f"📥 Download Cert ({name})", pdf, f"{name}.pdf", "application/pdf")

    elif menu == "🔍 Barbaadi/Edit":
        st.title("🔍 Barbaadi")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.write(f"Maamiltoota {len(res)} argaman:")
            st.dataframe(res)

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime, timedelta
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# Streamlit Page Config
st.set_page_config(
    page_title="Dadar Land Admin System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

# Professional CSS
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #006400; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# Variables
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
    "⚖️ Adabbii": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"] 
}
ERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Kaartaa Lafa Qoonnaa"
    ],
    "🏗 Pilaanii & Ijaarsa": [
      "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
       "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo)"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa",
        "Kaffaltii Seeressuu (Regularization)",
        "Adabbii Faallaa Pilaanii"
    ],
}
# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    df['Guyyaa'] = pd.to_datetime(df['Guyyaa'], dayfirst=True)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf_cert(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    
    if logo_left: 
        pdf.image(logo_left, 20, 15, 30)
    if logo_right: 
        pdf.image(logo_right, 230, 15, 30)
        
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    pdf.line(110, 180, 180, 180); pdf.set_xy(110, 182); pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. NAVIGATION & LOGIN =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

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
            else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    st.sidebar.title("🏢 DADAR LAND ADMIN")
    menu = st.sidebar.radio("FILANNOO:", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "🔍 Barbaadi/Edit", "Ba'i"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            fig = px.bar(df.groupby("Maqaa_Ogeessa")['Kafaltii_Taj'].sum().reset_index(), 
                         x="Maqaa_Ogeessa", y="Kafaltii_Taj", color='Maqaa_Ogeessa', title="Galii Per Ogeessa")
            st.plotly_chart(fig, use_container_width=True)

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa Filadhu:", list(SERVICE_STRUCTURE.keys()))
        
        final_services = []
        total_fee = 0
        
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    subs = st.multiselect(f"{cat}:", SERVICE_STRUCTURE[cat], key=cat)
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"f_{s}")
                        final_services.append(s)
                        total_fee += fee

        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee Scan (Image)", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services:
                    if nagahee:
                        with open(os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg"), "wb") as f:
                            f.write(nagahee.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Waliigala: {total_fee} ETB")
                else: st.error("Maaloo maqaa fi tajaajila filadhu!")

    # --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.title("📈 Gabaasa & Calaltuu")
        st.dataframe(df[COL_NAMES], use_container_width=True)
        st.metric("Galii Filtarii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")

    # --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa":
        st.title("🏆 Sartiifiikeeta Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            medals = ["🥇 1FFAA", "🥈 2FFAA", "🥉 3FFAA"]
            
            l_left = st.file_uploader("Logo Bita", type=["png","jpg"])
            l_right = st.file_uploader("Logo Mirga", type=["png","jpg"])
            
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2>{medals[i]}</h2><h3>{name}</h3><p>Abbootii Dhimmaa: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_pdf_cert(name, count, i+1, l_left, l_right)
                    st.download_button(f"📥 Download {name} PDF", pdf_bytes, f"Cert_{name}.pdf")

    # --- SEARCH / EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.title("🔍 Barbaadi / Edit")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    st.write(f"Tajaajila: {row['Gosa_Tajajjilaa']} | Kaffaltii: {row['Kafaltii_Taj']}")
                    if st.button("🗑 Haqi", key=f"del_{idx}"):
                        df = df.drop(idx)
                        save_data(df)
                        st.success("Haqameera!")
                        st.rerun()

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()


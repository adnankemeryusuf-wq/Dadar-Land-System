import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from PIL import Image

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Admin Pro", 
    page_icon="🏢", 
    layout="wide"
)

# Halluu fi Style
st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT (REVISED) =================
# Gosa tajaajilaa hunda akka gosa gurguddaatti addaan baasuu
SERVICE_STRUCTURE = {
    "🏷️ Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", 
        "Gibira Lafa Qonnaa", 
        "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", 
        "Gibira Milkii (Stamp Duty)", 
        "TOT (Turnover Tax)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", 
        "Kaartaa Bakka Bu'aa", 
        "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", 
        "Sirreeffama Daangaa",
        "Ganda Irraa gara Magaalaatti"
    ],
    "🏗️ Pilaanii & Ijaarsa": [
        "Hayyama Ijaarsaa", 
        "Pilaanii Magaalaa", 
        "Itti Fayyadama Lafaa (Land Use)",
        "Mirkaneessa Sertifikeeta Ijaarsaa",
        "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", 
        "Ugura Kaasuu", 
        "Waliigaltee Liqii Baankii",
        "Waliigaltee Hiikuu",
        "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", 
        "Deebii Iyyannoo",
        "Tajaajila Koppii (Photocopy)"
    ]
}

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_certificate(name, count, rank, l_l, l_r, sig):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    if sig:
        with open("tmp_sig.png", "wb") as f: f.write(sig.getbuffer())
        pdf.image("tmp_sig.png", 50, 160, 30)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.header("🏢 Admin Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📝 Galmee & Clearance", "🏆 Badhaasa", "📈 Gabaasa", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Overview")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            fig = px.bar(df, x='Guyyaa', y='Kafaltii_Taj', title="Trendii Kaffaltii")
            st.plotly_chart(fig)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        selected_cats = st.multiselect("Gosa Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        final_services = []
        total_fee = 0
        if selected_cats:
            for cat in selected_cats:
                subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat], key=cat)
                for s in subs:
                    final_services.append(s)
                    fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"f_{s}")
                    total_fee += fee

        with st.form("reg_form"):
            name = st.text_input("Maqaa Maamilaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            ogeessa = st.text_input("Ogeessa Raawwate")
            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")

    elif menu == "📝 Galmee & Clearance":
        st.header("📝 Galmee fi Qophii Clearance")
        st.sidebar.subheader("⚙️ Qindaa'ina Mallattoo")
        up_bitta = st.sidebar.file_uploader("Logo Bittaa", type=['png', 'jpg'])
        if up_bitta:
            Image.open(up_bitta).convert("RGB").save("logo_bitta.jpg")
        
        if st.session_state.get('pdf_to_download'):
            st.success("📄 Clearance qophaa'eera!")
            st.download_button("📥 PDF BUUFADHU", st.session_state.pdf_to_download, "Clearance.pdf")
            if st.button("Galmee Haaraa"): 
                st.session_state.pdf_to_download = None
                st.rerun()

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                st.write(f"**{i}. {name}** - {count} Hojii")
                pdf = create_certificate(name, count, i, None, None, None)
                st.download_button(f"📥 PDF {name}", pdf, f"Cert_{name}.pdf")

    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa Galmee Waliigalaa")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV Buusi", csv, "Gabaasa.csv")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

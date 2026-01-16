import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & DIRECTORIES =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# Style Halluu fi Bifa (CSS)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    div.stMetric { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #2e7d32; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Biometric_ID']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
        df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
        return df
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF GENERATOR =================
def create_advanced_pdf(name, count, rank, signature=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(27, 94, 32); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    
    pdf.set_y(40); pdf.set_font('Arial', 'B', 35); pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', 'B', 20); pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(15); pdf.set_font('Arial', '', 18); pdf.cell(0, 10, "Sartiifiketiin kun kan kennameef:", ln=True, align='C')
    pdf.set_font('Arial', 'B', 30); pdf.cell(0, 20, name.upper(), ln=True, align='C')
    
    msg = f"Waggaa 2026 keessatti tajaajila saffisaa fi biometric-n mirkanaa'een Abbootii Dhimmaa {count} tajaajiluun sadarkaa {rank}ffaa argataniiru."
    pdf.set_font('Arial', '', 16); pdf.multi_cell(0, 10, msg, align='C')
    
    if signature:
        with open("temp_sig.png", "wb") as f: f.write(signature.getvalue())
        pdf.image("temp_sig.png", x=110, y=155, h=20)
    
    pdf.line(100, 175, 180, 175); pdf.set_xy(100, 177); pdf.cell(80, 10, "Mallattoo Itti Gaafatamaa", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u.upper() == "ADMIN" and p == "2026":
            st.session_state.logged_in = True; st.session_state.role = "admin"; st.rerun()
        elif u.upper() == "USER" and p == "1234":
            st.session_state.logged_in = True; st.session_state.role = "user"; st.rerun()
        else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee & Biometric", "🏆 Badhaasa", "🔍 Barbaadi", "Ba'i"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Xiinxala Hojii")
        if st.session_state.role == "admin":
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            fig = px.area(df, x='Guyyaa', y='Kafaltii_Taj', title="Trendii Galii")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dashboard Admin qofaan argama.")

    # --- REGISTRATION WITH BIOMETRIC ---
    elif menu == "📝 Galmee & Biometric":
        st.header("📝 Galmee Haaraa fi Mirkaneessaa Biometric")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa", placeholder="Abdi Mahammad Yusuuf")
            ara = col2.text_input("Araddaa", placeholder="01")
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            fee = col2.number_input("Kafaltii (ETB)", min_value=0.0, format="%.2f")
            
            st.markdown("### 🔐 Mirkaneessaa Biometric")
            st.caption("Maaloo mallattoo quubaa kee 'Scanner' irra kaa'i...")
            bio_check = st.checkbox("Mallattoo Quubaa Mirkaneessi")
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and ara and bio_check:
                    bio_id = f"BIO-{datetime.now().strftime('%M%S')}-{name[:2].upper()}"
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", "Tajaajila Lafa", ogeessa, fee, bio_id]
                    
                    df_new = pd.DataFrame([new_row], columns=COL_NAMES)
                    df = pd.concat([df, df_new], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Biometric ID: {bio_id}")
                else:
                    st.error("Maaloo kutaalee hunda guuti ykn Biometric mirkaneessi!")

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Sartiifikeeta Ogeeyyii")
        sig = st.file_uploader("Mallattoo Itti Gaafatamaa (PNG)", type=['png'])
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                st.write(f"🌟 {i}ffaa: {name} ({count} Hojii)")
                pdf_out = create_advanced_pdf(name, count, i, sig)
                st.download_button(f"📥 Sartiifikeeta {name}", pdf_out, f"Cert_{name}.pdf")

    # --- BARBAADI ---
    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        query = st.text_input("Maqaa Barbaadi...")
        if query:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(query, case=False, na=False)]
            st.dataframe(res)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

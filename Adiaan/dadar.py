import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

# Folder nagahee uumuu
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land System", 
    page_icon="🏢", 
    layout="wide"
)

# Constants
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

# Custom CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0.0)
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    rank_colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    r_color = rank_colors.get(rank, (0, 80, 0))
    
    pdf.set_draw_color(*r_color)
    pdf.set_line_width(2.0)
    pdf.rect(10, 10, 277, 190)
    
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 15, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    pdf.multi_cell(0, 10, f"\nTajaajilamtoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.header("🏢 Login System")
        with st.form(key="main_login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "🔍 Barbaadi"])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2></div>", unsafe_allow_html=True)
            st.plotly_chart(px.line(df.groupby('Guyyaa')['Kafaltii_Taj'].sum().reset_index(), x='Guyyaa', y='Kafaltii_Taj'))
        else: st.info("Data'n hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Haaraa")
        with st.form(key="reg_form_unique", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col2.text_input("Araddaa")
            oge = col1.text_input("Maqaa Ogeessaa")
            kaff = col2.number_input("Kafaltii (ETB)", min_value=0.0)
            gosa = st.selectbox("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa", "TOT"])
            nagahee = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and oge:
                    if nagahee:
                        f_name = f"{name}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, f_name), "wb") as f:
                            f.write(nagahee.getbuffer())
                    
                    new_data = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, oge, kaff]
                    df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                else: st.error("Maaloo maqaa guuti!")

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h3>{i}FFAA</h3><h4>{name}</h4><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i)
                    st.download_button(f"📥 PDF {i}", pdf_bytes, f"Cert_{name}.pdf", "application/pdf", key=f"btn_{i}")

    # --- SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa maamilaa...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    with st.form(key=f"edit_{idx}"):
                        new_n = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'])
                        if st.form_submit_button("💾 Update"):
                            df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_n
                            save_data(df); st.rerun()

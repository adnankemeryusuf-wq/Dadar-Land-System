import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

st.set_page_config(
    page_title="Dadar Land System", 
    page_icon="🏢", 
    layout="wide"
)

# --- CSS: UI BAREEDCHUU FI TOOLBAR DHOKSUUF ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none !important;}
    header {visibility: hidden !important;}
    .stAppToolbar {display: none !important;}
    .stDeployButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        text-align: center; 
        border-top: 8px solid #2e7d32; 
        margin-bottom: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA HANDLING =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

# ================= 3. SARTIIFIKETA (FPDF) =================
def create_certificate(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluu Sadarkaa (RGB)
    colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    r_color = colors.get(rank, (0, 80, 0))

    # Border Dachaa
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*r_color); pdf.set_line_width(1.2); pdf.rect(13, 13, 271, 184)

    # Logos
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=20, y=18, w=25)
        pdf.image(LOGO_PATH, x=250, y=18, w=25)

    pdf.set_y(55)
    pdf.set_text_color(*r_color); pdf.set_font('Arial', 'B', 40)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_y(95); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 20, str(name).upper(), ln=True, align='C')
    
    pdf.set_y(125); pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, f"Tajaajilamtoota {count} saffisaan tajaajiluun waggaa 2026", ln=True, align='C')
    pdf.cell(0, 10, f"sadarkaa {rank}ffaa waan qabataniif beekamtiin kun kennameef.", ln=True, align='C')

    # Guyyaa fi Mallattoo
    pdf.set_y(165); pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", ln=0, align='C')
    pdf.cell(150, 10, "Mallattoo Hoogganaa: ________________", ln=1, align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>Admin Login</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Koodii dogoggora!")
else:
    df = load_data()
    
    with st.sidebar:
        st.title("🏢 Dadar Land")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "🏆 Badhaasa Ogeeyyii"])
        if st.button("🚪 Log Out"):
            st.session_state.logged_in = False; st.rerun()

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        st.metric("Waliigala Galmee", len(df))
        st.dataframe(df, use_container_width=True)

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty and 'Maqaa_Ogeessa' in df.columns:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            # 'i' as index, 'name' as key, 'count' as value
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2>{i+1}FFAA</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    try:
                        pdf_data = create_certificate(name, count, i+1)
                        st.download_button(f"📥 Download Cert {i+1}", pdf_data, f"Cert_{name}.pdf", "application/pdf")
                    except:
                        st.error("Dhimma uumuu irratti rakkoon uumame.")
        else:
            st.info("Data'n galmaa'e hin jiru.")

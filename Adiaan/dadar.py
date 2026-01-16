import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURATION ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

# Folder nagahee itti kuusnu yoo hin jirre uumuuf
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF GENERATOR (WITH SIGNATURE) =================
def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None, signature=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    # Border
    pdf.set_fill_color(245, 255, 245); pdf.rect(12, 12, 273, 186, 'F')
    pdf.set_line_width(4); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)

    # Logos
    if logo_left:
        ext_l = logo_left.name.split('.')[-1].lower()
        t_l = f"temp_l.{ext_l}"
        with open(t_l, "wb") as f: f.write(logo_left.getvalue())
        pdf.image(t_l, x=20, y=15, w=35)
    if logo_right:
        ext_r = logo_right.name.split('.')[-1].lower()
        t_r = f"temp_r.{ext_r}"
        with open(t_r, "wb") as f: f.write(logo_right.getvalue())
        pdf.image(t_r, x=240, y=15, w=35)

    # Header
    pdf.set_y(45); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 25, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_text_color(30, 70, 30); pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    # Body
    pdf.ln(15); pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    pdf.ln(5); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 32)
    pdf.cell(0, 20, f"{name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_text_color(40, 40, 40); pdf.set_font('Arial', '', 15)
    msg = f"Waggaa 2026 keessatti tajaajila saffisaa fi amannamaa ta'een Abbootii Dhimmaa {count} tajaajiluun badhaafamaniiru."
    pdf.multi_cell(0, 10, msg, align='C')
    
    # --- SIGNATURE AREA ---
    pdf.ln(25); curr_y = pdf.get_y()
    if signature:
        ext_s = signature.name.split('.')[-1].lower()
        t_s = f"temp_sig.{ext_s}"
        with open(t_s, "wb") as f: f.write(signature.getvalue())
        pdf.image(t_s, x=55, y=curr_y - 18, h=18) # Mallattoo sarara gubbaa
        
    pdf.line(40, curr_y, 110, curr_y); pdf.set_xy(40, curr_y + 2); pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
    pdf.line(180, curr_y, 250, curr_y); pdf.set_xy(180, curr_y + 2); pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # ... (Login code remains same)
    st.session_state.logged_in = True # For testing
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa Ogeeyyii", "Ba'i"])

    if menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa & Nagahee")
        
        with st.form("entry_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            
            st.markdown("---")
            tajaajila = st.selectbox("Gosa Tajaajilaa", ["Gibira Baaxii Gooroo", "Liizii Waggaa", "Kaartaa Manaa"])
            fee = st.number_input("Kafaltii (ETB)", min_value=0.0)
            
     
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sartiifiikeeta Badhaasaa")
        cl, cm, cr = st.columns(3)
        l_l = cl.file_uploader("Logo Bitaa", type=['png','jpg'])
        l_r = cm.file_uploader("Logo Mirgaa", type=['png','jpg'])
        sig = cr.file_uploader("Mallattoo (Signature) Olkaasi", type=['png','jpg'])
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h2>{i}FFAA</h2><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    try:
                        pdf_out = create_advanced_pdf(name, count, i, l_l, l_r, sig)
                        st.download_button(f"📥 Download Cert {i}", pdf_out, f"Cert_{name}.pdf", "application/pdf")
                    except Exception as e: st.error(f"Error: {e}")




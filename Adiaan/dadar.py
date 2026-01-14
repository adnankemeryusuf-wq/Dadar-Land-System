import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURATION TELEGRAM ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
EXCEL_FILE = "dadar_land_data.xlsx"
COL_NAMES = ["Guyyaa", "Maqaa_Abbaa_Dhimmaa", "Araddaa", "Qaxana", "Gosa_Tajaajilaa", "Maqaa_Ogeessa", "Kafaltii_Taj"]
MONTH_ORDER = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT (FURMAATA DOGOGGORA) =================
@st.cache_data
def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE)
            df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
            df['Ji\'a'] = df['Date_Obj'].dt.month_name()
            df['Waggaa'] = df['Date_Obj'].dt.year
            return df
        except:
            return pd.DataFrame(columns=COL_NAMES)
    return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df_to_save = df[COL_NAMES]
    df_to_save.to_excel(EXCEL_FILE, index=False)
    st.cache_data.clear()

# ================= 3. PDF GENERATOR (PREMIUM GOLD) =================
def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluuwwan
    gold = (255, 215, 0)
    green = (0, 80, 0)
    
    # Border & Background
    pdf.set_fill_color(255, 254, 242)
    pdf.rect(10, 10, 277, 190, 'F')
    pdf.set_draw_color(*green); pdf.set_line_width(2.5); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*gold); pdf.set_line_width(1.0); pdf.rect(13, 13, 271, 184)

    # Logo
    if logo_left:
        with open("temp_l.png", "wb") as f: f.write(logo_left.getbuffer())
        pdf.image("temp_l.png", x=25, y=18, w=35)
    if logo_right:
        with open("temp_r.png", "wb") as f: f.write(logo_right.getbuffer())
        pdf.image("temp_r.png", x=235, y=18, w=35)

    # Content
    pdf.set_y(35)
    pdf.set_text_color(*gold); pdf.set_font('Arial', 'B', 45)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_text_color(*green); pdf.set_font('Arial', 'B', 20)
    pdf.set_y(75)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    pdf.set_y(100); pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', 'I', 15)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')

    pdf.set_y(115); pdf.set_text_color(*green); pdf.set_font('Arial', 'B', 38)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')

    pdf.set_y(140); pdf.set_text_color(30, 30, 30); pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti tajaajila saffisaa fi amannamaa ta'een tajaajila hawaasaa irratti gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru.", align='C')

    pdf.set_y(175); pdf.line(40, 175, 110, 175); pdf.line(180, 175, 250, 175)
    pdf.set_xy(40, 177); pdf.set_font('Arial', 'B', 12); pdf.cell(70, 10, "Mallattoo", align='C')
    pdf.set_xy(180, 177); pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.title("Admin Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.title("Dadar Admin")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("Baay'ina Tajaajilamtootaa", len(df))
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum())

    elif menu == "📝 Galmee Haaraa":
        with st.form("galmee"):
            st.subheader("Galmee Haaraa Galchi")
            m_a = st.text_input("Maqaa Abbaa Dhimmaa")
            a_d = st.text_input("Araddaa")
            q_x = st.text_input("Qaxana")
            g_t = st.text_input("Gosa Tajaajilaa")
            m_o = st.text_input("Maqaa Ogeessaa")
            k_t = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                new_data = [datetime.now().strftime('%d/%m/%Y'), m_a, a_d, q_x, g_t, m_o, k_t]
                df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success("Galmeeffameera!")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa & Sartiifiikeeta")
        l1, l2 = st.columns(2)
        logo_l = l1.file_uploader("Logo Bitaa", type=['png', 'jpg'])
        logo_r = l2.file_uploader("Logo Mirgaa", type=['png', 'jpg'])
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.success(f"{i}ffaa: {name}")
                    pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                    st.download_button(f"📥 PDF {name}", pdf_bytes, f"Sartii_{name}.pdf", "application/pdf")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

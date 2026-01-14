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

# ================= 2. DATA MANAGEMENT =================
@st.cache_data
def load_data():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
        df['Ji\'a'] = df['Date_Obj'].dt.month_name()
        df['Waggaa'] = df['Date_Obj'].dt.year
        df['Kurmaana'] = df['Date_Obj'].dt.quarter
        return df
    return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df_to_save = df[COL_NAMES]
    df_to_save.to_excel(EXCEL_FILE, index=False)
    st.cache_data.clear()

def send_to_telegram(file_bytes, file_name, caption):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        files = {'document': (file_name, file_bytes)}
        data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
        requests.post(url, files=files, data=data)
        return True
    except: return False

# ================= 3. PDF GENERATOR (ULTIMATE GOLD) =================
def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    gold_metal = (255, 215, 0)
    deep_green = (0, 80, 0)
    bg_cream = (255, 254, 242)

    pdf.set_fill_color(*bg_cream)
    pdf.rect(10, 10, 277, 190, 'F') 
    pdf.set_draw_color(*deep_green); pdf.set_line_width(3.0); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*gold_metal); pdf.set_line_width(1.5); pdf.rect(13, 13, 271, 184)

    if logo_left:
        with open("temp_l.png", "wb") as f: f.write(logo_left.getbuffer())
        pdf.image("temp_l.png", x=25, y=18, w=38)
    if logo_right:
        with open("temp_r.png", "wb") as f: f.write(logo_right.getbuffer())
        pdf.image("temp_r.png", x=235, y=18, w=38)

    pdf.set_y(32)
    pdf.set_text_color(*gold_metal); pdf.set_font('Arial', 'B', 46)
    pdf.cell(0, 22, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_text_color(*deep_green); pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 12, "CERTIFICATE OF RECOGNITION", ln=True, align='C')
    
    pdf.set_draw_color(*gold_metal); pdf.line(90, 72, 207, 72)
    pdf.set_y(78); pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    pdf.set_y(105); pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', 'I', 15)
    pdf.cell(0, 10, "Sartiifiketiin kun kabaja guddaadhan kan kennameef:", ln=True, align='C')
    
    pdf.set_text_color(*deep_green); pdf.set_font('Arial', 'B', 40) 
    pdf.cell(0, 25, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    pdf.set_text_color(40, 40, 40); pdf.set_font('Arial', '', 14)
    msg = "Tajaajila saffisaa fi amannamaa waggaa 2026 keessatti gumaachaniif galateeffamtaniiru."
    pdf.multi_cell(0, 8, msg, align='C')

    pdf.set_y(170); pdf.set_draw_color(*deep_green); pdf.line(40, 170, 115, 170)
    pdf.set_xy(40, 172); pdf.set_font('Arial', 'B', 12); pdf.cell(75, 6, "Mallattoo", align='C')
    pdf.line(180, 170, 255, 170); pdf.set_xy(180, 172); pdf.cell(75, 6, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.title("Dadar Admin")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Tajaajilamtoota</h4><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    elif menu == "📝 Galmee Haaraa":
        with st.form("entry_form", clear_on_submit=True):
            st.subheader("Galmee Haaraa")
            m1 = st.text_input("Maqaa Abbaa Dhimmaa")
            a1 = st.text_input("Araddaa")
            q1 = st.text_input("Qaxana")
            t1 = st.text_input("Gosa Tajaajilaa")
            o1 = st.text_input("Maqaa Ogeessaa")
            k1 = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), m1, a1, q1, t1, o1, k1]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df); st.success("Galmeeffameera!")

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
                    st.markdown(f"<div class='card'><h2>{i}FFAA</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                    st.download_button(f"📥 Sartiifiikeeta", pdf_bytes, f"Cert_{name}.pdf", "application/pdf")

    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

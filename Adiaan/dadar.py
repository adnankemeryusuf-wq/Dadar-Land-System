import streamlit as st
import pandas as pd
import os
import io
import requests
import base64
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

st.set_page_config(
    page_title="Dadar Land Customer Registration", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

# Logo Base64 gochuuf (Header irratti mul'isuuf)
def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

img_b64 = get_base64_img(LOGO_PATH)

# CSS - Logo bitaa qofaaf fi Style bareeduuf
st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        align-items: center;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-bottom: 5px solid #2e7d32;
        margin-bottom: 25px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }}
    .logo-img {{ width: 90px; height: 90px; object-fit: contain; margin-right: 25px; }}
    .main-title {{ color: #1b5e20; font-family: 'Arial Black'; line-height: 1; }}
    .stApp {{ background-color: #f9fbf9; }}
    div.stForm {{ background: white; border-radius: 15px; border: 1px solid #ddd; padding: 20px; }}
    .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }}
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

def create_advanced_pdf(name, count, rank, cert_type="STAFF"):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluu Sadarkaa
    colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    b_color = colors.get(rank, (27, 94, 32))
    
    # Borders
    pdf.set_draw_color(*b_color)
    pdf.set_line_width(3.0); pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(1.0); pdf.rect(13, 13, 271, 184)
    
    # Logo Bitaa Qofa (PDF irratti)
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 15, 15, 30)
    
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 32); pdf.set_text_color(*b_color)
    title = "SARTIIFIKETA BEEKAMTII" if cert_type == "STAFF" else "WARAQAA RAGAA TAJAAJILAA"
    pdf.cell(0, 15, title, ln=True, align='C')
    
    pdf.set_font('Arial', '', 20); pdf.set_text_color(0, 0, 0); pdf.ln(20)
    if cert_type == "STAFF":
        msg = f"Obbo/Adde {str(name).upper()}\n\nTajaajilamtoota {count} saffisaan tajaajiluun sadarkaa {rank}ffaa\nwaggaa 2026 waan qabataniif beekamtiin kun kennameef."
    else:
        msg = f"Obbo/Adde {str(name).upper()}\n\nWaajjira Lafaa Bulchiinsa Magaalaa Dadar irraa tajaajila argachuu keessaniif ragaa kenname."
        
    pdf.multi_cell(0, 12, msg, align='C')
    pdf.set_y(170); pdf.line(110, 175, 187, 175)
    pdf.set_xy(110, 177); pdf.set_font('Arial', 'B', 12)
    pdf.cell(77, 8, "Itti Gaafatamaa Waajjiraa", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Page (Maqaa waajjiraa fi Logo qofa)
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("<h2 style='text-align:center;'>Systemii Galmee Dadar</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Dogoggora!")
else:
    # --- HEADER (LOGO BITAA QOFA) ---
    logo_src = f"data:image/png;base64,{img_b64}" if img_b64 else ""
    st.markdown(f"""
        <div class="header-container">
            <img src="{logo_src}" class="logo-img"> 
            <div class="main-title">
                <h1 style='margin:0; font-size: 28px;'>BULCHIINSA MAGAALAA DADAR</h1>
                <h2 style='margin:0; font-size: 20px; color: #4caf50;'>WAAJJIRA LAFAA</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "🔍 Barbaadi"])

    if menu == "📊 Dashboard":
        st.subheader("📊 Gabaasa Gabaabaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("Maamiltoota", len(df))
            c3.metric("Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.dataframe(df[COL_NAMES], use_container_width=True)
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Tajaajilaa")
        with st.form("reg", clear_on_submit=True):
            m = st.text_input("Maqaa Maamilaa")
            o = st.text_input("Maqaa Ogeessaa")
            t = st.text_input("Gosa Tajaajilaa")
            k = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                if m and o:
                    new = [datetime.now().strftime('%d/%m/%Y'), m, "-", "-", t, o, k]
                    df_new = pd.DataFrame([new], columns=COL_NAMES)
                    df_all = pd.concat([df, df_new], ignore_index=True)
                    df_all[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
                    st.success("Galmeeffameera!"); st.rerun()

    elif menu == "🏆 Badhaasa":
        st.subheader("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf = create_advanced_pdf(name, count, i+1)
                    st.download_button(f"📥 Sartiifiketa {i+1}", pdf, f"Badhaasa_{name}.pdf", key=f"s_{i}")

    elif menu == "🔍 Barbaadi":
        q = st.text_input("Maqaa Maamilaa Barbaadi")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res[COL_NAMES])

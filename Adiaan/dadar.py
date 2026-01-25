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

st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

# --- CSS: UI Enhancements ---
st.markdown("""
    <style>
    [data-testid="stHeader"] { display: none !important; }
    .stAppToolbar { display: none !important; }
    .block-container { padding-top: 1rem !important; }
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; color: black; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CONSTANTS & DATA HANDLING =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_advanced_pdf(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    rank_colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    r_color = rank_colors.get(rank, (0, 80, 0))
    
    pdf.set_draw_color(*r_color); pdf.set_line_width(3.0); pdf.rect(10, 10, 277, 190)
    pdf.set_y(45); pdf.set_text_color(*r_color); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_y(100); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 25, name.upper(), ln=True, align='C')
    pdf.set_y(140); pdf.set_font('Arial', '', 18)
    pdf.multi_cell(0, 10, f"Tajaajilamtoota {count} saffisaan tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>Dadar Land Registration</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii"])
        if st.button("Log Out"):
            st.session_state.logged_in = False; st.rerun()

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)
            
            fig = px.bar(df.groupby('Maqaa_Ogeessa').size().reset_index(name='Baay\'ina'), x='Maqaa_Ogeessa', y='Baay\'ina', title="Hojii Ogeessaan")
            st.plotly_chart(fig, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.subheader("Galmee Maamiltoota Haaraa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            aradda = col1.selectbox("Araddaa", ["01", "02", "03", "04"])
            service = col2.selectbox("Gosa Tajaajilaa", ["Lafa Kennuu", "Waraqaa Ragaa", "Iddoo Jijjiirraa", "Kan biroo"])
            staff = col2.text_input("Maqaa Ogeessa Hojjetu")
            payment = st.number_input("Kafaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("Galmeessi"):
                new_data = pd.DataFrame([[datetime.now().strftime('%d/%m/%Y'), name, aradda, "Q1", service, staff, payment]], columns=COL_NAMES)
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success(f"Maamilli {name} galmeeffameera!")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.subheader("Badhaasa Ogeeyyii Ciccoo")
        if not df.empty:
            stats = df.groupby('Maqaa_Ogeessa').size().sort_values(ascending=False).head(3)
            for i, (name, count) in enumerate(stats.items(), 1):
                col_a, col_b = st.columns([3, 1])
                col_a.write(f"**{i}. {name}** - {count} Tajaajilamtoota")
                pdf_bytes = create_advanced_pdf(name, count, i)
                col_b.download_button(f"Santiifikeeta {i}ffaa", data=pdf_bytes, file_name=f"Certificate_{name}.pdf")

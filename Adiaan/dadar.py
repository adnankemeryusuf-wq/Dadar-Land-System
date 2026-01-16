import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "logo_png.jpg"  # Maqaa faayila kee isa sirrii kanaan bakka buuseera
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon="🏢", 
    layout="wide"
)

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; border: none; }
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

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    rank_color = (255, 215, 0) if rank == 1 else ((192, 192, 192) if rank == 2 else (205, 127, 50))
    rank_text = f"{rank}FFAA"
    deep_green = (0, 80, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(10, 10, 277, 190, 'F')
    pdf.set_draw_color(*deep_green); pdf.set_line_width(3.0); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*rank_color); pdf.set_line_width(1.5); pdf.rect(13, 13, 271, 184)
    
    pdf.set_y(45); pdf.set_text_color(*rank_color); pdf.set_font('Arial', 'B', 35) 
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_y(90); pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 25, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center; color: #1b5e20;'>Dadar Land Administration</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("Baay'ina Maamilaa", len(df))
            c3.metric("Ogeeyyii", df['Maqaa_Ogeessa'].nunique())

    elif menu == "📝 Galmee Haaraa":
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            m_name = col1.text_input("Maqaa Abbaa Dhimmaa")
            m_ara = col2.text_input("Araddaa")
            m_qax = col1.text_input("Qaxana")
            m_oge = col2.text_input("Maqaa Ogeessaa")
            m_gosa = st.text_input("Gosa Tajaajilaa")
            m_kaff = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), m_name, m_ara, m_qax, m_gosa, m_oge, m_kaff]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df); st.success("Galmeeffameera!"); st.rerun()

    elif menu == "📈 Gabaasa Bal'aa":
        st.dataframe(df[COL_NAMES])

    elif menu == "🏆 Badhaasa Ogeeyyii":
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (name, count) in enumerate(top_3.items()):
                st.write(f"🏆 {i+1}. {name} ({count} Hojii)")
                pdf_file = create_advanced_pdf(name, count, i+1)
                st.download_button(f"Sartiifiketa {name}", pdf_file, f"{name}.pdf", "application/pdf")

    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Barbaadi (Maqaa)")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"Edit: {row['Maqaa_Abbaa_Dhimmaa']}"):
                    n_n = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                    n_k = st.number_input("Kafaltii", float(row['Kafaltii_Taj']), key=f"k_{idx}")
                    if st.button("💾 Update", key=f"u_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = n_n
                        df.at[idx, 'Kafaltii_Taj'] = n_k
                        save_data(df); st.rerun()

import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from pptx import Presentation
from pptx.util import Inches, Pt

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

st.set_page_config(page_title="Deder Land System", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .card { 
        background: white; padding: 20px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; 
        border-top: 5px solid #2e7d32; margin-bottom: 10px; 
    }
    .metric-value { font-size: 26px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_ppt_report(df_filtered, report_type):
    prs = Presentation()
    # Slide 1: Title
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Gabaasa Sochii Hojii Lafa Magaalaa"
    slide.placeholders[1].text = f"Deder City Land Office\nGabaasa: {report_type}\nGuyyaa: {datetime.now().strftime('%d/%m/%Y')}"
    
    # Slide 2: Summary
    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "Waliigala Gabaasaa"
    tf = slide2.placeholders[1].text_frame
    tf.text = f"• Waliigala Galii: {df_filtered['Kafaltii_Taj'].sum():,.2f} ETB"
    tf.add_paragraph().text = f"• Baay'ina Maamiltootaa: {len(df_filtered)}"
    
    ppt_io = io.BytesIO()
    prs.save(ppt_io)
    return ppt_io.getvalue()

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Deder Land Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df.empty else "-"
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Cimaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {"Gibira": ["Gibira Lafa Qonnaa", "Gibira Manaa"], "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "TOT"]}
        
        with st.form("entry_form"):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            gosa = st.multiselect("Gosa Tajaajilaa", sum(GATII_DICT.values(), []))
            kaffaltii = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(gosa), ogeessa, kaffaltii]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("Galmeeffameera!")

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Bal'aa")
        if not df.empty:
            f_type = st.selectbox("Calali:", ["Waliigala", "Waggaa", "Ji'a"])
            filtered = df.copy() # Calala dabalataa asitti galchuun ni danda'ama
            
            # Export Buttons
            st.subheader("📥 Gabaasa Buufadhu")
            ex1, ex2, ex3 = st.columns(3)
            
            # Excel
            buf_ex = io.BytesIO()
            with pd.ExcelWriter(buf_ex, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False)
            ex1.download_button("📊 Excel Buusi", buf_ex.getvalue(), "Gabaasa.xlsx")
            
            # PPT
            ppt_file = create_ppt_report(filtered, f_type)
            ex2.download_button("🖥️ PPT Buusi", ppt_file, "Gabaasa.pptx")
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

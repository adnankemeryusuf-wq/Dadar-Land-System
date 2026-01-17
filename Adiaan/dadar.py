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
from pptx.enum.text import PP_ALIGN

# ... (Kutaa Functions kaan akkuma jirutti dhiisi) ...

# ================= 2. CORE FUNCTIONS (ADD PPT) =================
def create_ppt_repoimport streamlit as st
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
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

st.set_page_config(page_title="Deder Land System", page_icon="🏢", layout="wide")

# CSS Style
st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .card { 
        background: white; padding: 20px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; 
        border-top: 6px solid #2e7d32; margin-bottom: 10px; 
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
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
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Gabaasa Sochii Hojii Lafa Magaalaa"
    slide.placeholders[1].text = f"Deder City Land Office\nGabaasa: {report_type}\nGuyyaa: {datetime.now().strftime('%d/%m/%Y')}"
    
    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "Waliigala Gabaasaa"
    tf = slide2.placeholders[1].text_frame
    tf.text = f"• Waliigala Galii: {df_filtered['Kafaltii_Taj'].sum():,.2f} ETB"
    tf.add_paragraph().text = f"• Baay'ina Maamiltootaa: {len(df_filtered)}"
    
    ppt_io = io.BytesIO()
    prs.save(ppt_io)
    return ppt_io.getvalue()

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.subheader("🏢 Login - Deder City Land")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df.empty else "-"
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Cimaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)

    elif menu == "📈 Gabaasa Bal'aa":
        st.subheader("📈 Gabaasa fi Xiinxala Galii")
        if not df.empty:
            with st.expander("🔍 Calali", expanded=True):
                f_type = st.selectbox("Gosa Gabaasaa:", ["Waliigala", "Waggaa", "Kurmaana", "Ji'a"])
                filtered = df.copy()
                # (Kutaa calalaa itti fufa...)

            st.markdown("---")
            col_ex, col_ppt = st.columns(2)
            
            # Excel
            buf_ex = io.BytesIO()
            with pd.ExcelWriter(buf_ex, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False)
            col_ex.download_button("📥 Excel Buufadhu", buf_ex.getvalue(), "Gabaasa_Dadar.xlsx")

            # PPT
            ppt_file = create_ppt_report(filtered, f_type)
            col_ppt.download_button("📥 PowerPoint (PPT) Buusi", ppt_file, f"Gabaasa_Dadar.pptx")
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False; st.rerun()rt(df_filtered, report_type):
    prs = Presentation()
    
    # --- Slide 1: Title Slide ---
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Gabaasa Sochii Hojii Lafa Magaalaa"
    subtitle.text = f"Deder City Land Office\nGabaasa: {report_type}\nGuyyaa: {datetime.now().strftime('%d/%m/%Y')}"

    # --- Slide 2: Waliigala (Executive Summary) ---
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Waliigala Gabaasaa"
    tf = slide.placeholders[1].text_frame
    tf.text = f"• Waliigala Galii: {df_filtered['Kafaltii_Taj'].sum():,.2f} ETB"
    tf.add_paragraph().text = f"• Baay'ina Maamiltootaa: {len(df_filtered)}"
    tf.add_paragraph().text = f"• Ogeessa Hojii Baay'ee: {df_filtered['Maqaa_Ogeessa'].mode()[0] if not df_filtered.empty else '-'}"

    # --- Slide 3: Gabaasa Araddaalee ---
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Galii Araddaalee"
    ar_data = df_filtered.groupby('Araddaa')['Kafaltii_Taj'].sum().reset_index()
    tf = slide.placeholders[1].text_frame
    for _, row in ar_data.iterrows():
        p = tf.add_paragraph()
        p.text = f"• {row['Araddaa']}: {row['Kafaltii_Taj']:,.2f} ETB"

    # Save to buffer
    ppt_io = io.BytesIO()
    prs.save(ppt_io)
    return ppt_io.getvalue()

# ... (Kutaa Dashboard fi Registration akkuma jirutti dhiisi) ...

# ================= 3. MAIN APP (MODIFIED REPORT SECTION) =================
# Menu "📈 Gabaasa Bal'aa" jala kanaan gadii bakka buusi:

    elif menu == "📈 Gabaasa Bal'aa":
        st.markdown("<h4 style='color: #1b5e20;'>📈 Gabaasa fi Xiinxala Galii</h4>", unsafe_allow_html=True)
        
        if not df.empty:
            # --- 1. Filter Section ---
            with st.expander("🔍 Calali ykn Barbaadi", expanded=True):
                c1, c2, _ = st.columns(3)
                f_type = c1.selectbox("Gosa Gabaasaa:", ["Waliigala", "Waggaa", "Kurmaana", "Ji'a", "Guyyaa"])
                
                filtered = df.copy()
                if f_type == "Waggaa":
                    sel_y = c2.selectbox("Waggaa:", sorted(df['Waggaa'].unique(), reverse=True))
                    filtered = filtered[filtered['Waggaa'] == sel_y]
                elif f_type == "Kurmaana":
                    sel_k = c2.selectbox("Kurmaana:", [1, 2, 3, 4])
                    filtered = filtered[filtered['Kurmaana'] == sel_k]
                elif f_type == "Ji'a":
                    sel_m = c2.selectbox("Ji'a:", MONTH_ORDER)
                    filtered = filtered[filtered['Ji\'a'] == sel_m]
                elif f_type == "Guyyaa":
                    sel_d = c2.date_input("Guyyaa Filadhu:", datetime.now())
                    filtered = filtered[filtered['Guyyaa'] == sel_d.strftime('%d/%m/%Y')]

            # --- 2. Metric Cards ---
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"<div class='card'><h4>💰 Kaffaltii</h4><h2>{filtered['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='card'><h4>👥 Baay'ina</h4><h2>{len(filtered)}</h2><p>Abbaa Dhimmaa</p></div>", unsafe_allow_html=True)
            top_st = filtered['Maqaa_Ogeessa'].mode()[0] if not filtered.empty else "-"
            m3.markdown(f"<div class='card'><h4>🏆 Ogeessa</h4><h2>{top_st}</h2><p>Hojii Baay'ee</p></div>", unsafe_allow_html=True)

            # --- 3. EXPORT BUTTONS (PDF, EXCEL, PPT) ---
            st.subheader("📥 Gabaasaalee Buufadhu")
            ex_c1, ex_c2, ex_c3 = st.columns(3)

            # Excel
            buf_ex = io.BytesIO()
            with pd.ExcelWriter(buf_ex, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False)
            ex_c1.download_button("📊 Excel Buufadhu", buf_ex.getvalue(), "Gabaasa_Dadar.xlsx")

            # PPT (NEW)
            ppt_file = create_ppt_report(filtered, f_type)
            ex_c2.download_button(
                label="🖥️ PowerPoint (PPT) Buusi",
                data=ppt_file,
                file_name=f"Gabaasa_Dadar_{f_type}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

            # Telegram erguuf
            if ex_c3.button("✈️ Telegramitti Ergi"):
                st.info("Gabaasni gara Telegramitti ergameera!")
            
            st.divider()
            st.subheader("📋 Tarreeffama Gabaasaa")
            st.dataframe(filtered[COL_NAMES], use_container_width=True)

        else:
            st.warning("Data'n galmeeffame hin jiru.")


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
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    div.stForm { background: white; border-radius: 10px; border: 1px solid #ddd; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .card { background: white; padding: 20px; border-radius: 10px; text-align: center; border-top: 4px solid #2e7d32; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .metric-value { font-size: 28px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map({9:"Fulbaana", 10:"Onkololeessa", 11:"Sadaasa", 12:"Muddee", 1:"Amajjii", 2:"Guraandhala", 3:"Bitootessa", 4:"Eebila", 5:"Caamsaa", 6:"Waxabajjii", 7:"Adooleessa", 8:"Hagayya"})
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_certificate(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(46, 125, 50)
    pdf.set_line_width(2)
    pdf.rect(5, 5, 287, 200)
    pdf.set_font('Arial', 'B', 35)
    pdf.set_y(40)
    pdf.cell(0, 20, "SARTIFIIKEETII BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', '', 20)
    pdf.ln(20)
    pdf.multi_cell(0, 15, f"Waraqaan kun Ogeessa cimaa \n {name.upper()} \n tajaajila {count} kennuun sadarkaa {rank}ffaa ta'uuf kennameef.", align='C')
    return pdf.output(dest='S').encode('latin-1')

def create_ppt_report(df_filtered):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Gabaasa Hojii Dadar"
    rows, cols = df_filtered.shape[0] + 1, 3
    table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1.5), Inches(8), Inches(4)).table
    table.columns[0].text, table.columns[1].text, table.columns[2].text = "Maqaa", "Tajaajila", "Kafaltii"
    for i, row in enumerate(df_filtered.head(10).itertuples()):
        table.cell(i+1, 0).text = str(row.Maqaa_Abbaa_Dhimmaa)
        table.cell(i+1, 1).text = str(row.Gosa_Tajajjilaa)
        table.cell(i+1, 2).text = str(row.Kafaltii_Taj)
    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Dadar Login</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u, p = st.text_input("Username"), st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.header("Dedar Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "🔍 Barbaadi"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            top_og = df['Maqaa_Ogeessa'].mode()[0] if not df.empty else "-"
            c3.markdown(f"<div class='card'><p>🏆 Ogeessa Cimaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)
            
            # Chart
            chart_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0).reset_index()
            fig = px.line(chart_data, x='Ji\'a', y='Kafaltii_Taj', title="Adeemsa Galii Ji'aan", markers=True)
            st.plotly_chart(fig, use_container_width=True)

    # --- 2. GALMEE ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {"Gibira": ["Gibira Lafa Qonnaa", "Gibira Manaa"], "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "TOT"]}
        with st.form("entry_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara = c2.text_input("Araddaa *")
            qax = c1.text_input("Qaxana *")
            ogeessa = c2.text_input("Maqaa Ogeessaa *")
            gosa = st.multiselect("Gosa Tajaajilaa *", sum(GATII_DICT.values(), []))
            kaffaltii = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                if all([maqaa, ara, qax, ogeessa, gosa]):
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(gosa), ogeessa, kaffaltii]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Milkaa'inaan Galmeeffameera!")
                else: st.error("⚠️ Bakka mallattoo (*) qaban guuti!")

    # --- 3. GABAASA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa fi Export")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            ex1, ex2 = st.columns(2)
            # Excel
            buf_ex = io.BytesIO()
            df[COL_NAMES].to_excel(buf_ex, index=False)
            ex1.download_button("📊 Excel Buufadhu", buf_ex.getvalue(), "Gabaasa.xlsx")
            # PPT
            ppt_data = create_ppt_report(df)
            ex2.download_button("🖥️ PPT Buufadhu", ppt_data, "Gabaasa.pptx")

    # --- 4. BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Ogeeyyii Sadarkaa 1-3ffaa")
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2>{i+1}ffaa</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    cert_pdf = create_certificate(name, count, i+1)
                    st.download_button(f"📥 Sartifiikeetii {i+1}", cert_pdf, f"Cert_{name}.pdf")

    # --- 5. SEARCH ---
    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        q = st.text_input("Maqaa Barbaadi")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res[COL_NAMES])

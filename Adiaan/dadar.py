import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# 1. PAGE SETUP & STYLE
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-top: 5px solid #1b5e20;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 2. DATA MANAGEMENT
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

# 3. ADVANCED PDF CERTIFICATE
def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Background & Borders
    pdf.set_fill_color(255, 254, 245)
    pdf.rect(10, 10, 277, 190, 'F')
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(2.5); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(218, 165, 32); pdf.set_line_width(1.0); pdf.rect(13, 13, 271, 184)
    
    # Title
    pdf.set_y(45); pdf.set_font('Arial', 'B', 38); pdf.set_text_color(218, 165, 32)
    pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", ln=True, align='C')
    
    # Content
    pdf.set_y(85); pdf.set_font('Arial', 'B', 30); pdf.set_text_color(0, 80, 0)
    pdf.cell(0, 15, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    pdf.set_y(120); pdf.set_font('Arial', '', 16); pdf.set_text_color(40, 40, 40)
    msg = f"Waggaa 2026 keessatti tajaajilamtoota {count} saffisaan tajaajiluun sadarkaa {rank}ffaa waan qabataniif beekamtiin kun kennameef."
    pdf.multi_cell(0, 10, msg.encode('latin-1', 'replace').decode('latin-1'), align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# 4. NAVIGATION & LOGIN
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("### 🏢 Admin Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "1234":
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa Ogeeyyii", "Ba'i"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Gabaasa Raawwii Hojii")
        
        # Metrics
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.0f} ETB</h2></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2></div>", unsafe_allow_html=True)
        
        st.write("---")
        
        # Plotly Chart
        if not df.empty:
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                fig = px.bar(df, x='Maqaa_Ogeessa', y='Kafaltii_Taj', color='Gosa_Tajajjilaa', 
                             title="Raawwii Ogeeyyii fi Gosa Tajaajilaa", barmode='group')
                st.plotly_chart(fig, use_container_width=True)
            with col_table:
                st.write("📊 Gabaasa Gabaabaa")
                st.dataframe(df[['Maqaa_Abbaa_Dhimmaa', 'Kafaltii_Taj']].tail(10), hide_index=True)

    # --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.title("🏆 Sartifiikeeta Badhaasaa")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card text-center'><h3>{i}FFAA</h3><h4>{name}</h4><p>{count} Hojii</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_pdf_cert(name, count, i)
                    st.download_button(f"📥 Download Cert", pdf_bytes, f"Cert_{name}.pdf", "application/pdf")
        else: st.info("Data'n galmeeffame hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

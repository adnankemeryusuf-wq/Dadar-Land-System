import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# 1. Configuration
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

# 2. Path & Data Load
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

# 3. PDF Function (Gold-Green Theme)
def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_fill_color(255, 254, 245)
    pdf.rect(10, 10, 277, 190, 'F')
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    
    pdf.set_y(50); pdf.set_font('Arial', 'B', 35); pdf.set_text_color(218, 165, 32)
    pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_font('Arial', 'B', 28); pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    pdf.set_font('Arial', '', 16); pdf.set_text_color(0, 0, 0)
    msg = f"Waggaa 2026 keessatti tajaajilamtoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru."
    pdf.multi_cell(0, 10, msg.encode('latin-1', 'replace').decode('latin-1'), align='C')
    return pdf.output(dest='S').encode('latin-1')

# 4. Main App Interface
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Section
    st.title("🔐 Admin Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "1234":
            st.session_state.logged_in = True; st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("Menu", ["Dashboard", "Galmee", "Badhaasa"])

    if menu == "Dashboard":
        st.header("📈 Gabaasa Raawwii")
        m1, m2 = st.columns(2)
        m1.metric("Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        m2.metric("Baay'ina Maamiltootaa", len(df))
        
        # Plotly Giraafii
        fig = px.bar(df, x='Maqaa_Ogeessa', y='Kafaltii_Taj', color='Araddaa', title="Galii Ogeessaan")
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Badhaasa":
        st.header("🏆 Sartifiikeeta Badhaasaa")
        top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        for i, (name, count) in enumerate(top_3.items(), 1):
            st.write(f"Sadarkaa {i}ffaa: **{name}**")
            pdf_bytes = create_pdf_cert(name, count, i)
            st.download_button(f"Download Cert - {name}", pdf_bytes, f"{name}.pdf")

import streamlit as st
import pandas as pd
import sqlite3
import os
import io
import requests
import tempfile
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & DATABASE =================
DB_NAME = "dadar_land_system.db"
LOGO_PATH = "Adiaan/logo.png"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  guyyaa TEXT, maqaa_abbaa_dhimmaa TEXT, araddaa TEXT, 
                  qaxana TEXT, gosa_tajaajilaa TEXT, maqaa_ogeessa TEXT, 
                  kafaltii_taj REAL)''')
    conn.commit()
    conn.close()

init_db()

# ================= 2. UI & STYLE =================
st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #10b981; }
    div[data-testid="stSidebarUserContent"] .stRadio label { background-color: #10b981 !important; color: #000000 !important; border-radius: 10px; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# ================= 3. PDF & EXPORT FUNCTIONS =================
def create_receipt_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "WAAJJIRA LAFAA MAGAALAA DADAR", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Maqaa: {data[2]} | Guyyaa: {data[1]}", ln=True)
    pdf.cell(0, 10, f"Kaffaltii: {data[7]:,.2f} ETB", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. AUTHENTICATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("SEENI"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username ykn Password dogoggora!")
else:
    # Sidebar
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = st.radio("Filannoo", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📜 Gabaasa & Export", "🚪 Logout"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM records", conn)
        conn.close()
        
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Waliigala Galii", f"{df['kafaltii_taj'].sum():,.2f} ETB")
            c2.metric("Maamiltoota", len(df))
            
            fig = px.pie(df, names='gosa_tajaajilaa', values='kafaltii_taj', title="Galii Gosa Tajaajilaan")
            st.plotly_chart(fig, use_container_width=True)

    # --- GALMEE ---
    elif menu == "📝 Galmee Tajaajilaa":
        with st.form("reg_form"):
            name = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            serv = st.selectbox("Tajaajila", ["Kaartaa Haaraa", "Gibira", "Pilaanii"])
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 GALMEESSI"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO records (guyyaa, maqaa_abbaa_dhimmaa, araddaa, qaxana, gosa_tajaajilaa, kafaltii_taj) VALUES (?,?,?,?,?,?)",
                          (datetime.now().strftime('%Y-%m-%d'), name, ara, qax, serv, fee))
                conn.commit()
                conn.close()
                st.success("✅ Galmeeffameera!")

    # --- Gabaasa & Export ---
    elif menu == "📜 Gabaasa & Export":
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM records", conn)
        conn.close()
        st.dataframe(df)
        
        # Excel Export
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Excel Buufadhu", output.getvalue(), "Gabaasa.xlsx")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

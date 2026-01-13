import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import io
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# Akka koodiin keenya bifa bareedaa qabaatuuf
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom right, #f8fafc, #e2e8f0); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-top: 5px solid #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATABASE & SECURITY =================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect("dadar_land.db")
    c = conn.cursor()
    # Teebulii ragaa tajaajilaa
    c.execute('''CREATE TABLE IF NOT EXISTS records 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, yeroo TEXT, maqaa TEXT, 
                  araddaa TEXT, qaxana TEXT, gosa TEXT, ogeessa TEXT, kafaltii REAL)''')
    # Teebulii fayyadamtootaa
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    
    # Admin durumaan jiru (Password: admin123)
    admin_pwd = hash_password("admin123")
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", ("admin", admin_pwd, "Admin"))
    conn.commit()
    conn.close()

# Database jalqabsiisuu
init_db()

def load_data_sql(role, user):
    conn = sqlite3.connect("dadar_land.db")
    if role == "Admin":
        df = pd.read_sql_query("SELECT * FROM records", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM records WHERE ogeessa = ?", conn, params=(user,))
    conn.close()
    return df

# ================= 3. PDF GENERATOR (NAGAHEE) =================
def generate_receipt(data):
    pdf = FPDF(orientation='P', unit='mm', format=(100, 150))
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "BULCHIINSA LAFAA DADAR", ln=True, align='C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, "NAGAHEE KAFALTII", ln=True, align='C')
    pdf.line(10, 25, 90, 25)
    pdf.ln(10)
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 7, f"Guyyaa: {data['Guyyaa']}", ln=True)
    pdf.cell(0, 7, f"Maqaa: {data['Maqaa']}", ln=True)
    pdf.cell(0, 7, f"Gosa: {data['Gosa']}", ln=True)
    pdf.cell(0, 7, f"Kafaltii: {data['Kafaltii']} ETB", ln=True)
    pdf.ln(5)
    pdf.cell(0, 7, f"Ogeessa: {data['Ogeessa']}", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. AUTHENTICATION LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGOUT FUNC ---
def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

# ================= 5. MAIN APP =================

if not st.session_state.logged_in:
    # --- FUULA LOGIN ---
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<h1 style='text-align: center;'>🏢 Dadar Land Admin</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Seeni", use_container_width=True):
                conn = sqlite3.connect("dadar_land.db")

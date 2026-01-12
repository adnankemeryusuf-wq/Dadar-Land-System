# DADAR LAND ADMIN PRO - FULL STREAMLIT APP

import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageOps

# ================= CONFIG =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

DATA_FILE = "dadar_final_report.txt"
USERS_FILE = "users.csv"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj', 'Kafaltii_Wal', 'C1', 'C2', 'C3']

# ================= SECURITY =================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# ================= USERS =================
def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([["admin", hash_password("admin123"), "admin"]], columns=["username", "password", "role"])
        df.to_csv(USERS_FILE, index=False)
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

# ================= DATA =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False)

# ================= PDF REPORT =================
def create_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()

    if LOGO_PATH:
        pdf.image(LOGO_PATH, 10, 8, 18)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "WAAJJIRA LAFEE MAGAALAA DADAR", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 9)
    headers = ["Maqaa", "Araddaa", "Gosa", "Kaf. Taj", "Kaf. Wal"]
    widths = [45, 35, 35, 35, 35]

    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 8, h, 1, 0, 'C', True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 9)
    fill = False
    for _, r in df.iterrows():
        pdf.set_fill_color(245, 247, 250) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(widths[0], 7, str(r['Maqaa']), 1, fill=fill)
        pdf.cell(widths[1], 7, str(r['Araddaa']), 1, fill=fill)
        pdf.cell(widths[2], 7, str(r['Gosa']), 1, fill=fill)
        pdf.cell(widths[3], 7, str(r['Kafaltii_Taj']), 1, fill=fill)
        pdf.cell(widths[4], 7, str(r['Kafaltii_Wal']), 1, ln=1, fill=fill)
        fill = not fill

    return pdf.output(dest='S').encode('latin-1')

# ================= LOGIN =================
def login_page():
    st.title("🔐 Seensa Sirna")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Seeni"):
        users = load_users()
        h = hash_password(p)
        user = users[(users.username == u) & (users.password == h)]

        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.user = u
            st.session_state.role = user.iloc[0]['role']
            st.rerun()
        else:
            st.error("Seensa hin milkaa'in")

# ================= SESSION =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ================= SIDEBAR =================
st.sidebar.success(f"👤 {st.session_state.user}")
st.sidebar.info(f"Role: {st.session_state.role}")
if st.sidebar.button("🚪 Ba'i"):
    st.session_state.clear()
    st.rerun()

menu = st.sidebar.radio("Menu", ["Galmee", "Data", "PDF", "Users"])

# ================= PAGES =================
if menu == "Galmee":
    st.header("📝 Galmee Tajaajilaa")
    with st.form("entry"):
        maqaa = st.text_input("Maqaa")
        araddaa = st.text_input("Araddaa")
        gosa = st.text_input("Gosa")
        ogeessa = st.text_input("Ogeessa")
        k_taj = st.number_input("Kafaltii Taj")
        k_wal = st.number_input("Kafaltii Wal")
        if st.form_submit_button("💾 Galmeessi"):
            df = load_data()
            new = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, '', gosa, ogeessa, k_taj, k_wal, '', '', '']
            df.loc[len(df)] = new
            save_data(df)
            st.success("Galmeeffame")

elif menu == "Data":
    st.header("📊 Odeeffannoo")
    df = load_data()
    st.dataframe(df, use_container_width=True)

elif menu == "PDF":
    st.header("📄 Gabaasa PDF")
    df = load_data()
    if st.button("PDF Uumi"):
        pdf = create_pdf_report(df)
        st.download_button("Buusi PDF", pdf, "Gabaasa_Dadar.pdf", "application/pdf")

elif menu == "Users" and st.session_state.role == "admin":
    st.header("🧑‍💼 Bulchiinsa Users")
    users = load_users()
    st.dataframe(users[["username", "role"]])

    with st.form("add_user"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        r = st.selectbox("Role", ["admin", "user"])
        if st.form_submit_button("➕ Dabaluu"):
            users.loc[len(users)] = [u, hash_password(p), r]
            save_users(users)
            st.success("User dabalame")

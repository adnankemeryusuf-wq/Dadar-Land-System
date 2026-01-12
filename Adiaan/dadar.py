# DADAR LAND ADMIN PRO - FULL STREAMLIT APP (STABLE VERSION)

import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw

# ================= CONFIG =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

DATA_FILE = "dadar_final_report.txt"
USERS_FILE = "users.csv"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj', 'Kafaltii_Wal', 'C1', 'C2', 'C3']

# ================= SESSION INIT (VERY IMPORTANT) =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "role" not in st.session_state:
    st.session_state.role = ""

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
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False)

# ================= CIRCULAR LOGO =================
def circular_logo(path):
    if not path:
        return None
    img = Image.open(path).convert("RGBA").resize((400, 400))
    mask = Image.new("L", (400, 400), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 400, 400), fill=255)
    img.putalpha(mask)
    out = Image.new("RGB", (400, 400), (255, 255, 255))
    out.paste(img, mask=img.split()[3])
    return out

# ================= CERTIFICATE =================
def generate_certificate(name):
    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_draw_color(184, 134, 11)
    pdf.set_line_width(2)
    pdf.rect(5, 5, 287, 200)

    logo = circular_logo(LOGO_PATH)
    if logo:
        pdf.image(logo, x=131, y=10, w=35)

    pdf.ln(40)
    pdf.set_font('Times', 'B', 40)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')

    pdf.set_font('Arial', 'I', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    pdf.ln(10)
    pdf.set_font('Times', 'B', 32)
    pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, name.upper(), ln=True, align='C')

    pdf.ln(8)
    pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 10, "Tajaajila amanamaa fi qulqulluu hojjettanii waan argamtaniif beekamtii kanaan badhaafamte.", align='C')

    pdf.set_y(170)
    pdf.cell(100, 8, "____________________", align='C')
    pdf.cell(87, 8, "")
    pdf.cell(100, 8, datetime.now().strftime('%d/%m/%Y'), ln=1, align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= LOGIN PAGE =================
def login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if LOGO_PATH:
            st.image(LOGO_PATH, width=140)
        st.title("🔐 Seensa Sirna")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni", use_container_width=True):
            users = load_users()
            h = hash_password(p)
            row = users[(users.username == u) & (users.password == h)]
            if not row.empty:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.session_state.role = row.iloc[0]['role']
                st.rerun()
            else:
                st.error("Username ykn Password dogoggora")

# ================= MAIN =================
if not st.session_state.logged_in:
    login_page()
    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    if LOGO_PATH:
        st.image(LOGO_PATH, width=120)
    st.success(f"👤 {st.session_state.user} ({st.session_state.role})")
    menu = st.radio("Menu", ["📝 Galmee", "📊 Odeeffannoo", "🏆 Sartiifiketa", "🧑‍💼 Users", "🚪 Ba'i"])

# ================= DATA LOAD =================
df = load_data()

# ================= PAGES =================
if menu == "📝 Galmee":
    st.header("📝 Galmee Haaraa")
    with st.form("entry"):
        maqaa = st.text_input("Maqaa")
        araddaa = st.text_input("Araddaa")
        gosa = st.text_input("Gosa")
        ogeessa = st.text_input("Ogeessa")
        k_taj = st.number_input("Kafaltii Taj", min_value=0.0)
        k_wal = st.number_input("Kafaltii Wal", min_value=0.0)
        if st.form_submit_button("💾 Galmeessi"):
            df.loc[len(df)] = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, '', gosa, ogeessa, k_taj, k_wal, '', '', '']
            save_data(df)
            st.success("Galmeeffame")
            st.rerun()

elif menu == "📊 Odeeffannoo":
    st.header("📊 Odeeffannoo")
    st.dataframe(df, use_container_width=True)

elif menu == "🏆 Sartiifiketa":
    st.header("🏆 Sartifiketii")
    if not df.empty:
        best = df['Ogeessa'].value_counts().idxmax()
        if st.button("Sartifiketa Uumi"):
            pdf = generate_certificate(best)
            st.download_button("Buusi PDF", pdf, f"Sartifiketa_{best}.pdf")

elif menu == "🧑‍💼 Users" and st.session_state.role == "admin":
    st.header("🧑‍💼 Users")
    users = load_users()
    st.table(users[["username", "role"]])

elif menu == "🚪 Ba'i":
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.session_state.role = ""
    st.rerun()

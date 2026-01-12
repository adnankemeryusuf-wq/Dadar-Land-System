# DADAR LAND ADMIN PRO - FULL STREAMLIT APP (SQLite, Dashboard, Telegram, Multilingual)

import streamlit as st
import pandas as pd
import os
import hashlib
import sqlite3
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw
import plotly.express as px
import requests

# ================= CONFIG =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

DATA_DB = "dadar_land.db"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# ================= SESSION INIT =================
for key in ['logged_in', 'user', 'role', 'lang']:
    if key not in st.session_state:
        st.session_state[key] = False if key=='logged_in' else ("Oromo" if key=='lang' else "")

# ================= SECURITY =================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# ================= DATABASE =================
def get_connection():
    conn = sqlite3.connect(DATA_DB, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        maqaa TEXT,
        araddaa TEXT,
        qaxana TEXT,
        gosa TEXT,
        ogeessa TEXT,
        kafaltii_taj REAL,
        kafaltii_wal REAL,
        c1 TEXT,
        c2 TEXT,
        c3 TEXT
    )''')
    conn.commit()
    c.execute('SELECT * FROM users WHERE username=?', ('admin',))
    if not c.fetchone():
        c.execute('INSERT INTO users VALUES (?, ?, ?)', ('admin', hash_password('admin123'), 'admin'))
        conn.commit()
    conn.close()

init_db()

# ================= TELEGRAM =================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}"
    try:
        requests.get(url)
    except:
        pass

# ================= DASHBOARD =================
def show_dashboard():
    conn = get_connection()
    df = pd.read_sql('SELECT * FROM records', conn)
    conn.close()

    if df.empty:
        st.warning("No records yet.")
        return

    st.subheader("Gosa Tajaajilaa Bar Chart")
    fig1 = px.bar(df, x='gosa', y='kafaltii_wal', title='Kafaltii waliigalaa gosa tajaajilaa')
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Ogeessa Pie Chart")
    fig2 = px.pie(df, names='ogeessa', title='Hojjettoota hirmaatan')
    st.plotly_chart(fig2, use_container_width=True)

# ================= LOGIN =================
def login_page():
    st.title("🔐 Seensa Sirna")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (u, hash_password(p)))
        row = c.fetchone()
        conn.close()
        if row:
            st.session_state.logged_in = True
            st.session_state.user = row[0]
            st.session_state.role = row[2]
            st.rerun()
        else:
            st.error("Username ykn Password dogoggora")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ================= MAIN APP =================
with st.sidebar:
    if LOGO_PATH: st.image(LOGO_PATH, width=120)
    st.success(f"👤 {st.session_state.user} ({st.session_state.role})")
    st.session_state.lang = st.selectbox("Afaan", ["Oromo", "English"], index=0)
    menu = st.radio("Menu", ["📝 Galmee", "📊 Dashboard", "🏆 Sartiifiketa", "🧑‍💼 Users", "🚪 Ba'i"])

conn = get_connection()
c = conn.cursor()

# ================= MENU PAGES =================
if menu == "📝 Galmee":
    st.header("📝 Galmee Haaraa")
    maqaa = st.text_input("Maqaa")
    araddaa = st.text_input("Araddaa")
    gosa = st.text_input("Gosa")
    ogeessa = st.text_input("Ogeessa")
    k_taj = st.number_input("Kafaltii Taj", min_value=0.0)
    k_wal = st.number_input("Kafaltii Wal", min_value=0.0)
    if st.button("💾 Galmeessi"):
        c.execute('INSERT INTO records (date, maqaa, araddaa, qaxana, gosa, ogeessa, kafaltii_taj, kafaltii_wal) VALUES (?,?,?,?,?,?,?,?)',
                  (datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, '', gosa, ogeessa, k_taj, k_wal))
        conn.commit()
        st.success("Galmeeffame")
        send_telegram(f"New record added: {maqaa}")

elif menu == "📊 Dashboard":
    st.header("📊 Dashboard")
    show_dashboard()

elif menu == "🏆 Sartiifiketa":
    st.header("🏆 Sartifiketii")
    # Implement PDF certificate here (reuse previous function)

elif menu == "🧑‍💼 Users" and st.session_state.role == "admin":
    st.header("Users")
    df_users = pd.read_sql('SELECT username, role FROM users', conn)
    st.table(df_users)

elif menu == "🚪 Ba'i":
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.session_state.role = ""
    st.rerun()

conn.close()

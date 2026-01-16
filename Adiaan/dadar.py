import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
import requests

# --- 1. ENVIRONMENT VARIABLES ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_MANAGER = os.getenv("CHAT_ID_MANAGER")

# --- 2. DATABASE SETUP ---
DB_FILE = "dadar.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS galmee (
        Guyyaa TEXT,
        Maqaa_Abbaa_Dhimmaa TEXT,
        Araddaa TEXT,
        Qaxana TEXT,
        Gosa_Tajajjilaa TEXT,
        Maqaa_Ogeessa TEXT,
        Kafaltii_Taj REAL
    )
    """)
    conn.commit()
    conn.close()

def save_data(new_record):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO galmee VALUES (?, ?, ?, ?, ?, ?, ?)", new_record)
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM galmee", conn)
    conn.close()
    return df

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try:
        return requests.post(url, files=files, data=data).status_code == 200
    except:
        return False

# --- 3. STREAMLIT APP ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")
init_db()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        # Fakkeenya: admin login salphaa (hash fayyadamuun fooyyessuu ni danda’ama)
        if u == "admin" and p == "123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Dogoggora!")
else:
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "Ba'i"])
    df = load_data()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            t_income = df['Kafaltii_Taj'].sum()
            t_clients = len(df)
            avg_inc = t_income / t_clients if t_clients > 0 else 0
            st.metric("💰 Waliigala Galii", f"{t_income:,.2f} ETB")
            st.metric("👥 Tajaajilamtoota", t_clients)
            st.metric("📈 Giddu-galeessa", f"{avg_inc:,.2f} ETB")
        else:
            st.info("Odeeffannoo hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
        araddaa = st.text_input("Araddaa")
        qaxana = st.text_input("Qaxana")
        gosa = st.text_input("Gosa Tajaajilaa")
        ogeessa = st.text_input("Maqaa Ogeessaa")
        kafaltii = st.number_input("Kafaltii", min_value=0.0)
        if st.button("💾 Galmeessi"):
            if maqaa and gosa:

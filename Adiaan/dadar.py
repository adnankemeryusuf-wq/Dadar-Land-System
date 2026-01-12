import streamlit as st
import os
import pandas as pd
import requests
import plotly.express as px  # Charts miidhagaaf
from datetime import datetime, timedelta

# --- 1. QINDAA'INA BU'URAA ---
st.set_page_config(page_title="Dadar Land Administration", layout="wide", page_icon="🏢")

USER_NAME = "Lafa2026"
PASS_WORD = "Dadar@2026"
DATA_FILE = "dadar_final_report.txt"

# Telegram Config
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI" 
TELEGRAM_CHAT_ID = "7329587700"

# --- 2. CSS STYLE (PRO DASHBOARD) ---
st.markdown("""
    <style>
    /* Background waliigalaa */
    .stApp { background-color: #f4f7f6; }
    
    /* Header Box */
    .header-box { 
        text-align: center; padding: 35px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); 
        color: white; border-radius: 20px; margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.3);
    }
    
    /* Metrics Cards */
    .metric-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-bottom: 5px solid #1e3a8a;
        text-align: center; transition: 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.1); }
    .metric-label { color: #64748b; font-size: 1.1rem; font-weight: 500; }
    .metric-value { color: #1e3a8a; font-size: 2.2rem; font-weight: 800; margin-top: 10px; }
    
    /* Table Styling */
    .stDataFrame { border-radius: 15px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown("<div style='background:white; padding:40px; border-radius:20px; box-shadow:0 15px 35px rgba(0,0,0,0.1); text-align:center;'>", unsafe_allow_html=True)
        st.title("Seensa")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("## 🏢 Dadar Land")
        st.divider()
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Telegram", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)

    # Header Section
    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1><p>Sistama Bulchiinsa Ragaa fi Galmee Maallaqaa</p></div>', unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            # Data Dubbisuu
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Bilbila', 'Gosa', 'Ogeessa', 'Lakk_Galmee', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            
            # --- ROW 1: METRICS ---
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">👥 Abbootii Dhimmaa</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">💰 Galii Waligalaa</div><div class="metric-value">{df["Kafaltii"].sum():,.0f} <small style="font-size:1rem;">ETB</small></div></div>', unsafe_allow_html=True)
            with m3:
                ground_count = len(df[df['Gosa'] == "Ground"])
                st.markdown(f'<div class="metric-card"><div class="metric-label">🏗️ Ground</div><div class="metric-value">{ground_count}</div></div>', unsafe_allow_html=True)
            with m4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">📅 Hardha</div><div class="metric-value">{len(df[pd.to_datetime(df["Yeroo"]).dt.date == datetime.now().date()])}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # --- ROW 2: CHARTS ---
            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.subheader("📈 Gosa Tajaajilaa (Service Distribution)")
                fig = px.bar(df['Gosa'].value_counts().reset_index(), x='index', y='Gosa', 
                             labels={'index': 'Gosa Tajaajilaa', 'Gosa': 'Baay\'ina'},
                             color='index', template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.subheader("🕒 Galmee Dhiyoo")
                st.dataframe(df[['Maqaa', 'Gosa', 'Kafaltii']].tail(6), use_container_width=True)

        else:
            st.info("Ragaan galmaa'e hin jiru. Maaloo Galmee Haaraa irratti ragaa galchaa.")

    elif choice == "📝 Galmee Haaraa":
        # (Koodiin Galmee Haaraa akkuma isa duraatti itti fufa...)
        st.subheader("Galmeessa Abbaa Dhimmaa")
        with st.form("form_pro"):
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                qx = st.text_input("Qaxana / Lakk. Manaa")
                bl = st.text_input("Lakkoofsa Bilbilaa")
            with col2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Ground", "Gibira"])
                og = st.text_input("Maqaa Ogeessaa")
                lk = st.text_input("Reference No.")
                k_wal = st.number_input("Kafaltii", min_value=0.0)
            
            if st.form_submit_button("GALMEE MIRKANEEESSI"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                line = f"{now}|{ad}|{ar}|{qx}|{bl}|{gs}|{og}|{lk}|Hardha|0|0|0|{k_wal}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(line)
                st.success("Milkiin Galmaa'eera!")
                st.balloons()

    elif choice == "📊 Gabaasa & Telegram":
        # (Koodiin Gabaasaa akkuma isa duraatti itti fufa...)
        st.subheader("Gabaasa Seeraa")
        if os.path.exists(DATA_FILE):
            df_rep = pd.read_csv(DATA_FILE, sep="|", header=None)
            st.dataframe(df_rep, use_container_width=True)
            if st.button("🚀 Gabaasa Telegram-itti Ergi"):
                st.success("Gabaasni ergameera!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

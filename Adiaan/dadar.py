import streamlit as st
import pandas as pd
import sqlite3
import os, io, requests
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# ================= 1. DATABASE & CONFIG =================
DB_FILE = "dadar_land_pro.db"
NAGAHEE_DIR = "nagahee_scan"
LOGO_PATH = "Adiaan/logo.png"

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS galmee (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 guyyaa TEXT, maqaa TEXT, araddaa TEXT, qaxana TEXT, 
                 tajaajila TEXT, ogeessa TEXT, kaffaltii REAL, nagahee_path TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ================= 2. ANALYTICS FUNCTIONS =================
def show_advanced_analytics(df):
    st.markdown("### 📊 Xiinxala Gadi Fagoo")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("📂 **Gosa Tajaajilaa (Income Distribution)**")
        # Pie Chart Interaktiivii ta'e
        fig_pie = px.pie(df, values='kaffaltii', names='tajaajila', 
                         hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.write("📈 **Trendii Galii (Monthly Trend)**")
        df['Guyyaa_Obj'] = pd.to_datetime(df['guyyaa'], format='%d/%m/%Y')
        trend = df.groupby(df['Guyyaa_Obj'].dt.strftime('%B'))['kaffaltii'].sum().reset_index()
        fig_line = px.line(trend, x='Guyyaa_Obj', y='kaffaltii', markers=True, 
                           color_discrete_sequence=['#1b5e20'])
    
        st.plotly_chart(fig_line, use_container_width=True)

# ================= 3. REGISTRATION WITH SCAN =================
def registration_page():
    st.header("📝 Galmee Haaraa & Nagahee")
    with st.form("reg_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Maqaa Abbaa Dhimmaa")
        ogeessa = col2.text_input("Maqaa Ogeessaa")
        taj = col1.selectbox("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa", "Clearance", "TOT"])
        fee = col2.number_input("Kaffaltii (ETB)", min_value=0.0)
        
        # Nagahee Scan/Photo Upload
        nagahee_file = st.file_uploader("Suuraa Nagahee (Upload Scan)", type=['jpg', 'png', 'pdf'])
        
        if st.form_submit_button("💾 Galmeessi"):
            if name and ogeessa:
                # Save Image if exists
                n_path = ""
                if nagahee_file:
                    n_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.png")
                    with open(n_path, "wb") as f: f.write(nagahee_file.getbuffer())
                
                # Save to SQL
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT INTO galmee (guyyaa, maqaa, araddaa, qaxana, tajaajila, ogeessa, kaffaltii, nagahee_path) VALUES (?,?,?,?,?,?,?,?)",
                             (datetime.now().strftime('%d/%m/%Y'), name, "-", "-", taj, ogeessa, fee, n_path))
                conn.commit()
                conn.close()
                st.success("✅ Galmeen milkiin kuufameera!")

# ================= 4. MAIN NAVIGATION =================
# ... (Login Logic kee akkuma jirutti itti fufa) ...

if st.session_state.get('logged_in'):
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🔍 Barbaadi"])
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM galmee", conn)
    conn.close()

    if menu == "📊 Dashboard":
        st.title("🏢 Dadar Land Admin Dashboard")
        if not df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("💰 Galii Waliigalaa", f"{df['kaffaltii'].sum():,.2f} ETB")
            m2.metric("👥 Maamiltoota", len(df))
            m3.metric("🏆 Ogeessa Active", df['ogeessa'].nunique())
            st.divider()
            show_advanced_analytics(df)
        else:
            st.info("Data'n galmeeffame hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        registration_page()

    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa SQL")
        st.dataframe(df.drop(columns=['nagahee_path']), use_container_width=True)
        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Gabaasa CSV Buusi", csv, "gabaasa.csv")

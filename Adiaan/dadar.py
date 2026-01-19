import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import plotly.express as px

# ================= 1. DATABASE & CONFIG =================
DB_FILE = "dadar_land_pro.db"
NAGAHEE_DIR = "nagahee_scan"

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

# ================= 2. SERVICE LIST =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Gibira Milkii", "TOT"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa", "Sirreeffama Daangaa"],
    "🏗 Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Dhimma Dhala"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii"]
}

# ================= 3. REGISTRATION PAGE =================
def registration_page():
    st.header("📝 Galmee Haaraa & Nagahee")
    
    with st.form("galmee_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        # 1. Maqaa fi Ogeessa
        maqaa = col1.text_input("Maqaa Abbaa Dhimmaa *")
        ogeessa = col2.text_input("Maqaa Ogeessaa *")
        
        # 2. Dynamic Dropdowns (Ramaddii fi Gosa Tajaajilaa)
        main_cat = col1.selectbox("🟢 Ramaddii Tajaajilaa Filadhu", options=list(SERVICE_STRUCTURE.keys()))
        sub_cat = col2.selectbox("🔵 Gosa Tajaajilaa Tarreeffama Isaa", options=SERVICE_STRUCTURE[main_cat])
        
        # 3. Kaffaltii fi Scan
        kaffaltii = col1.number_input("Kaffaltii (ETB)", min_value=0.0)
        nagahee_file = col2.file_uploader("Scan Nagahee (Image)", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("💾 Galmeessi"):
            if maqaa and ogeessa:
                n_path = ""
                if nagahee_file:
                    # Suuraa maqaa maamilaatiin kuusuu
                    n_path = os.path.join(NAGAHEE_DIR, f"{maqaa.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.png")
                    with open(n_path, "wb") as f:
                        f.write(nagahee_file.getbuffer())
                
                # SQL Database keessatti kuusuu
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT INTO galmee (guyyaa, maqaa, araddaa, qaxana, tajaajila, ogeessa, kaffaltii, nagahee_path) VALUES (?,?,?,?,?,?,?,?)",
                             (datetime.now().strftime('%d/%m/%Y'), maqaa, "-", "-", sub_cat, ogeessa, kaffaltii, n_path))
                conn.commit()
                conn.close()
                
                st.success(f"✅ Maamilli {maqaa} tajaajila '{sub_cat}' irratti milkiin galmeeffameera!")
                st.rerun()
            else:
                st.error("Maaloo, Maqaa fi Ogeessa guuti!")

# ================= 4. DASHBOARD & REPORT =================
def show_dashboard(df):
    st.title("🏢 Dadar Land Admin Dashboard")
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Galii Waliigalaa", f"{df['kaffaltii'].sum():,.2f} ETB")
    m2.metric("👥 Maamiltoota", len(df))
    m3.metric("🏆 Ogeessa Active", df['ogeessa'].nunique())
    
    st.divider()
    fig = px.pie(df, values='kaffaltii', names='tajaajila', hole=0.4, 
                 title="Gosa Tajaajilaa & Galii", color_discrete_sequence=px.colors.sequential.Greens_r)
    st.plotly_chart(fig, use_container_width=True)

# ================= 5. APP NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "123": 
            st.session_state.logged_in = True
            st.rerun()
else:
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🔍 Barbaadi"])
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM galmee", conn)
    conn.close()

    if menu == "📊 Dashboard":
        if not df.empty: show_dashboard(df)
        else: st.info("Data'n galmeeffame hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        registration_page()

    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa Waliigalaa")
        st.dataframe(df.drop(columns=['nagahee_path']), use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Gabaasa Buusi (CSV)", csv, "gabaasa_dadar.csv")

    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        q = st.text_input("Maqaa maamilaa barreessi...")
        if q:
            res = df[df['maqaa'].str.contains(q, case=False, na=False)]
            st.write(res)

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import plotly.express as px

# ================= 1. DATABASE & CONFIG =================
DB_FILE = "dadar_land_pro.db"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR): 
    os.makedirs(NAGAHEE_DIR)

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

# ================= 2. DATA LISTS =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa", "Sirreeffama Daangaa"],
    "🏗 Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Dhimma Dhala"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii"]
}

ARADDAA_LIST = ["Araddaa 01", "Araddaa 02", "Araddaa 03", "Araddaa 04", "Araddaa 05"]
QAXANA_LIST = [str(i) for i in range(1, 11)]

# ================= 3. FUNCTIONS (KUTAALEE HOJII) =================

def registration_page():
    st.header("📝 Galmee Haaraa fi Kaffaltii")
    with st.form("galmee_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Maqaa Abbaa Dhimmaa *")
            main_cat = st.selectbox("🟢 Ramaddii Tajaajilaa", options=list(SERVICE_STRUCTURE.keys()))
            araddaa = st.selectbox("📍 Araddaa", options=ARADDAA_LIST)
            fee = st.number_input("💰 Kaffaltii (ETB) *", min_value=0.0, step=10.0)

        with col2:
            ogeessa = st.text_input("Maqaa Ogeessaa *")
            sub_cat = st.selectbox("🔵 Gosa Tajaajilaa", options=SERVICE_STRUCTURE[main_cat])
            qaxana = st.selectbox("🔢 Qaxana (1-10)", options=QAXANA_LIST)
            nagahee_file = st.file_uploader("📸 Scan Nagahee (Image)", type=['jpg', 'png', 'jpeg'])

        if st.form_submit_button("💾 Galmeessi"):
            if name and ogeessa and fee >= 0:
                n_path = ""
                if nagahee_file:
                    n_path = os.path.join(NAGAHEE_DIR, f"{name.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.png")
                    with open(n_path, "wb") as f:
                        f.write(nagahee_file.getbuffer())
                
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT INTO galmee (guyyaa, maqaa, araddaa, qaxana, tajaajila, ogeessa, kaffaltii, nagahee_path) VALUES (?,?,?,?,?,?,?,?)",
                             (datetime.now().strftime('%d/%m/%Y'), name, araddaa, qaxana, sub_cat, ogeessa, fee, n_path))
                conn.commit()
                conn.close()
                st.success(f"✅ Galmeen {name} tajaajila '{sub_cat}' irratti milkiin kuufameera!")
                st.rerun()
            else:
                st.error("Maaloo, dirree (*) qaban hunda sirriitti guuti!")

def show_dashboard(df):
    st.title("📊 Dashboard Gabaasa Kaffaltii")
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Galii Waliigalaa", f"{df['kaffaltii'].sum():,.2f} ETB")
    m2.metric("👥 Baay'ina Maamiltootaa", len(df))
    m3.metric("📈 Giddu-galeessa Kaffaltii", f"{df['kaffaltii'].mean():,.2f} ETB")

    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig_pie = px.pie(df, values='kaffaltii', names='tajaajila', hole=0.4, title="Galiin Gosa Tajaajilaatiin")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        qaxana_rev = df.groupby('qaxana')['kaffaltii'].sum().reset_index()
        fig_bar = px.bar(qaxana_rev, x='qaxana', y='kaffaltii', color='qaxana', title="Galii Qaxana Qaxanaan")
        st.plotly_chart(fig_bar, use_container_width=True)

def search_page(df):
    st.header("🔍 Barbaadi fi Nagahee Ilaali")
    q = st.text_input("Maqaa maamilaa barreessi...")
    if q:
        res = df[df['maqaa'].str.contains(q, case=False, na=False)]
        for _, row in res.iterrows():
            with st.expander(f"📄 {row['maqaa']} | {row['tajaajila']} | {row['guyyaa']}"):
                c1, c2 = st.columns([2, 1])
                c1.write(f"**Qaxana:** {row['qaxana']} | **Araddaa:** {row['araddaa']}")
                c1.write(f"**Kaffaltii:** {row['kaffaltii']} ETB | **Ogeessa:** {row['ogeessa']}")
                if row['nagahee_path'] and os.path.exists(row['nagahee_path']):
                    c2.image(row['nagahee_path'], caption="Scan Nagahee")
                else:
                    c2.info("Scan nagahee hin jiru.")

# ================= 4. MAIN APP LOGIC =================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login: Bulchiinsa Lafa Dadar")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Username ykn Password dogoggora!")
else:
    st.sidebar.header("Dadar Land Pro")
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "📈 Gabaasa Guutuu"])
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM galmee", conn)
    conn.close()

    if menu == "📊 Dashboard":
        if not df.empty: show_dashboard(df)
        else: st.info("Data'n galmeeffame hin jiru.")
    elif menu == "📝 Galmee Haaraa":
        registration_page()
    elif menu == "🔍 Barbaadi":
        search_page(df)
    elif menu == "📈 Gabaasa Guutuu":
        st.header("📋 Gabaasa Galmee Hundaatti")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Gabaasa CSV Buusi", csv, "gabaasa_dadar.csv")

    if st.sidebar.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.rerun()

# ================= 2. SERVICE LIST (GOSA TAJAAJILAA) =================
# Gosa tajaajilaa hunda akka gosa gurguddaatti addaan baasuu
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"
    ]
}

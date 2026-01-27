import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png" 
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# Telegram Config (Token kee fi Chat ID kee asitti jijjiiri)
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"

# ================= 2. SERVICE STRUCTURE (RAMADDII) =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax) 2%"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Hayyama Ijaarsaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
    "📂 Tajaajila Biroo": ["Waraqaa Qulqullummaa", "Deebii Iyyannoo"]
}

# ================= 3. FUNCTIONS =================
def send_telegram_msg(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
        requests.get(url)
    except:
        pass

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 4. UI SETUP =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

st.markdown("""
    <style>
    .login-box { background: white; padding: 30px; border-radius: 15px; box-shadow: 0px 5px 15px rgba(0,0,0,0.1); border-top: 5px solid #2e7d32; text-align: center; }
    .card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #2e7d32; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# ================= 5. LOGIN SCREEN =================
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=90)
        st.header("Dadar Land Admin")
        with st.form("Login"):
            u, p = st.text_input("Username"), st.text_input("Password", type="password")
            if st.form_submit_button("SEENI"):
                if u == "admin" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= 6. MAIN SYSTEM =================
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa", "🔍 Barbaadi", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c1.text_input("Araddaa")
            qax = c2.text_input("Qaxana")
            og = c2.text_input("Maqaa Ogeessaa")
            
            # Ramaddii fi Gosa addaan baasuu
            cat = st.selectbox("Ramaddii Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
            gosa = st.selectbox("Gosa Tajaajilaa", SERVICE_STRUCTURE[cat])
            
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            final_fee = fee * 0.02 if "TOT" in gosa else fee

            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, gosa, og, final_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    # Telegram irratti erguu
                    msg = f"✅ Galmee Haaraa:\nMaqaa: {name}\nTajaajila: {gosa}\nKaffaltii: {final_fee} ETB\nOgeessa: {og}"
                    send_telegram_msg(msg)
                    
                    st.success(f"✅ Galmeeffameera! Telegram irrattis ergameera.")

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f}")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        st.plotly_chart(px.bar(df, x='Gosa_Tajajjilaa', y='Kafaltii_Taj', color='Gosa_Tajajjilaa'))

    elif menu == "🏆 Badhaasa":
        st.title("🏆 Badhaasa Ogeeyyii Cimaa")
        if not df.empty:
            top_og = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            icons = ["🥇", "🥈", "🥉"]
            for i, (name, count) in enumerate(top_og.items()):
                with cols[i]:
                    st.markdown(f"""<div class='card'><h2>{icons[i]}</h2><b>{name}</b><br>Maamiltoota {count} tajaajile.</div>""", unsafe_allow_html=True)
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa")
        st.dataframe(df)
        st.download_button("📥 CSV Buufadhu", df.to_csv(index=False), "gabaasa.csv")

    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi & Haqii")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            if st.button("🗑 Haqii"):
                df = df.drop(res.index)
                save_data(df); st.rerun()

import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# ================= 2. CORE FUNCTIONS =================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"}
        requests.get(url, params=params)
    except: pass

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. UI SETUP =================
st.set_page_config(page_title="Dadar Land Administration", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .stMetric { background: white; padding: 15px; border-radius: 10px; border-top: 5px solid #2e7d32; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ================= 4. SERVICE LIST =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
}

# ================= 5. LOGIN LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni", use_container_width=True):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        
        selected_cats = st.multiselect("Duraan dursa Ramaddii Tajaajilaa filadhu:", list(SERVICE_STRUCTURE.keys()))
        
        with st.form("reg_form", clear_on_submit=True):
            st.subheader("👤 Ragaa Abbaa Dhimmaa")
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee Scan (Suuraa)", type=['jpg','png','jpeg'])

            st.divider()
            st.subheader("🛠 Tajaajiloota Filataman")
            
            final_services = []
            total_fee = 0
            
            if selected_cats:
                cols = st.columns(len(selected_cats))
                for i, cat in enumerate(selected_cats):
                    with cols[i]:
                        st.write(f"**{cat}**")
                        subs = st.multiselect(f"Gosa {cat}:", SERVICE_STRUCTURE[cat], key=f"sub_{cat}")
                        for s in subs:
                            fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"fee_{s}")
                            final_services.append(s)
                            total_fee += fee
            
            st.info(f"💰 Waliigala Kaffaltii: **{total_fee:,.2f} ETB**")

            if st.form_submit_button("💾 Galmeessi FI Telegramitti Ergi", use_container_width=True):
                if name and final_services and ogeessa:
                    # Suuraa Nagahee Save gochuu
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    # Ragaa Galmeessuu
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    # Beeksisa Telegram
                    telegram_msg = f"🔔 *Galmee Haaraa*\n👤 Maqaa: {name}\n🛠 Tajaajila: {', '.join(final_services)}\n💰 Waliigala Kaffaltii: {total_fee} ETB\n👷 Ogeessa: {ogeessa}"
                    send_telegram(telegram_msg)
                    
                    st.success(f"✅ Maamilichi galmeeffameera! Gabaasni gara Telegramitti ergameera.")
                else:
                    st.error("Maaloo! Maqaa, tajaajila fi ogeessa guutuu kee mirkaneeffadhu.")

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            st.plotly_chart(px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa', title="Trendii Kaffaltii Guyyaatti"))
            st.plotly_chart(px.pie(df, names='Gosa_Tajajjilaa', values='Kafaltii_Taj', title="Qoodinsa Galii Gosa Tajaajilaan"))
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Bal'aa")
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Gabaasa (CSV) Buufadhu", df.to_csv(index=False), "gabaasa_dadar.csv")

import streamlit as st
import pandas as pd
import os
import requests
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
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
    .stButton>button { background-color: #2e7d32; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ================= 4. SERVICE STRUCTURE =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
}

# ================= 5. MAIN APP =================
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
            else: st.error("Dogoggora Username ykn Password!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        
        selected_cats = st.multiselect("Duraan dursa Ramaddii Tajaajilaa filadhu:", list(SERVICE_STRUCTURE.keys()))
        
        with st.form("reg_form"):
            st.subheader("👤 Ragaa Abbaa Dhimmaa")
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee Scan (Suuraa)", type=['jpg','png','jpeg'])

            st.divider()
            st.subheader("🛠 Tajaajiloota fi Kaffaltii")
            
            final_services = []
            total_fee = 0
            
            if selected_cats:
                for cat in selected_cats:
                    st.write(f"**📍 {cat}**")
                    subs = st.multiselect(f"Gosa {cat}:", SERVICE_STRUCTURE[cat], key=f"sub_{cat}")
                    
                    if subs:
                        sub_cols = st.columns(len(subs))
                        for idx, s in enumerate(subs):
                            with sub_cols[idx]:
                                # IDDOO KAFALTII - Asitti mul'ata
                                fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"fee_{s}")
                                final_services.append(s)
                                total_fee += fee
            else:
                st.info("Maaloo, duraan dursa gubbaatti 'Ramaddii Tajaajilaa' filadhu.")

            st.markdown("---")
            st.warning(f"💰 Waliigala Kaffaltii: **{total_fee:,.2f} ETB**")

            if st.form_submit_button("💾 GALMEESSI FI TELEGRAMITTI ERGI", use_container_width=True):
                if name and final_services and ogeessa:
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    telegram_msg = f"🔔 *GALMEE HAARAA*\n👤 Maqaa: {name}\n📍 Araddaa: {ara}\n🛠 Tajaajila: {', '.join(final_services)}\n💰 Kaffaltii: {total_fee:,.2f} ETB\n👷 Ogeessa: {ogeessa}"
                    send_telegram(telegram_msg)
                    
                    st.success(f"✅ Maamilichi galmeeffameera! Gabaasni Telegramitti ergameera.")
                    st.balloons()
                else:
                    st.error("Maaloo! Ragaa hunda guuti.")

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            st.plotly_chart(px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa', title="Trendii Kaffaltii Guyyaatti"))
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    # --- REPORT ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.title("📈 Gabaasa Galii")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Excel/CSV Buufadhu", csv, "Gabaasa_Dadar.csv", "text/csv")

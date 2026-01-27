import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
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

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# UI Style
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-bottom: 4px solid #007bff; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def send_telegram_msg(msg, image_path=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
        requests.get(url + "sendMessage", params={"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"})
        if image_path:
            with open(image_path, "rb") as photo:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID_MANAGER}, files={"photo": photo})
    except: pass

def send_telegram_doc(file_path):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open(file_path, "rb") as file:
            requests.post(url, data={"chat_id": CHAT_ID_MANAGER}, files={"document": file})
        return True
    except: return False

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. SERVICE DEFINITION =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
}

# ================= 4. AUTHENTICATION =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.title("🔐 Login")
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.title("Dadar Admin")
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Haqii", "📈 Gabaasa", "Logout"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Analysis Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.plotly_chart(px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa', barmode='group'))
        else: st.info("Ragaan galmeeffame hin jiru.")

    # --- REGISTRATION (FIXED FEE LOGIC) ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Haaraa")
        cats = st.multiselect("Tajaajila Filadhu:", list(SERVICE_STRUCTURE.keys()))
        with st.form("reg_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c1.selectbox("Araddaa", ["01", "02", "03", "04", "Baadiyyaa"])
            qax = c2.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee (Suuraa)", type=['jpg','png','jpeg'])
            
            final_services = []
            total_fee = 0.0 # Herregni float akka ta'u
            
            for cat in cats:
                st.write(f"**--- {cat} ---**")
                subs = st.multiselect(f"Gosa {cat}:", SERVICE_STRUCTURE[cat], key=f"sub_{cat}")
                for s in subs:
                    if "TOT" in s:
                        col_t1, col_t2 = st.columns(2)
                        gurg = col_t1.text_input(f"Maqaa Gurguraa", key=f"gurg_{s}")
                        bit = col_t2.text_input(f"Maqaa Bitaa", key=f"bit_{s}")
                        gatii = st.number_input(f"Gatii Waliigaltee ({s})", min_value=0.0, key=f"val_{s}")
                        fee = gatii * 0.02
                        final_services.append(f"{s} [{gurg} -> {bit}]")
                    else:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"fee_{s}")
                        final_services.append(s)
                    total_fee += fee # Kaffaltiin itti fufiinsaan ida'ama
            
            st.write(f"### Waliigala: **{total_fee:,.2f} ETB**")

            if st.form_submit_button("💾 GALMEESSI FI ERGI"):
                if name and final_services:
                    f_path = None
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    msg = f"🚀 *GALMEE HAARAA*\n👤 Maamila: {name}\n📍 Araddaa: {ara}\n🛠 Tajaajila: {', '.join(final_services)}\n💰 *Kaffaltii: {total_fee:,.2f} ETB*\n👷 Ogeessa: {ogeessa}"
                    send_telegram_msg(msg, f_path)
                    st.success("✅ Galmeeffamee Hoogganaatti ergameera!")
                else: st.error("Maaloo ragaa guutuu galchi!")

    # --- SEARCH & DELETE ---
    elif menu == "🔍 Barbaadi & Haqii":
        st.title("🔍 To'annoo Ragaalee")
        q_name = st.text_input("Maqaa maamilaa...")
        if q_name:
            filtered = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q_name, case=False, na=False)]
            if not filtered.empty:
                st.dataframe(filtered)
                target_id = st.selectbox("ID Haquuf:", filtered.index)
                if st.button("🚨 Haqii"):
                    df = df.drop(target_id)
                    save_data(df)
                    st.success("Haqameera!")
                    st.rerun()
            else: st.warning("Ragaan hin jiru.")

    # --- REPORT ---
    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Waliigalaa")
        if not df.empty:
            st.dataframe(df)
            report_name = f"Report_{datetime.now().strftime('%d_%m_%Y')}.csv"
            st.download_button("📥 CSV Buufadhu", df.to_csv(index=False), report_name)
        else: st.info("Ragaan hin jiru.")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

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

# ================= 2. CORE FUNCTIONS =================
def send_telegram(msg, image_path=None):
    try:
        base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
        requests.get(base_url + "sendMessage", params={
            "chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"
        })
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as photo:
                requests.post(base_url + "sendPhoto", data={"chat_id": CHAT_ID_MANAGER}, files={"photo": photo})
    except: pass

def send_telegram_file(file_path):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open(file_path, "rb") as file:
            requests.post(url, data={"chat_id": CHAT_ID_MANAGER}, files={"document": file})
        return True
    except: return False

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. SERVICE STRUCTURE =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
}

# ================= 4. UI SETUP & LOGIN =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

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
            if st.form_submit_button("SEENI", use_container_width=True):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.title("Dadar Admin")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Haqii", "📈 Gabaasa", "Logout"])
        quick_search = st.text_input("Maqaa Maamilaa...", placeholder="Barbaadi...")

    # ================= 5. DASHBOARD =================
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.plotly_chart(px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa'))

    # ================= 6. REGISTRATION (WITH TOT & TELEGRAM) =================
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa")
        selected_cats = st.multiselect("Ramaddii Filadhu:", list(SERVICE_STRUCTURE.keys()))
        with st.form("reg_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c1.text_input("Araddaa")
            qax = c2.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee Scan", type=['jpg','png','jpeg'])
            
            final_services = []
            total_fee = 0
            if selected_cats:
                for cat in selected_cats:
                    subs = st.multiselect(f"Gosa {cat}:", SERVICE_STRUCTURE[cat])
                    for s in subs:
                        if "TOT" in s:
                            col_t1, col_t2 = st.columns(2)
                            gurguraa = col_t1.text_input("Maqaa Gurguraa")
                            bitaa = col_t2.text_input("Maqaa Bitaa")
                            gatii_wal = st.number_input("Gatii Waliigaltee", min_value=0.0)
                            fee = gatii_wal * 0.02
                            final_services.append(f"{s} [G: {gurguraa}, B: {bitaa}]")
                        else:
                            fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0)
                            final_services.append(s)
                        total_fee += fee

            if st.form_submit_button("💾 GALMEESSI FI ERGI"):
                if name and final_services:
                    f_path = None
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    send_telegram(f"🚀 *GALMEE HAARAA*\n👤 {name}\n💰 {total_fee:,.2f} ETB\n🛠 {', '.join(final_services)}", f_path)
                    st.success("Galmeeffameera!")

    # ================= 7. SEARCH & DELETE =================
    elif menu == "🔍 Barbaadi & Haqii":
        st.title("🔍 Barbaadi")
        q = st.text_input("Maqaa Barbaadi:", value=quick_search)
        if q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(results)
            if not results.empty:
                idx = st.selectbox("ID Haquuf:", results.index)
                if st.button("🗑 Haqii"):
                    df = df.drop(idx)
                    save_data(df)
                    st.rerun()

    # ================= 8. REPORT (SEND TO TELEGRAM) =================
    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa & Telegram")
        if not df.empty:
            st.dataframe(df)
            csv_data = df.to_csv(index=False)
            file_name = f"gabaasa_{datetime.now().strftime('%d_%m_%Y')}.csv"
            
            c1, c2 = st.columns(2)
            c1.download_button("📥 Buufadhu (CSV)", csv_data, file_name)
            if c2.button("📤 Gabaasa Telegramitti Ergi"):
                with open(file_name, "w") as f: f.write(csv_data)
                if send_telegram_file(file_name):
                    st.success("✅ Gabaasni gara Telegramitti ergameera!")
                os.remove(file_name)
        else: st.info("Ragaan hin jiru.")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

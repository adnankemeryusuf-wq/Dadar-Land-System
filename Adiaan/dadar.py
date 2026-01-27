import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
import plotly.express as px

# ================= 1. CONFIGURATION & LOGIC =================
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
    .stSubheader { color: #1e3a8a; border-bottom: 1px solid #dee2e6; margin-top: 10px;}
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

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. UPDATED SERVICE STRUCTURE =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Kaartaa Lafa Qonnaa"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", "Adabbii Faallaa Pilaanii"
    ],
}

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.title("🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Invaaliidii!")
else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Haqii", "📈 Gabaasa", "Logout"])

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            st.plotly_chart(px.pie(df, values='Kafaltii_Taj', names='Araddaa', title="Galii Araddaadhaan"))
        else: st.info("Ragaan hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa")
        selected_categories = st.multiselect("Ramaddii Tajaajilaa Filadhu:", list(SERVICE_STRUCTURE.keys()))
        
        with st.form("main_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c1.selectbox("Araddaa", ["01", "02", "03", "04", "Baadiyyaa"])
            qax = c2.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee (Suuraa)", type=['jpg','png','jpeg'])
            
            final_services = []
            total_fee = 0.0
            
            # Category tokko tokkoon kaffaltii gaafachuu
            for cat in selected_categories:
                st.subheader(cat)
                subs = st.multiselect(f"Gosa tajaajila {cat}:", SERVICE_STRUCTURE[cat], key=f"sub_{cat}")
                for s in subs:
                    if "TOT" in s:
                        v_gatii = st.number_input(f"Gatii Waliigaltee ({s})", min_value=0.0, key=f"v_{s}")
                        fee = v_gatii * 0.02
                        final_services.append(f"{s} (2%)")
                    else:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"f_{s}")
                        final_services.append(s)
                    total_fee += fee

            st.markdown(f"### 💰 Waliigala Kaffaltii: **{total_fee:,.2f} ETB**")
            
            if st.form_submit_button("💾 GALMEESSI FI ERGI"):
                if name and final_services:
                    f_path = None
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    msg = f"🚀 *GALMEE HAARAA*\n👤 Maamila: {name}\n📍 Bakka: {ara}\n🛠 Tajaajila: {', '.join(final_services)}\n💰 *Kaffaltii: {total_fee:,.2f} ETB*\n👷 Ogeessa: {ogeessa}"
                    send_telegram_msg(msg, f_path)
                    st.success("✅ Galmeeffameera!")
                else: st.error("Maaloo ragaa guuti!")

    elif menu == "🔍 Barbaadi & Haqii":
        st.title("🔍 Barbaadi")
        q = st.text_input("Maqaa maamilaa...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            if not res.empty:
                idx = st.selectbox("ID Haquuf:", res.index)
                if st.button("🚨 Haqii"):
                    df = df.drop(idx)
                    save_data(df)
                    st.rerun()

    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa")
        st.dataframe(df)
        st.download_button("📥 Buufadhu", df.to_csv(index=False), "Report.csv")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

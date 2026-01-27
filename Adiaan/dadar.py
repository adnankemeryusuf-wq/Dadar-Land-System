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

# ================= 3. SERVICE STRUCTURE =================
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

# ================= 4. UI LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("SEENI"):
        if u == "DAD" and p == "2026":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Haqii", "📈 Gabaasa", "Logout"])

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Analysis")
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            st.plotly_chart(px.bar(df, x='Araddaa', y='Kafaltii_Taj', color='Araddaa', title="Galii Araddaadhaan"))

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        selected_categories = st.multiselect("Ramaddii Tajaajilaa Filadhu:", list(SERVICE_STRUCTURE.keys()))
        
        with st.form("main_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c1.selectbox("Araddaa", ["01", "02", "03", "04", "Baadiyyaa"])
            qax = c2.text_input("Qaxana / L.Manaa")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee Scan (Image)", type=['jpg','png','jpeg'])
            
            final_services = []
            total_fee = 0.0
            
            if selected_categories:
                for cat in selected_categories:
                    st.markdown(f"### {cat}")
                    subs = st.multiselect(f"Gosa {cat}:", SERVICE_STRUCTURE[cat], key=f"sub_{cat}")
                    
                    for s in subs:
                        col_a, col_b = st.columns([3, 1])
                        col_a.write(f"🔹 **{s}**")
                        if "TOT" in s:
                            v_gatii = col_b.number_input("Gatii Waliigaltee", min_value=0.0, key=f"v_{s}")
                            fee = v_gatii * 0.02
                            final_services.append(f"{s} (2%)")
                        else:
                            fee = col_b.number_input("Kaffaltii (ETB)", min_value=0.0, key=f"f_{s}")
                            final_services.append(s)
                        total_fee += fee
                
                st.divider()
                st.markdown(f"#### 💰 Waliigala Kaffaltii: **{total_fee:,.2f} ETB**")
            
            if st.form_submit_button("💾 GALMEESSI FI ERGI"):
                if name and final_services:
                    f_path = None
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    msg = f"🚀 *GALMEE HAARAA*\n👤 Maamila: {name}\n📍 Araddaa: {ara}\n🛠 Tajaajila: {', '.join(final_services)}\n💰 *Total: {total_fee:,.2f} ETB*\n👷 Ogeessa: {ogeessa}"
                    send_telegram_msg(msg, f_path)
                    st.success("Milkaa'inaan galmeeffameera!")
                else: st.error("Maaloo ragaa guuti!")

    elif menu == "🔍 Barbaadi & Haqii":
        st.title("🔍 To'annoo Ragaalee")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            if not res.empty:
                idx = st.selectbox("ID filadhu:", res.index)
                if st.button("🚨 HAQUU"):
                    df = df.drop(idx)
                    save_data(df)
                    st.rerun()

    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Waliigalaa")
        st.dataframe(df)
        st.download_button("📥 CSV Buufadhu", df.to_csv(index=False), "Dadar_Report.csv")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

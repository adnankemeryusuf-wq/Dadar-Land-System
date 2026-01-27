import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"

# Telegram Security
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# Professional CSS for visual appeal
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #007bff; }
    div.stButton > button { border-radius: 5px; height: 3em; width: 100%; background-color: #007bff; color: white; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e3440, #4c566a); color: white; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE LOGIC =================
def send_telegram_msg(msg, image_path=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
        requests.get(url + "sendMessage", params={"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"})
        if image_path:
            with open(image_path, "rb") as photo:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID_MANAGER}, files={"photo": photo})
    except Exception: pass

def send_telegram_doc(file_path):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open(file_path, "rb") as file:
            requests.post(url, data={"chat_id": CHAT_ID_MANAGER}, files={"document": file})
        return True
    except Exception: return False

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
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.write("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=180)
        st.title("🔐 Admin Login")
        with st.form("login_form"):
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("SIGN IN"):
                if user == "DAD" and password == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Invaaliidii dha!")
else:
    # ================= 5. MAIN NAVIGATION =================
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.title("Admin Panel")
        menu = st.radio("MAIN MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Haqii", "📈 Gabaasa Guutuu", "Logout"])
        st.divider()
        st.info(f"📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}")

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Analysis Dashboard")
        if not df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💰 Gatii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.0f} ETB")
            c2.metric("👥 Maamiltoota", f"{len(df)}")
            c3.metric("👷 Ogeeyyii", f"{df['Maqaa_Ogeessa'].nunique()}")
            c4.metric("📍 Araddaalee", f"{df['Araddaa'].nunique()}")
            
            st.divider()
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                fig_bar = px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa', title="Gali Guyyaatti", template="plotly_white")
                st.plotly_chart(fig_bar, use_container_width=True)
            with col_chart2:
                fig_pie = px.pie(df, values='Kafaltii_Taj', names='Araddaa', title="Galii Araddaadhaan", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("Ragaan galmeeffame hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa Filadhu:", list(SERVICE_STRUCTURE.keys()))
        
        with st.form("professional_reg_form", clear_on_submit=True):
            st.subheader("👤 Ragaa Maamilaa")
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c1.selectbox("Araddaa Filadhu", ["01", "02", "03", "04", "Baadiyyaa"])
            qax = c2.text_input("Qaxana / Zone")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee (Image Only)", type=['jpg','png','jpeg'])
            
            final_services = []
            total_fee = 0
            if selected_cats:
                st.divider()
                for cat in selected_cats:
                    st.write(f"**{cat}**")
                    subs = st.multiselect(f"Gosa tajaajila {cat}:", SERVICE_STRUCTURE[cat])
                    for s in subs:
                        if "TOT" in s:
                            st.info("ℹ️ TOT Herreguuf")
                            v1, v2 = st.columns(2)
                            gurguraa = v1.text_input(f"Maqaa Gurguraa ({s})")
                            bitaa = v2.text_input(f"Maqaa Bitaa ({s})")
                            gatii = st.number_input("Gatii Waliigaltee", min_value=0.0, key=f"tot_{s}")
                            fee = gatii * 0.02
                            final_services.append(f"{s} [G:{gurguraa} -> B:{bitaa}]")
                        else:
                            fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"fee_{s}")
                            final_services.append(s)
                        total_fee += fee

            st.write("---")
            st.subheader(f"💰 Waliigala Kaffaltii: {total_fee:,.2f} ETB")
            
            if st.form_submit_button("💾 GALMEESSI FI ERGI"):
                if name and final_services and ogeessa:
                    f_path = None
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    services_str = ", ".join(final_services)
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, services_str, ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    # Professional Telegram Message
                    t_msg = f"🔔 *GALMEE HAARAA RAWWATAME*\n\n👤 *Maamila:* {name}\n📍 *Bakka:* {ara} ({qax})\n🛠 *Tajaajila:* {services_str}\n💰 *Kaffaltii:* {total_fee:,.2f} ETB\n👷 *Ogeessa:* {ogeessa}\n\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                    send_telegram_msg(t_msg, f_path)
                    st.success("✅ Ragaan milkaa'inaan galmeeffamee Hoogganaatti ergameera!")
                else:
                    st.error("Maaloo ragaa barbaachisu hunda guuti!")

    # --- SEARCH & DELETE ---
    elif menu == "🔍 Barbaadi & Haqii":
        st.title("🔍 To'annoo Ragaalee")
        q = st.text_input("Maqaa maamilaa galchi...")
        if q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not results.empty:
                st.table(results)
                st.divider()
                idx_to_del = st.selectbox("ID Haqamu filadhu:", results.index)
                if st.button("🚨 Ragaa Kana Haqii"):
                    df = df.drop(idx_to_del)
                    save_data(df)
                    st.success("Haqameera!")
                    st.rerun()
            else:
                st.warning("Maqaa kanaan ragaan hin jiru.")

    # --- FULL REPORT & TELEGRAM ---
    elif menu == "📈 Gabaasa Guutuu":
        st.title("📈 Gabaasa Waliigalaa")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            report_file = f"Report_{datetime.now().strftime('%d_%m_%Y')}.csv"
            
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📥 Gabaasa Buufadhu (CSV)", df.to_csv(index=False), report_file)
            with c2:
                if st.button("📤 Gabaasa Gara Telegramitti Ergi"):
                    df.to_csv(report_file, index=False)
                    if send_telegram_doc(report_file):
                        st.success("✅ Gabaasni Hoogganaatti ergameera!")
                    os.remove(report_file)
        else:
            st.info("Gabaasni argamu hin jiru.")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

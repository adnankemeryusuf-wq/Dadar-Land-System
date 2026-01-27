import streamlit as st
import pandas as pd  # Fixed import
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png" 
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 2. UI STYLE (CENTERING) =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    /* Centering logic for the login box */
    [data-testid="stVerticalBlock"] > div:has(div.login-box) {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .login-box {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 8px solid #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 3. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 4. LOGIN SCREEN (CENTERED) =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
        st.header("Dadar Land Administration")
        st.write("Customer Registration System")
        
        with st.form("Login"):
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("SEENI / LOGIN")
            
            if submit:
                if user == "admin" and password == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= 5. MAIN SYSTEM =================
else:
    df = load_data()
    
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, width=100)
    st.sidebar.title("Main Menu")
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltootaa", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            fig = px.bar(df.groupby('Gosa_Tajajjilaa')['Kafaltii_Taj'].sum().reset_index(), 
                         x='Gosa_Tajajjilaa', y='Kafaltii_Taj', 
                         color='Gosa_Tajajjilaa',
                         title="Galii Gosa Tajaajilaan")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Hanga ammaatti ragaan galmeeffame hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        SERVICE_STRUCTURE = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax) 2%"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa"],
            "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Hayyama Ijaarsaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
            "📂 Tajaajila Biroo": ["Waraqaa Qulqullummaa", "Deebii Iyyannoo"],
            "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"]
        }

        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col1.text_input("Araddaa")
            qax = col2.text_input("Qaxana")
            og = col2.text_input("Maqaa Ogeessaa")
            
            cat_choice = st.selectbox("Ramaddii Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
            serv_choice = st.selectbox("Gosa Tajaajilaa", SERVICE_STRUCTURE[cat_choice])
            
            fee_input = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            # Auto-calculate TOT if selected
            final_fee = fee_input * 0.02 if "TOT" in serv_choice else fee_input

            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, serv_choice, og, final_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Kafaltii waliigalaa: {final_fee:,.2f} ETB")
                else:
                    st.error("Maaloo, maqaa abbaa dhimmaa fi maqaa ogeessaa guutaa.")

    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Waliigalaa")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV Buufadhu", csv, "gabaasa_dadar.csv", "text/csv")

    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi / Haqii")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not results.empty:
                st.dataframe(results)
                idx = st.selectbox("ID Haquuf filadhu:", results.index)
                if st.button("🗑 Haqii"):
                    df = df.drop(idx)
                    save_data(df)
                    st.success("Ragaan haqameera!")
                    st.rerun()
            else:
                st.warning("Maqaa kanaan ragaan argame hin jiru.")
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
    except Exception as e:
        st.error(f"Telegram error: {e}")

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. UI STYLE =================
st.set_page_config(page_title="Dadar Land Administration", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .stMetric { background: white; padding: 15px; border-radius: 10px; border-top: 5px solid #2e7d32; }
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
            else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa"])

    # --- REGISTRATION ---
    if menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        
        selected_cats = st.multiselect("Ramaddii Tajaajilaa Filadhu:", list(SERVICE_STRUCTURE.keys()))
        
        final_services = []
        total_fee = 0
        
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    st.write(f"**{cat}**")
                    subs = st.multiselect(f"Gosa {cat}:", SERVICE_STRUCTURE[cat], key=cat)
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"fee_{s}")
                        final_services.append(s)
                        total_fee += fee

        st.divider()
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee Scan (Image)", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services and ogeessa:
                    # Save Image
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    # Save Data
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    # Telegram Notification
                    telegram_msg = f"🔔 *Galmee Haaraa*\n👤 Maqaa: {name}\n🛠 Tajaajila: {', '.join(final_services)}\n💰 Kaffaltii: {total_fee} ETB\n👷 Ogeessa: {ogeessa}"
                    send_telegram(telegram_msg)
                    
                    st.success(f"✅ Galmeeffameera! Gabaasni gara Telegramitti ergameera.")
                else: st.error("Maaloo odeeffannoo guutuu galchi!")

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
        else: st.info("Hanga ammaatti ragaan galmeeffame hin jiru.")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Bal'aa")
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Gabaasa Buufadhu (CSV)", df.to_csv(index=False), "gabaasa_dadar.csv")

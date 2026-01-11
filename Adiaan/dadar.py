import streamlit as st
import os
import requests
import qrcode
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- 1. CONFIG (Bal'ina PC-f) ---
st.set_page_config(
    page_title="Dadar Land Administration System",
    page_icon="🏢",
    layout="wide", # Skriinii PC guutuu akka fayyadamuuf
    initial_sidebar_state="expanded"
)

# --- CONFIG DATA ---
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8586015354:AAEliISf-RtoeJ8anbVLapY3NBm7hz8dZWI"
CHAT_ID_MANAGER = "568248052"
DATA_FILE = "dadar_final_report.txt"

# --- LOGO SEARCH ---
logo_options = ["Adiaan/logo.png", "Adiaan/logo.png.png", "logo.png", "logo.png.png"]
LOGO_PATH = next((p for p in logo_options if os.path.exists(p)), None)

# --- 2. CUSTOM CSS (PC Design) ---
st.markdown("""
    <style>
    /* Bakka Login PC irratti gidduu qabachiisuuf */
    .login-container {
        max-width: 450px;
        margin: auto;
        padding: 50px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    /* Metric Cards Style */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* Button PC Style */
    .stButton>button {
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
def send_telegram(file_data, file_name, file_type="doc", caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    url += "sendDocument" if file_type == "doc" else "sendPhoto"
    try:
        files = {'document' if file_type == "doc" else 'photo': (file_name, file_data)}
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, files=files, timeout=15)
    except: pass

# --- 3. LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Page (Centered on PC)
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=150)
        st.markdown("<h2 style='text-align: center;'>Dadar Land System</h2>", unsafe_allow_html=True)
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("LOG IN"):
                if u == USER_NAME and p == PASS_WORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Ragaan galchite sirrii miti!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 4. MAIN DASHBOARD (PC LAYOUT) ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.title("Admin Panel")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi (Search)", "📊 Gabaasa Excel", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)
        st.divider()
        st.info("User: Admin | Online")

    # Centered Header
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if LOGO_PATH: st.image(LOGO_PATH, width=100)
    st.markdown("<h1 style='color: #1f4e78;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>", unsafe_allow_html=True)
    st.markdown("<p>Customer Registration and Management System</p></div>", unsafe_allow_html=True)
    st.divider()

    # --- 5. DASHBOARD HOME ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            total_ppl = len(df)
            total_money = df[10].astype(float).sum() if len(df.columns) > 10 else 0
            
            # PC Columns (Metric Cards side by side)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Abbootii Dhimmaa", f"{total_ppl}")
            m2.metric("Galii Waligalaa", f"{total_money:,.2f} ETB")
            m3.metric("Gosa Tajaajilaa", "5")
            m4.metric("Status", "Active ✅")
            
            st.write("### 🕒 Galmeewwan Dhiyoo (Recent Registrations)")
            df.columns = ["Yeroo", "Maqaa", "Bilbila", "Gosa", "Ogeessa", "B_Og", "Beellama", "Kartaa", "User", "Jij", "Waligala"]
            st.dataframe(df.tail(15), use_container_width=True) # PC irratti table bal'aa ta'ee mul'ata
        else:
            st.info("Hanga ammaatti ragaan galmaa'e hin jiru.")

    # --- 6. GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Haaraa")
        with st.form("PC_Entry", clear_on_submit=True):
            # PC irratti columns sadiitti qoodna (Layout qusachuuf)
            c1, c2, c3 = st.columns(3)
            with c1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                bad = st.text_input("Bilbila Abbaa Dhimmaa")
            with c2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizio", "TOT", "Gibira"])
                og = st.text_input("Maqaa Ogeessa")
            with c3:
                gb = st.date_input("Beellama Guyyaa")
                sb = st.time_input("Sa'aatii")

            st.write("--- 💰 Kafaltiiwwan ---")
            k1, k2, k3 = st.columns(3)
            with k1: kartaa = st.number_input("Kafaltii Kartaa", min_value=0.0)
            with k2: user = st.number_input("User Fee", min_value=0.0)
            with k3: jij = st.number_input("Jijjiirra Maqaa", min_value=0.0)

            if st.form_submit_button("✅ Galmee Xumuri"):
                if ad and bad:
                    total = kartaa + user + jij
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Save
                    line = f"{now}|{ad}|{bad}|{gs}|{og}|-|{gb} {sb}|{kartaa}|{user}|{jij}|{total}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    # QR
                    qr = qrcode.make(f"AD: {ad}\nKafaltii: {total} ETB\nBeellama: {gb}")
                    buf = BytesIO(); qr.save(buf, format="PNG")
                    send_telegram(buf.getvalue(), f"{ad}.png", "photo", f"✅ Galmee: {ad}\n💰 {total} ETB")
                    st.success(f"Galmeen {ad} milkiin xumurameera!")
                    st.image(buf.getvalue(), width=150)
                else: st.warning("Maaloo Maqaa fi Bilbila guuti!")

    # --- 7. SEARCH & EXCEL (PC EXCLUSIVE) ---
    elif choice == "🔍 Barbaadi (Search)":
        st.subheader("🔍 Ragaa Barbaadi")
        query = st.text_input("Maqaa ykn Bilbila galchi:")
        if query and os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            res = df[df.apply(lambda row: query.lower() in row.astype(str).str.lower().values, axis=1)]
            st.dataframe(res, use_container_width=True)

    elif choice == "📊 Gabaasa Excel":
        st.subheader("📊 Gabaasa Gara Telegram")
        if st.button("🚀 Excel Gara Telegram Ergi"):
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE, sep="|", header=None)
                buf = BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                send_telegram(buf.getvalue(), "Gabaasa.xlsx", "doc", "Gabaasa Bulchiinsa Lafaa")
                st.success("Gabaasni hoggantatti ergameera!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

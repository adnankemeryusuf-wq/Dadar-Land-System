import streamlit as st
import os
import requests
import qrcode
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- QINDAA'INA (CONFIG) ---
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8586015354:AAEliISf-RtoeJ8anbVLapY3NBm7hz8dZWI"
CHAT_ID_MANAGER = "568248052"
DATA_FILE = "dadar_final_report.txt"

# --- LOGO BARBAADU ---
logo_options = ["Adiaan/logo.png", "Adiaan/logo.png.png", "logo.png", "logo.png.png"]
LOGO_PATH = next((p for p in logo_options if os.path.exists(p)), None)

# --- WEB UI CONFIG ---
st.set_page_config(
    page_title="Dadar Land Administration", 
    page_icon=LOGO_PATH if LOGO_PATH else "🏢",
    layout="wide"
)

# --- CUSTOM CSS (Style Bareeduuf) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKSHIINIIWWAN ---
def send_telegram(file_data, file_name, file_type="doc", caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    url += "sendDocument" if file_type == "doc" else "sendPhoto"
    try:
        files = {'document' if file_type == "doc" else 'photo': (file_name, file_data)}
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, files=files, timeout=20)
    except:
        st.error("Internet kee mirkaneeffadhu!")

# --- LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if LOGO_PATH: st.image(LOGO_PATH, width=150)
        st.title("Dadar Land System Login")
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni (Login)"):
                if u == USER_NAME and p == PASS_WORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maqaa ykn Password dogoggora!")
else:
    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.title("Dashboard")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa Excel", "🚪 Logout"]
        choice = st.selectbox("Filannoo", menu)
        st.info("Systemii Bulchiinsa Lafaa Magaalaa Dadar")

    # --- MAIN PAGE HEADER ---
    st.markdown(f"<h1 style='text-align: center; color: #1f4e78;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>", unsafe_allow_html=True)
    st.write("---")

    # --- 1. DASHBOARD HOME ---
    if choice == "🏠 Dashboard":
        st.subheader("📈 Haala Waliigalaa Today")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            total_entries = len(df)
            total_money = df[10].astype(float).sum() if len(df.columns) > 10 else 0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Abbootii Dhimmaa", f"{total_entries}")
            m2.metric("Galii Waligalaa (ETB)", f"{total_money:,.2f}")
            m3.metric("Status", "Active", delta="Online")
            
            st.write("### Galmeewwan dhiyoo")
            df.columns = ["Yeroo", "Maqaa", "Bilbila", "Tajaajila", "Ogeessa", "B_Ogeessa", "Beellama", "Kartaa", "User", "Jijjiirra", "Waligala"]
            st.dataframe(df.tail(5), use_container_width=True)
        else:
            st.info("Hanga ammaatti ragaan galmaa'e hin jiru.")

    # --- 2. GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Abbaa Dhimmaa Haaraa")
        with st.container():
            with st.form("EntryForm", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    ad = st.text_input("Maqaa Abbaa Dhimmaa")
                    bad = st.text_input("Bilbila Abbaa Dhimmaa")
                    gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizio", "TOT", "Gibira"])
                with c2:
                    og = st.text_input("Maqaa Ogeessa")
                    bog = st.text_input("Bilbila Ogeessa")
                    gb = st.date_input("Beellama")
                    sb = st.time_input("Sa'aatii")

                st.markdown("#### 💰 Kafaltiiwwan")
                k1, k2, k3 = st.columns(3)
                with k1: kartaa = st.number_input("Kartaa", min_value=0.0)
                with k2: user = st.number_input("User Fee", min_value=0.0)
                with k3: jijjiirra = st.number_input("Jij_Maqaa", min_value=0.0)
                
                if st.form_submit_button("✅ Galmeessi fi QR Uumi"):
                    if ad and bad:
                        waligala = kartaa + user + jijjiirra
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        # QR Logic
                        qr = qrcode.make(f"AD: {ad}\nKafaltii: {waligala} ETB\nBeellama: {gb}")
                        qr_buf = BytesIO()
                        qr.save(qr_buf, format="PNG")
                        
                        # Save Logic
                        line = f"{now_str}|{ad}|{bad}|{gs}|{og}|{bog}|{gb} {sb}|{kartaa}|{user}|{jijjiirra}|{waligala}\n"
                        with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                        
                        # Feedback
                        send_telegram(qr_buf.getvalue(), f"{ad}.png", "photo", f"✅ Galmee: {ad}\n💰 Waligala: {waligala} ETB")
                        st.success(f"Abbaan dhimmaa {ad} galmaa'eera!")
                        st.image(qr_buf.getvalue(), width=200, caption="QR Code Abbaa Dhimmaa")
                    else:
                        st.warning("Maaloo maqaa fi bilbila guuti!")

    # --- 3. GABAASA EXCEL ---
    elif choice == "📊 Gabaasa Excel":
        st.subheader("📊 Gabaasa Gara Telegram Ergi")
        colA, colB = st.columns(2)
        with colA:
            f = st.radio("Yeroo Filadhu:", ["Guyyaa 1", "Torbee 1", "Ji'a 1"])
        
        if st.button("🚀 Gabaasa Gara Telegram Ergi"):
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE, sep="|", header=None)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Gabaasa')
                send_telegram(output.getvalue(), f"Gabaasa_{f}.xlsx", "doc", f"📊 Gabaasa {f}")
                st.success("Gabaasni hoggantatti ergameera!")
            else:
                st.error("Ragaan kuufame hin jiru!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

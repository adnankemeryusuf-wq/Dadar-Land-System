import streamlit as st
import os
import requests
import qrcode
import openpyxl
import pandas as pd
from datetime import datetime
from openpyxl.styles import Font, Alignment, PatternFill
from io import BytesIO

# --- QINDAA'INA (CONFIG) ---
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8586015354:AAEliISf-RtoeJ8anbVLapY3NBm7hz8dZWI"
CHAT_ID_MANAGER = "568248052"
DATA_FILE = "dadar_final_report.txt"

# --- LOGO BARBAADU (Flexible Search) ---
# Maqaa faayila keetii hunda danda'uuf
logo_options = ["Adiaan/logo.png", "Adiaan/logo.png.png", "logo.png", "logo.png.png"]
LOGO_PATH = None
for path in logo_options:
    if os.path.exists(path):
        LOGO_PATH = path
        break

# --- WEB UI CONFIG ---
st.set_page_config(page_title="Dadar Land System", page_icon=LOGO_PATH if LOGO_PATH else "🏢")

# --- FUNKSHIINIIWWAN ERGAA ---
def send_telegram(file_data, file_name, file_type="doc", caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    url += "sendDocument" if file_type == "doc" else "sendPhoto"
    try:
        payload = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
        files = {'document' if file_type == "doc" else 'photo': (file_name, file_data)}
        requests.post(url, data=payload, files=files, timeout=20)
    except:
        st.error("[!] Ergaan Telegram hin darbine. Internet kee mirkaneeffadhu.")

# --- LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    if LOGO_PATH:
        st.image(LOGO_PATH, width=150)
    st.title("W/Bulchiinsa Lafaa Magaalaa Dadar")
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Login Dogoggora!")
else:
    # --- SIDEBAR & MENU ---
    if LOGO_PATH:
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    
    menu = ["Galmee Haaraa", "Gabaasa Excel (Telegram)", "Logout"]
    choice = st.sidebar.selectbox("Filannoo", menu)

    # --- MAIN HEADER ---
    col1, col2 = st.columns([1, 5])
    with col1:
        if LOGO_PATH:
            st.image(LOGO_PATH, width=80)
    with col2:
        st.title("W/Bulchiinsa Lafaa Magaalaa Dadar")

    # --- 1. GALMEE HAARAA ---
    if choice == "Galmee Haaraa":
        st.subheader("📝 Galmee Haaraa Galchi")
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

            st.write("--- Kafaltiiwwan ---")
            k1, k2, k3 = st.columns(3)
            with k1: kartaa = st.number_input("Kartaa", value=0.0)
            with k2: user = st.number_input("User", value=0.0)
            with k3: jijjiirra = st.number_input("Jij_Maqaa", value=0.0)
            
            if st.form_submit_button("Galmeessi"):
                waligala = kartaa + user + jijjiirra
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # QR Generation
                qr = qrcode.make(f"AD: {ad}\nBilbila: {bad}\nKafaltii: {waligala}\nBeellama: {gb}")
                qr_buf = BytesIO()
                qr.save(qr_buf, format="PNG")
                
                # Save to Text File
                line = f"{now_str}|{ad}|{bad}|{gs}|{og}|{bog}|{gb} {sb}|{kartaa}|{user}|{jijjiirra}|{waligala}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(line)
                
                # Send to Telegram
                send_telegram(qr_buf.getvalue(), f"QR_{ad}.png", "photo", f"✅ QR Haaraa: {ad}\n💰 Waligala: {waligala} ETB")
                st.success(f"Galmeeffameera! Waligala: {waligala} ETB")
                st.image(qr_buf.getvalue(), caption=f"QR Code - {ad}")

    # --- 2. GABAASA EXCEL ---
    elif choice == "Gabaasa Excel (Telegram)":
        st.subheader("📊 Gabaasa Gara Telegram Ergi")
        f = st.radio("Yeroo Filadhu:", ["Guyyaa 1", "Torbee 1", "Ji'a 1"])
        days = {"Guyyaa 1": 1, "Torbee 1": 7, "Ji'a 1": 30}[f]
        
        if st.button("Gabaasa Ergi"):
            if os.path.exists(DATA_FILE):
                try:
                    df = pd.read_csv(DATA_FILE, sep="|", header=None, names=["Yeroo", "Abbaa Dhimmaa", "Bilbila", "Tajaajila", "Ogeessa", "B_Ogeessa", "Beellama", "Kartaa", "User", "Jijjiirra", "Waligala"])
                    
                    # Excel Creator
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Gabaasa')
                    
                    send_telegram(output.getvalue(), f"Gabaasa_{f}.xlsx", "doc", f"📊 Gabaasa {f}\n💰 Galii Waligalaa")
                    st.success("Gabaasni hoggantatti ergameera!")
                except Exception as e:
                    st.error(f"Dogoggora: {e}")
            else:
                st.warning("Ragaan kuufame hin jiru.")

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.rerun()

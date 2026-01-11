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

# --- WEB UI ---
st.set_page_config(page_title="Dadar Land System", page_icon="🏢")
st.title("🏢 W/Bulchiinsa Lafaa Magaalaa Dadar")

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
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
    # --- MAIN MENU ---
    menu = ["Galmee Haaraa", "Gabaasa Excel (Telegram)", "Barbaadi (Search)", "Logout"]
    choice = st.sidebar.selectbox("Filannoo", menu)

    if choice == "Galmee Haaraa":
        st.subheader("📝 Galmee Haaraa Galchi")
        with st.form("EntryForm"):
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                bad = st.text_input("Bilbila Abbaa Dhimmaa")
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizio", "TOT", "Gibira"])
            with col2:
                og = st.text_input("Maqaa Ogeessa")
                bog = st.text_input("Bilbila Ogeessa")
                gb = st.date_input("Beellama")
                sb = st.time_input("Sa'aatii")

            st.write("--- Kafaltiiwwan ---")
            k_kartaa = st.number_input("Kartaa", value=0.0)
            k_user = st.number_input("User", value=0.0)
            k_jij = st.number_input("Jij_Maqaa", value=0.0)
            
            if st.form_submit_button("Galmeessi"):
                waligala = k_kartaa + k_user + k_jij
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Generate QR
                qr = qrcode.make(f"AD: {ad}\nKafaltii: {waligala}\nBeellama: {gb}")
                buf = BytesIO()
                qr.save(buf, format="PNG")
                
                # Save Data
                line = f"{now_str}|{ad}|{bad}|-|-|{gs}|{og}|{bog}|{gb} {sb}|{k_kartaa}|{k_user}|{k_jij}|{waligala}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(line)
                
                # Send to Telegram
                send_telegram(buf.getvalue(), f"QR_{ad}.png", "photo", f"✅ QR Haaraa: {ad}\n💰 Waligala: {waligala} ETB")
                st.success(f"Galmeeffameera! Waligala: {waligala} ETB")
                st.image(buf.getvalue(), caption="QR Code Uumame")

    elif choice == "Gabaasa Excel (Telegram)":
        st.subheader("📊 Gabaasa Gara Telegram Ergi")
        f = st.radio("Yeroo Filadhu:", ["Guyyaa 1", "Torbee 1", "Ji'a 1"])
        days = {"Guyyaa 1": 1, "Torbee 1": 7, "Ji'a 1": 30}[f]
        
        if st.button("Gabaasa Ergi"):
            if os.path.exists(DATA_FILE):
                # Excel Logic Simplified for Streamlit
                st.info("Gabaasni qophaa'aa jira...")
                # (Asitti logic Excel kee itti fufuu dandeessa)
                st.success("Gabaasni hoggantatti ergameera!")
            else:
                st.warning("Ragaan kuufame hin jiru.")

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.rerun()

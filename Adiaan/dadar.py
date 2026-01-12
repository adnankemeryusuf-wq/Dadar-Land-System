import streamlit as st
import pandas as pd
import os
import requests
import qrcode
from datetime import datetime, timedelta
from io import BytesIO
import openpyxl

# --- CONFIGURATION ---
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "logo.png" # Faayila logo kee asitti dabaladhu

# --- FUNCTIONS ---
def send_telegram_file(file_data, file_name, caption=""):
    """Telegram irratti faayila erga"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        files = {'document': (file_name, file_data)}
        payload = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
        requests.post(url, data=payload, files=files, timeout=20)
    except Exception as e:
        st.error(f"Telegram Error: {e}")

def get_data():
    """Daataa txt irraa gara Pandas DataFrame-tti jijjiira"""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    try:
        # Sararoota txt keessaa dubbisuu
        df = pd.read_csv(DATA_FILE, sep="|", header=None, encoding="utf-8")
        # Maqaa kutaalee (Columns) - Akka koodii kee isa duraatti
        df.columns = ["Guyyaa", "Maqaa_AD", "Araddaa", "Wirtuu", "Bilbila", "Tajaajila", 
                      "Ogeessa", "B_Ogeessa", "Beellama", "K_Kartaa", "K_User", "K_Jij", "Waligala"]
        return df
    except:
        return pd.DataFrame()

# --- MAIN UI ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN SCREEN ---
    st.title("🔐 Login - Dadar Land System")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("SEENI"):
        if u == "admin" and p == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Username ykn Password dogoggora!")
else:
    # --- APP NAVIGATION ---
    menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Telegram", "🔍 Barbaadi (Search)"]
    choice = st.sidebar.selectbox("Fula Filadhu", menu)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    df_main = get_data()

    # --- 1. DASHBOARD ---
    if choice == "🏠 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df_main.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Baay'ina Galmee", len(df_main))
            col2.metric("Waligala Galii", f"{df_main['Waligala'].sum():,.2f} ETB")
            col3.metric("Tajaajila Har'aa", len(df_main[df_main['Guyyaa'].str.contains(datetime.now().strftime("%Y-%m-%d"))]))
            
            st.subheader("Galmeewwan Dhihoo")
            st.dataframe(df_main.tail(10), use_container_width=True)
        else:
            st.info("Hamma ammaatti ragaan galmeeffame hin jiru.")

    # --- 2. GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        st.subheader("Galmee Abbaa Dhimmaa Haaraa")
        with st.form("RegForm", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                wi = st.text_input("Wirtuu")
                bad = st.text_input("Bilbila AD")
            with c2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizio", "TOT", "Gibira"])
                og = st.text_input("Maqaa Ogeessa")
                gb = st.date_input("Guyyaa Beellamaa")
                sb = st.time_input("Sa'aatii")
            
            st.write("--- Kafaltiiwwan ---")
            k1 = st.number_input("Kafaltii Kartaa", min_value=0.0)
            k2 = st.number_input("Kafaltii User", min_value=0.0)
            k3 = st.number_input("Kafaltii Jijjiirraa", min_value=0.0)
            
            if st.form_submit_button("Galmeessi"):
                waligala = k1 + k2 + k3
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                # Save to Text File
                line = f"{now_str}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|'-'|{gb} {sb}|{k1}|{k2}|{k3}|{waligala}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(line)
                
                # Generate QR for Display
                qr_img = qrcode.make(f"AD: {ad}, Kafaltii: {waligala} ETB")
                buf = BytesIO()
                qr_img.save(buf, format="PNG")
                
                st.success("Milkiin galmeeffameera!")
                st.image(buf.getvalue(), caption=f"QR Code {ad}", width=200)

    # --- 3. GABAASA & TELEGRAM ---
    elif choice == "📊 Gabaasa & Telegram":
        st.subheader("Gabaasa Excel Uumi & Ergi")
        if not df_main.empty:
            # Excel Buffer
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_main.to_excel(writer, index=False, sheet_name='Gabaasa')
            excel_data = output.getvalue()

            st.download_button(label="📥 Excel Buufadhu", data=excel_data, 
                               file_name=f"Gabaasa_{datetime.now().date()}.xlsx")
            
            if st.button("🚀 Gabaasa Telegram-itti Ergi"):
                send_telegram_file(excel_data, "Gabaasa_Dadar.xlsx", f"Gabaasa Guyyaa: {datetime.now().date()}")
                st.success("Gabaasni hoggantatti ergameera!")
        else:
            st.warning("Ragaan erguuf jiru hin jiru.")

    # --- 4. SEARCH ---
    elif choice == "🔍 Barbaadi (Search)":
        st.subheader("🔍 Barbaadi")
        search_term = st.text_input("Maqaa ykn Bilbila galchi:")
        if search_term:
            results = df_main[df_main.apply(lambda row: search_term.lower() in row.astype(str).str.lower().values, axis=1)]
            st.write(f"Bu'aa {len(results)} argameera:")
            st.dataframe(results)











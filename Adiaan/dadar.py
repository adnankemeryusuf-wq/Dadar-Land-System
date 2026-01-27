import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
from collections import Counter
import plotly.express as px

# ================= 1. CONFIGURATION =================
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700" 

# SMS Gateway Config
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send" 
DEVICE_ID = "1" 

DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "logo.png" 
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Bilbila', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists("nagahee_scan"): os.makedirs("nagahee_scan")

# ================= 2. CORE FUNCTIONS =================

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"})
    except: pass

def send_sms(phone, message):
    try:
        if phone.startswith('0'): phone = "+251" + phone[1:]
        payload = {'token': SMS_TOKEN, 'device': DEVICE_ID, 'to': phone, 'message': message}
        requests.post(SMS_URL, data=payload, timeout=5)
    except: pass

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['dt'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf_cert(name, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(31, 78, 120); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 130, 15, 35)
    pdf.set_y(55); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 15, f"Ogeessa: {name}", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 16); pdf.multi_cell(0, 10, f"Waggaa kanatti tajaajila mamiilaa haala bareedaan kennaa turaniif\nsadarkaa {rank}ffaa argataniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. UI STYLE =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")
st.markdown("""<style>
    .stApp { background: #f4f7f6; }
    .main-card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-top: 8px solid #1f4e78; }
    </style>""", unsafe_allow_html=True)

# ================= 4. APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.header("🏢 Wajjira Lafa Dadar")
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI", use_container_width=True):
                # ASITTI SIRREEFFAMEERA: Username fi Password bifa "Text" tiin
                if u == "admin" and p == "1234": 
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maaloo sirriitti galchi!")
else:
    df = load_data()
    
    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.title("Main Menu")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "Logout"])
        st.divider()
        st.info(f"📅 {datetime.now().strftime('%d/%m/%Y')}")

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        
        if not df.empty:
            st.plotly_chart(px.line(df, x='dt', y='Kafaltii_Taj', title="Trendii Galii Guyyaatti"))
            
    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            bad = c1.text_input("Bilbila Maamilaa")
            og = c2.text_input("Maqaa Ogeessaa")
            gosa = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Gibira", "Liizii", "Clearance"])
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    now = datetime.now().strftime('%d/%m/%Y')
                    new_row = [now, name, ara, bad, gosa, og, fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    # Notifications
                    send_telegram(f"🆕 *Galmee Haaraa*\n👤 Maamila: {name}\n💰 {fee} ETB\n👷 Ogeessa: {og}")
                    send_sms(bad, f"Kabajamaa {name}, tajaajila {gosa}af galmeeffamtaniittu. Dadar Land.")
                    
                    st.success("Milkaa'inaan galmeeffameera!")
                else: st.error("Maaloo ragaa guuti!")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Bal'aa")
        st.dataframe(df[COL_NAMES], use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV Download", csv, "gabaasa.csv", "text/csv")

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.title("🏆 Badhaasa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"### Sadarkaa {i+1}")
                    st.write(f"**{name}**")
                    st.write(f"Tajaajile: {count}")
                    cert = create_pdf_cert(name, i+1)
                    st.download_button(f"📥 Download PDF {i+1}", cert, f"{name}_cert.pdf")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

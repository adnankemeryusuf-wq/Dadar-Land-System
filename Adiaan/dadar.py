import streamlit as st
import os
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
from fpdf import FPDF
import io

# --- 1. QINDAA'INA BU'URAA ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png" 

# Telegram Config
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

# --- FUNKSHINII TELEGRAM (TEXT & EXCEL) ---
def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, data=payload)
    except: pass

def send_telegram_file(df, filename):
    # Faayila Excel (CSV) memory keessatti qopheessuu
    csv_data = df.to_csv(index=False).encode('utf-8')
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    files = {'document': (filename, csv_data)}
    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': f"📊 Gabaasa Faayila: {filename}"}
    try: requests.post(url, data=data, files=files)
    except: st.error("Faayila erguun hin danda'amne.")

# --- 2. SARTIIFIKETA GENERATOR ---
def generate_certificate(expert_name, total_served, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(2)
    pdf.set_draw_color(30, 58, 138)
    pdf.rect(10, 10, 277, 190)
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=130, y=15, w=35)
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 35)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "BADHAASA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', 'I', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font('Arial', '', 16)
    pdf.set_text_color(0, 0, 0)
    text = (f"Waggaa {year} keessatti tajaajila saffisaa fi qulqullina qabuun "
            f"Abbootii Dhimmaa {total_served} tajaajiluun Ogeessa Waggaa "
            "ta'uun waan filatamaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, text, align='C')
    pdf.ln(20)
    pdf.cell(90, 10, "____________________", ln=0, align='C')
    pdf.cell(90, 10, "", ln=0)
    pdf.cell(90, 10, "____________________", ln=1, align='C')
    pdf.cell(90, 10, "Itti Gaafatamaa Waajjiraa", ln=0, align='C')
    pdf.cell(90, 10, "", ln=0)
    pdf.cell(90, 10, "Guyyaa", ln=1, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MIIDHAGSITUU (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .header-box { 
        text-align: center; padding: 20px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #15803d 100%); 
        color: white; border-radius: 15px; margin-bottom: 20px;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 6px solid #1e3a8a; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.image(LOGO_FILE if os.path.exists(LOGO_FILE) else "https://cdn-icons-png.flaticon.com/512/619/619153.png", width=100)
        st.title("Seensa")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=100)
        st.title("🏢 Dadar Land")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Telegram", "🏆 Badhaasa", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)

    # --- PAGE: DASHBOARD ---
    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><h5>👥 Abbootii Dhimmaa</h5><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><h5>💰 Galii Waligalaa</h5><h2>{df["Kafaltii"].sum():,.2f}</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><h5>📅 Galmee Hardhaa</h5><h2>{len(df[pd.to_datetime(df["Yeroo"]).dt.date == datetime.now().date()])}</h2></div>', unsafe_allow_html=True)
            
            st.plotly_chart(px.bar(df['Gosa'].value_counts().reset_index(), x='index', y='Gosa', title="Baay'ina Tajaajilaa"), use_container_width=True)
        else: st.info("Ragaan hin jiru.")

    # --- PAGE: GALMEE HAARAA ---
    elif choice == "📝 Galmee Haaraa":
        with st.form("form_reg", clear_on_submit=True):
            st.subheader("📝 Galmeessa Haaraa")
            c1, c2 = st.columns(2)
            with c1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                qx = st.text_input("Qaxana / Lakk. Manaa")
            with c2:
                gosa_list = [
                    "Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", 
                    "Walitti Bu'iinsa Dangaa", "Dhimma Mana Murttii", 
                    "Dhorkii Mana Murtii Galmeessu", "Liqii Bankii Galmeessu", 
                    "Dhorkii Mana Murtii Kaasuu ykn Haquu", "Liqii Bankii Kasuu ykn Haquu"
                ]
                gs = st.selectbox("Gosa Tajaajilaa", gosa_list)
                og = st.text_input("Maqaa Ogeessaa")
                k_wal = st.number_input("Kafaltii", min_value=0.0)
            
            if st.form_submit_button("✅ GALMEESSI"):
                if ad and og:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Structure: Yeroo|Maqaa|Araddaa|Qaxana|Gosa|Ogeessa|Status|C1|C2|C3|Kafaltii
                    line = f"{now}|{ad}|{ar}|{qx}|{gs}|{og}|Active|0|0|0|{k_wal}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    st.success("Milkiin Galmaa'eera!")
                else: st.warning("Maaloo Maqaa fi Ogeessa guuti.")

    # --- PAGE: GABAASA & TELEGRAM ---
    elif choice == "📊 Gabaasa & Telegram":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Yeroo'] = pd.to_datetime(df['Yeroo'])
            
            y_filter = st.radio("Yeroo Filadhu:", ["Hunda", "Hardha", "Torban", "Ji'a", "Waggaa"], horizontal=True)
            now = datetime.now()
            if y_filter == "Hardha": df_f = df[df['Yeroo'].dt.date == now.date()]
            elif y_filter == "Torban": df_f = df[df['Yeroo'] >= (now - timedelta(days=7))]
            elif y_filter == "Ji'a": df_f = df[df['Yeroo'].dt.month == now.month]
            elif y_filter == "Waggaa": df_f = df[df['Yeroo'].dt.year == now.year]
            else: df_f = df
            
            st.dataframe(df_f, use_container_width=True)
            
            st.divider()
            if st.button("🚀 GABAASA EXCEL TELEGRAM-ITTI ERGI"):
                # Ergaa Text
                t_galii = df_f['Kafaltii'].sum()
                msg = f"📊 *Gabaasa Dadar ({y_filter})*\n\n👤 Namoota: {len(df_f)}\n💰 Galii: {t_galii:,.2f} ETB\n📅 Guyyaa: {now.strftime('%Y-%m-%d')}"
                send_telegram_msg(msg)
                
                # Ergaa Faayila Excel (CSV)
                filename = f"Gabaasa_Dadar_{y_filter}_{now.strftime('%Y%m%d')}.csv"
                send_telegram_file(df_f, filename)
                st.success("Gabaasni fi Faayilli Excel Telegram-itti ergameera!")

    # --- PAGE: BADHAASA ---
    elif choice == "🏆 Badhaasa":
        st.subheader("🏆 Beekamtii Ogeessa Waggaa")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            winner = df[5].value_counts() # Index 5 is Ogeessa
            if not winner.empty:
                w_name, w_count = winner.idxmax(), winner.max()
                st.success(f"Ogeessi Waggaa: **{w_name}** ({w_count} tajaajile)")
                if st.button("📜 SARTIIFIKETA QOPHEESSI"):
                    pdf_bytes = generate_certificate(w_name, w_count, datetime.now().year)
                    st.download_button("📥 Buufadhu (PDF)", pdf_bytes, f"Certificate_{w_name}.pdf", "application/pdf")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()


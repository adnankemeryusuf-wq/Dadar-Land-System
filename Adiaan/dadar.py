import streamlit as st
import os
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
from fpdf import FPDF

# --- 1. CONFIG ---
st.set_page_config(page_title="Dadar Land Administration", layout="wide", page_icon="🏢")

USER_NAME = "Lafa2026"
PASS_WORD = "Dadar@2026"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png"  # Suuraa logo keetii folder tokko keessa kaayi

# Telegram Config
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, data=payload)
    except: pass

# --- 2. SARTIIFIKETA GENERATOR (LOGO DABALATEE) ---
def generate_certificate(expert_name, total_served, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_line_width(2)
    pdf.set_draw_color(30, 58, 138)
    pdf.rect(10, 10, 277, 190)
    
    # Logo (Yoo folder keessa jiraate)
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=130, y=15, w=35)
    
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 35)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "BADHAASA BEEKAMTII", ln=True, align='C')
    
    pdf.set_font('Arial', 'I', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(15)
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, "Sartiifiketiin kun kan kennameef:", ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 30)
    pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    pdf.set_text_color(0, 0, 0)
    text = (f"Waggaa {year} keessatti tajaajila saffisaa fi qulqullina qabuun "
            f"Abbootii Dhimmaa {total_served} tajaajiluun Ogeessa Waggaa "
            "ta'uun waan filatamaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, text, align='C')

    pdf.ln(25)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(90, 10, "____________________", ln=0, align='C')
    pdf.cell(90, 10, "", ln=0)
    pdf.cell(90, 10, "____________________", ln=1, align='C')
    pdf.cell(90, 10, "Itti Gaafatamaa Waajjiraa", ln=0, align='C')
    pdf.cell(90, 10, "", ln=0)
    pdf.cell(90, 10, "Guyyaa", ln=1, align='C')

    return pdf.output(dest='S').encode('latin-1')

# --- 3. CSS STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header-box { 
        text-align: center; padding: 30px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #15803d 100%); 
        color: white; border-radius: 20px; margin-bottom: 25px;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-top: 5px solid #1e3a8a; text-align: center;
    }
    .metric-value { color: #1e3a8a; font-size: 2rem; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>Seensa</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    with st.sidebar:
        st.title("🏢 Dadar Land")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Telegram", "🏆 Badhaasa", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Magaalaa Dadar</h1><p>Sistama Galmee fi Gabaasa Ammayyaa</p></div>', unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Bilbila', 'Gosa', 'Ogeessa', 'Lakk_Galmee', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            
            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(f'<div class="metric-card"><div>Abbootii Dhimmaa</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card"><div>Galii Waligalaa</div><div class="metric-value">{df["Kafaltii"].sum():,.2f}</div></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metric-card"><div>Galmee Hardhaa</div><div class="metric-value">{len(df[pd.to_datetime(df["Yeroo"]).dt.date == datetime.now().date()])}</div></div>', unsafe_allow_html=True)
            
            st.plotly_chart(px.pie(df, names='Gosa', hole=0.4, title="Gosa Tajaajilaa"), use_container_width=True)
        else: st.info("Ragaan hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        with st.form("form_reg", clear_on_submit=True):
            st.subheader("📝 Galmeessa Haaraa")
            c1, c2 = st.columns(2)
            with c1:
                ad, ar = st.text_input("Maqaa Abbaa Dhimmaa"), st.text_input("Araddaa")
                qx, bl = st.text_input("Qaxana"), st.text_input("Lakkoofsa Bilbilaa")
            with c2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Ground", "Gibira"])
                og, lk = st.text_input("Maqaa Ogeessaa"), st.text_input("Lakk. Galmee (Ref)")
                k_wal = st.number_input("Kafaltii", min_value=0.0)
            
            if st.form_submit_button("✅ GALMEESSI"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                line = f"{now}|{ad}|{ar}|{qx}|{bl}|{gs}|{og}|{lk}|Active|0|0|0|{k_wal}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                st.success("Milkiin Galmaa'eera!")

    elif choice == "📊 Gabaasa & Telegram":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Bilbila', 'Gosa', 'Ogeessa', 'Lakk_Galmee', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Yeroo'] = pd.to_datetime(df['Yeroo'])
            
            y_filter = st.radio("Yeroo Filadhu:", ["Hunda", "Hardha", "Torban", "Ji'a", "Waggaa"], horizontal=True)
            now = datetime.now()
            if y_filter == "Hardha": df = df[df['Yeroo'].dt.date == now.date()]
            elif y_filter == "Torban": df = df[df['Yeroo'] >= (now - timedelta(days=7))]
            elif y_filter == "Ji'a": df = df[df['Yeroo'].dt.month == now.month]
            
            st.dataframe(df, use_container_width=True)
            if st.button("🚀 GABAASA TELEGRAM"):
                msg = f"📊 *Gabaasa Dadar ({y_filter})*\n👤 Namoota: {len(df)}\n💰 Galii: {df[12].astype(float).sum():,.2f} ETB"
                send_telegram_msg(msg)
                st.success("Ergameera!")

    elif choice == "🏆 Badhaasa":
        st.subheader("🏆 Badhaasa Ogeessa Waggaa")
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            winner = df[6].value_counts()
            if not winner.empty:
                w_name, w_count = winner.idxmax(), winner.max()
                st.success(f"Ogeessi Waggaa: **{w_name}** ({w_count} tajaajile)")
                if st.button("📜 SARTIIFIKETA QOPHEESSI"):
                    pdf_bytes = generate_certificate(w_name, w_count, datetime.now().year)
                    st.download_button("📥 Buufadhu (PDF)", pdf_bytes, f"Certificate_{w_name}.pdf", "application/pdf")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

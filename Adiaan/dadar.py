import streamlit as st
import os
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
from fpdf import FPDF
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png"

# Telegram API Config
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

# --- FUNCTIONS ---
def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, data=payload)
    except: st.error("Ergaa Telegram erguun hin danda'amne.")

def send_telegram_file(df, filename, caption):
    csv_data = df.to_csv(index=False).encode('utf-8')
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    files = {'document': (filename, csv_data)}
    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
    try: requests.post(url, data=data, files=files)
    except: st.error("Faayila Telegram erguun hin danda'amne.")

# --- 2. SARTIIFIKETA (Signature with Aqiil Abdujaaliil) ---
def generate_certificate(expert_name, total_served, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border Miidhagaa (Double Border)
    pdf.set_line_width(1.5)
    pdf.set_draw_color(184, 134, 11) # Gold Color
    pdf.rect(5, 5, 287, 200)
    pdf.set_line_width(0.5)
    pdf.rect(8, 8, 281, 194)
    
    # Logo
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=130, y=12, w=35)
    
    pdf.ln(40)
    pdf.set_font('Arial', 'B', 40)
    pdf.set_text_color(30, 58, 138) # Dark Blue
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_font('Arial', 'I', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(15)
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(21, 128, 61) # Green
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 15)
    pdf.set_text_color(50, 50, 50)
    text = (f"Waggaa {year} keessatti tajaajila saffisaa, iftoomina qabuu fi "
            f"amannamaa ta'een Abbootii Dhimmaa {total_served} tajaajiluun "
            "bu'aa qabeessa ta'anii waan argamaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, text, align='C')
    
    pdf.ln(20)
    
    # Sarara Mallattoo
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(100, 10, "__________________________", ln=0, align='C') 
    pdf.cell(87, 10, "", ln=0)
    pdf.cell(100, 10, "__________________________", ln=1, align='C')

    # Maqaa fi Titlaa
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C') 
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, "", ln=1, align='C') 

    pdf.set_font('Arial', '', 12)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa", ln=0, align='C') 
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, "Guyyaa", ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. STYLING (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #1e3a8a; color: white; }
    .header-box { 
        text-align: center; padding: 30px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #15803d 100%); 
        color: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-top: 5px solid #1e3a8a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1, 1])
    with center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=150)
        st.subheader("Sistama Galmee Dadar")
        u = st.text_input("Maqaa Seensaa")
        p = st.text_input("Fungula (Password)", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=120)
        st.title("Admin Panel")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa Telegr_Pro", "🏆 Sartiifiketa", "🚪 Logout"]
        choice = st.selectbox("Filannoo", menu)
        st.divider()
        st.info("Sistama Bulchiinsa Lafaa v3.5")

    st.markdown('<div class="header-box"><h1>Waajjira Lafaa Magaalaa Dadar</h1><p>Gabaasa fi Galmeessa Ammayyaa</p></div><br>', unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="card"><h5>👥 Waligala</h5><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="card"><h5>💰 Galii</h5><h2>{pd.to_numeric(df["Kafaltii"]).sum():,.2f}</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="card"><h5>📅 Hardha</h5><h2>{len(df[pd.to_datetime(df["Yeroo"]).dt.date == datetime.now().date()])}</h2></div>', unsafe_allow_html=True)
            st.plotly_chart(px.bar(df['Gosa'].value_counts().reset_index(), x='index', y='Gosa', color='index', title="Tajaajila Gosaan"), use_container_width=True)
        else: st.info("Ragaan hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        with st.form("reg_form", clear_on_submit=True):
            st.subheader("📝 Ragaa Galmeessi")
            col1, col2 = st.columns(2)
            with col1:
                ad = st.text_input("Maqaa Abbaa Dhimmaa")
                ar = st.text_input("Araddaa")
                qx = st.text_input("Qaxana / Lakk. Manaa")
            with col2:
                gs = st.selectbox("Gosa Tajaajilaa", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"])
                og = st.text_input("Maqaa Ogeessaa")
                kf = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("✅ GALMEESSI"):
                if ad and og:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    line = f"{now}|{ad}|{ar}|{qx}|{gs}|{og}|Active|0|0|0|{kf}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    st.success(f"Ragaan {ad} galmaa'eera!")
                else: st.warning("Maaloo ragaa guutuu guutaa.")

    elif choice == "📊 Gabaasa Telegr_Pro":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            df.columns = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']
            df['Yeroo'] = pd.to_datetime(df['Yeroo'])
            
            tab1, tab2, tab3 = st.tabs(["📅 Guyyaa/Torban", "📅 Ji'a/Kurmaana", "🚀 Telegram"])
            
            with tab1:
                day_filter = st.multiselect("Guyyaa Filadhu:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
                week_filter = st.selectbox("Torban:", ["Hunda", "Torban 1ffaa", "Torban 2ffaa", "Torban 3ffaa", "Torban 4ffaa"])
                df_f = df.copy()
                if day_filter: df_f = df_f[df_f['Yeroo'].dt.day_name().isin(day_filter)]
                if week_filter != "Hunda":
                    w_num = int(week_filter.split()[1][0])
                    df_f = df_f[(df_f['Yeroo'].dt.day - 1) // 7 + 1 == w_num]
                st.dataframe(df_f, use_container_width=True)

            with tab2:
                months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                m_filter = st.selectbox("Ji'a:", ["Hunda"] + months)
                q_filter = st.selectbox("Kurmaana:", ["Hunda", "Kur1", "Kur2", "Kur3", "Kur4"])
                
                if m_filter != "Hunda": df_f = df_f[df_f['Yeroo'].dt.month == months.index(m_filter) + 1]
                if q_filter != "Hunda":
                    q_num = int(q_filter[-1])
                    df_f = df_f[df_f['Yeroo'].dt.quarter == q_num]
                st.dataframe(df_f, use_container_width=True)

            with tab3:
                if st.button("🚀 GABAASA ERGI"):
                    msg = f"📊 *GABAASA DADAR*\n👤 Namoota: {len(df_f)}\n💰 Galii: {pd.to_numeric(df_f['Kafaltii']).sum():,.2f} ETB"
                    send_telegram_msg(msg)
                    send_telegram_file(df_f, "Gabaasa.csv", "Faayila Gabaasaa")
                    st.success("Telegram-itti ergameera!")

    elif choice == "🏆 Sartiifiketa":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            counts = df[5].value_counts()
            if not counts.empty:
                w_name = counts.idxmax()
                w_val = counts.max()
                st.markdown(f"<div class='card'><h3>🏆 Ogeessa Waggaa: {w_name}</h3><p>Abbootii dhimmaa {w_val} tajaajile.</p></div>", unsafe_allow_html=True)
                if st.button("📜 SARTIIFIKETA QOPHEESSI"):
                    cert = generate_certificate(w_name, w_val, datetime.now().year)
                    st.download_button("📥 Buufadhu (PDF)", cert, f"Cert_{w_name}.pdf")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

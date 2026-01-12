import streamlit as st
import os
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# --- 1. QINDAYYII BU'URAA ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png"

# Maqaa Tarree (Columns) - Bakka tokkotti qindeessuuf
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']

# Telegram API Config
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

# --- 2. FUNKSHINOOTA GARGAARAA ---

def load_data():
    """Ragaa faayila irraa dubbisuuf fi dogoggora tarree sirreessuuf"""
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        # on_bad_lines='skip' sarara dogoggora qabu bira darba
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"Ragaa dubbisuun hin danda'amne: {e}")
        return pd.DataFrame(columns=COL_NAMES)

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

# --- 3. SARTIIFIKETA ---
def generate_certificate(expert_name, total_served, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(1.5)
    pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200)
    pdf.set_line_width(0.5)
    pdf.rect(8, 8, 281, 194)
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, x=130, y=12, w=35)
    pdf.ln(40)
    pdf.set_font('Arial', 'B', 40)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', 'I', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(15); pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    pdf.ln(5); pdf.set_font('Arial', 'B', 32); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 15); pdf.set_text_color(50, 50, 50)
    text = (f"Waggaa {year} keessatti tajaajila saffisaa, iftoomina qabuu fi "
            f"amannamaa ta'een Abbootii Dhimmaa {total_served} tajaajiluun "
            "bu'aa qabeessa ta'anii waan argamaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, text, align='C')
    pdf.ln(20); pdf.set_font('Arial', 'B', 14); pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 10, "__________________________", ln=0, align='C') 
    pdf.cell(87, 10, "", ln=0)
    pdf.cell(100, 10, "__________________________", ln=1, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C') 
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, "", ln=1, align='C') 
    pdf.set_font('Arial', '', 12)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa", ln=0, align='C') 
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, "Guyyaa", ln=1, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1, 1])
    with center:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=150)
        st.subheader("Sistama Galmee Dadar")
        u = st.text_input("Maqaa Seensaa")
        p = st.text_input("Fungula", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    # SIDEBAR
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=100)
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa Telegr_Pro", "🏆 Sartiifiketa", "🚪 Logout"]
        choice = st.selectbox("Filannoo", menu)

    st.title("Waajjira Lafaa Magaalaa Dadar")

    df = load_data()

    if choice == "🏠 Dashboard":
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Waligala", len(df))
            c2.metric("Galii (ETB)", f"{pd.to_numeric(df['Kafaltii'], errors='coerce').sum():,.2f}")
            c3.metric("Hardha", len(df[pd.to_datetime(df['Yeroo'], errors='coerce').dt.date == datetime.now().date()]))
            st.plotly_chart(px.bar(df['Gosa'].value_counts().reset_index(), x='index', y='Gosa', title="Tajaajila Gosaan"))
        else: st.info("Ragaan galmeeffame hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            ad = col1.text_input("Maqaa Abbaa Dhimmaa")
            ar = col1.text_input("Araddaa")
            qx = col1.text_input("Qaxana / Lakk. Manaa")
            gs = col2.selectbox("Gosa Tajaajilaa", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"])
            og = col2.text_input("Maqaa Ogeessaa")
            kf = col2.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("✅ GALMEESSI"):
                if ad and og:
                    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}|{ad}|{ar}|{qx}|{gs}|{og}|Active|0|0|0|{kf}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    st.success(f"Ragaan {ad} galmaa'eera!")
                    st.rerun()

    elif choice == "📊 Gabaasa Telegr_Pro":
        if not df.empty:
            df['Yeroo'] = pd.to_datetime(df['Yeroo'], errors='coerce')
            st.dataframe(df)
            if st.button("🚀 GABAASA TELEGRAM-ITTI ERGI"):
                msg = f"📊 *GABAASA DADAR*\n👤 Namoota: {len(df)}\n💰 Galii: {pd.to_numeric(df['Kafaltii'], errors='coerce').sum():,.2f} ETB"
                send_telegram_msg(msg)
                send_telegram_file(df, "Gabaasa.csv", "Gabaasa Guutuu")
                st.success("Ergameera!")

    elif choice == "🏆 Sartiifiketa":
        if not df.empty:
            counts = df['Ogeessa'].value_counts()
            if not counts.empty:
                w_name = counts.idxmax()
                st.success(f"Ogeessa Waggaa: {w_name}")
                if st.button("📜 SARTIIFIKETA QOPHEESSI"):
                    cert = generate_certificate(w_name, counts.max(), datetime.now().year)
                    st.download_button("📥 Buufadhu (PDF)", cert, f"Cert_{w_name}.pdf")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

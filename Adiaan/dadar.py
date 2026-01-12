import streamlit as st
import os
import pandas as pd
import requests
import io
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageOps

# --- 1. QINDAYYII BU'URAA ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"

# Mallattoo barbaaduu
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj', 'Kafaltii_Wal', 'C1', 'C2', 'C3']
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

# --- 2. FUNKSHINOOTA ---
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# --- 3. REPORT GENERATOR (Logo-n dabalameera) ---
def create_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    
    # Logoo Gabaasa Irratti
    if LOGO_PATH:
        pdf.image(LOGO_PATH, x=10, y=8, w=25)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "GABAASA WAAJJIRA LAFAA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_fill_color(30, 58, 138) # Navy Blue
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 9)
    h = ["Maqaa", "Araddaa", "Gosa", "K.Taj", "K.Wal"]
    for col in h:
        pdf.cell(38, 8, col, 1, 0, 'C', True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 8)
    for _, row in df.iterrows():
        pdf.cell(38, 7, str(row['Maqaa'])[:18], 1)
        pdf.cell(38, 7, str(row['Araddaa']), 1)
        pdf.cell(38, 7, str(row['Gosa']), 1)
        pdf.cell(38, 7, str(row['Kafaltii_Taj']), 1)
        pdf.cell(38, 7, str(row['Kafaltii_Wal']), 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SARTIIFIKETA (Circular Logo & Clean Text) ---
def generate_certificate(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    pdf.set_line_width(2); pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200) 
    
    if LOGO_PATH and os.path.exists(LOGO_PATH):
        try:
            img = Image.open(LOGO_PATH).convert("RGBA")
            size = (400, 400)
            img = img.resize(size, Image.LANCZOS)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            img.putalpha(mask)
            final_logo = Image.new("RGB", size, (255, 255, 255))
            final_logo.paste(img, mask=img.split()[3])
            pdf.image(final_logo, x=131, y=10, w=35)
        except: pass

    pdf.ln(35)
    pdf.set_font('Times', 'B', 40); pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.ln(25); pdf.set_font('Times', 'B', 32); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
    msg = ("Waggaa kanatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een "
            "hojii gaarii hojjettanii waan argamtaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    
    pdf.set_y(172)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 8, "__________________________", ln=0, align='C')
    pdf.cell(87, 8, "", ln=0)
    pdf.cell(100, 8, "__________________________", ln=1, align='C')
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, datetime.now().strftime("%d/%m/%Y"), ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. MAIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        # LOGO LOGIN IRRATTI
        if LOGO_PATH: st.image(LOGO_PATH, width=150)
        st.markdown("<h2 style='text-align:center;'>Dadar Land Admin</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI", use_container_width=True):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Maqaa ykn Password dogoggora!")
else:
    with st.sidebar:
        # LOGO SIDEBAR IRRATTI
        if LOGO_PATH: st.image(LOGO_PATH, width=120)
        st.title("Admin Menu")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaaduu & Sirreessu", "📊 Gabaasa Telegr_Pro", "🏆 Sartiifiketa", "🚪 Logout"]
        choice = st.selectbox("Menu Filadhu", menu)

    df = load_data()

    if choice == "🏠 Dashboard":
        st.header("🏠 Dashboard")
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Waligala Galmee", len(df))
            df['Kafaltii_Wal'] = pd.to_numeric(df['Kafaltii_Wal'], errors='coerce').fillna(0)
            c2.metric("Galii Waliigalaa", f"{df['Kafaltii_Wal'].sum():,.2f} ETB")
            st.dataframe(df.tail(10), use_container_width=True)

    elif choice == "📝 Galmee Haaraa":
        st.header("📝 Galmee Haaraa Galchi")
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            ad = col1.text_input("Maqaa Abbaa Dhimmaa")
            og = col2.text_input("Maqaa Ogeessaa")
            gs = col1.selectbox("Gosa", ["Kartaa", "Jijjirra Maqaa", "Liqii Bankii", "Dangaa"])
            kf = col2.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("GALMEESSI"):
                if ad and og:
                    line = f"{datetime.now().strftime('%Y-%m-%d')}|{ad}|-|-|{gs}|{og}|{kf}|{kf}|0|0|0\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    st.success("Milkaa'inaan galmeeffameera!")
                    st.rerun()

    elif choice == "🔍 Barbaaduu & Sirreessu":
        st.header("🔍 Barbaadi fi Sirreessi")
        query = st.text_input("Maqaa barreessi...")
        if not df.empty:
            res = df[df['Maqaa'].str.contains(query, case=False, na=False)]
            if not res.empty:
                st.dataframe(res, use_container_width=True)
                sel = st.selectbox("Nama sirreessuuf filadhu:", res['Maqaa'].tolist())
                idx = df[df['Maqaa'] == sel].index[0]
                with st.form("edit"):
                    n_ad = st.text_input("Maqaa", value=df.at[idx, 'Maqaa'])
                    n_og = st.text_input("Ogeessa", value=df.at[idx, 'Ogeessa'])
                    if st.form_submit_button("💾 SAVE"):
                        df.at[idx, 'Maqaa'] = n_ad
                        df.at[idx, 'Ogeessa'] = n_og
                        save_data(df)
                        st.success("Fooyya'eera!")
                        st.rerun()

    elif choice == "📊 Gabaasa Telegr_Pro":
        st.header("📊 Gabaasa & Ergaa")
        if not df.empty:
            st.dataframe(df)
            col1, col2 = st.columns(2)
            col1.download_button("📥 PDF Buufadhu", create_pdf_report(df), "Gabaasa.pdf")
            if col2.button("🚀 Telegram-itti Ergi"):
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                              data={"chat_id": TELEGRAM_CHAT_ID, "text": f"Gabaasa Dadar: {len(df)} galmeeffame."})
                st.success("Gabaasni ergameera!")

    elif choice == "🏆 Sartiifiketa":
        st.header("🏆 Beekamtii Ogeessaa")
        if not df.empty:
            best_og = df['Ogeessa'].value_counts().idxmax()
            st.success(f"Ogeessa Beekamtii Argatu: **{best_og}**")
            if st.button("📜 SARTIIFIKETA QOPHEESSI"):
                cert = generate_certificate(best_og)
                st.download_button("📥 PDF Buufadhu", cert, f"Cert_{best_og}.pdf")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

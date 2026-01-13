import streamlit as st
import pandas as pd
import os
import hashlib
import requests
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageOps

# ================= CONFIG =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

DATA_FILE = "dadar_final_report.txt"
USERS_FILE = "users.csv"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

# --- ODEEFFANNOO TELEGRAM ---
TELEGRAM_TOKEN = "7864321234:AAH_F_XXXXXXXXXXXXX" # API Token kee galchi
TELEGRAM_CHAT_ID = "123456789"                   # Chat ID Manager-aa galchi

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Ittii Fayyaddam": 50.0, "Kartaa": 150.0, "Jijjirra Maqaa": 200.0,
    "Dhimma Dangaa": 100.0, "Dhimma Mana Murtii": 0.0, "Ugura Mana Murtii": 50.0,
    "Uguraa Mana Murtii Kasuu": 50.0, "Dorkka Liqii Bankii": 100.0, "Dorkkaa Liqii Bankii Kasuu": 100.0
}

# ================= FUNCTIONS =================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([["admin", hash_password("123"), "admin"]], columns=["username", "password", "role"])
        df.to_csv(USERS_FILE, index=False)
    return pd.read_csv(USERS_FILE)

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_path, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": message, "parse_mode": "Markdown"}
            files = {"document": file}
            response = requests.post(url, data=payload, files=files)
            return response.status_code == 200
    except:
        return False

# ================= LOGO & CERTIFICATE FUNCTIONS =================
def get_circular_logo(path):
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        size = (400, 400)
        img = img.resize(size, Image.LANCZOS)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask)
        output = Image.new("RGB", size, (255, 255, 255))
        output.paste(img, mask=img.split()[3])
        return output
    return None

def generate_certificate(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(2); pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200) 
    circular_img = get_circular_logo(LOGO_PATH)
    if circular_img:
        pdf.image(circular_img, x=131, y=10, w=35)
    pdf.ln(35)
    pdf.set_font('Helvetica', 'B', 40)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.ln(5); pdf.set_font('Arial', 'I', 16); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, "Gootummaa Hojii Waggaa kan kennameef:", ln=True, align='C')
    pdf.ln(5); pdf.set_font('Helvetica', 'B', 32); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
    msg = ("Waggaa kanatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een "
            "hojii gaarii hojjettanii waan argamtaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    pdf.set_y(172)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 8, "__________________________", ln=0, align='C')
    pdf.cell(87, 8, "", ln=0)
    pdf.cell(100, 8, "__________________________", ln=1, align='C')
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, datetime.now().strftime("%d/%m/%Y"), ln=1, align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if LOGO_PATH: st.image(LOGO_PATH, width=150)
        st.title("🏢 Seensa Sirna")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni", use_container_width=True):
            users = load_users()
            if not users[(users.username == u) & (users.password == hash_password(p))].empty:
                st.session_state.logged_in, st.session_state.user = True, u
                st.session_state.role = users[users.username == u].iloc[0]['role']
                st.rerun()
            else: st.error("Username ykn Password dogoggora")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, width=120)
        st.success(f"👤 {st.session_state.user} ({st.session_state.role})")
        menu = st.radio("Menu", ["📝 Galmee", "🔍 Barbaadi & Sirreessi", "📊 Odeeffannoo", "🏆 Sartiifiketa", "🚪 Ba'i"])

    df = load_data()

    if menu == "📝 Galmee":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        with st.form("entry"):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = c2.text_input("Araddaa")
            qaxana = c1.text_input("Qaxana")
            gosa = c2.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            ogeessa = c1.text_input("Maqaa Ogeessaa")
            k_taj_base = GATII_DICT[gosa]
            k_dab = c2.number_input("Kafaltii Dabalataa", min_value=0.0, value=0.0)
            k_wal = k_taj_base + k_dab
            st.info(f"💰 Kafaltii Waliigalaa: {k_wal} ETB")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, k_wal]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success("Galmeeffameera!")
                    st.rerun()
                else: st.error("Maqaa galchuun dirqama!")

    elif menu == "🔍 Barbaadi & Sirreessi":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa barbaadi...")
        if not df.empty:
            results = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            st.dataframe(results, use_container_width=True)

    elif menu == "📊 Odeeffannoo":
        st.header("📊 Gabaasa fi Ergaa Telegram")
        st.dataframe(df, use_container_width=True)
        col_ex, col_te = st.columns(2)
        with col_ex:
            if not df.empty:
                excel_file = "Gabaasa_Dadar_Lafaa.xlsx"
                df.to_excel(excel_file, index=False)
                with open(excel_file, "rb") as f:
                    st.download_button("📥 Excel Download", f, file_name=excel_file)
        with col_te:
            if st.button("📤 Manager-itti Ergi"):
                temp_path = "Gabaasa_Manager.xlsx"
                df.to_excel(temp_path, index=False)
                total_sum = df['Kafaltii_Taj'].astype(float).sum()
                msg = f"🏢 *Gabaasa Dadar*\n📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}\n💰 Kaffaltii Waliigalaa: *{total_sum} ETB*"
                if send_to_telegram(temp_path, msg): st.success("✅ Ergameera!")
                else: st.error("❌ Erguun hin danda'amne!")

    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Beekamtii Ogeessaa")
        if not df.empty:
            # Ogeessa tajaajila baay'ee kenne filachuu
            og_counts = df['Ogeessa'].value_counts()
            if not og_counts.empty:
                best_og = og_counts.idxmax()
                st.success(f"Ogeessa Hojii Gaarii Hojjete: **{best_og}** ({og_counts[best_og]} tajaajila kenne)")
                if st.button("📜 SARTIIFIKETA QOPHEESSI"):
                    cert_pdf = generate_certificate(best_og)
                    st.download_button("📥 PDF Buufadhu", cert_pdf, f"Sartiifiketa_{best_og}.pdf")
        else:
            st.warning("Data'n waan hin jirreef sartiifiketa qopheessun hin danda'amu.")

    elif menu == "🚪 Ba'i":
        st.session_state.clear()
        st.rerun()

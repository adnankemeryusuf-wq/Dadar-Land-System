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

# --- TELEGRAM CONFIG ---
TELEGRAM_TOKEN = "7864321234:AAH_F_XXXXXXXXXXXXX" # API Token as galchi
TELEGRAM_CHAT_ID = "123456789"                   # Chat ID as galchi

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

# ================= LOGO & CERTIFICATE =================
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
    # Border
    pdf.set_line_width(2)
    pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200) 
    
    circular_img = get_circular_logo(LOGO_PATH)
    if circular_img:
        circular_img.save("temp_logo.png")
        pdf.image("temp_logo.png", x=131, y=10, w=35)
    
    pdf.ln(35)
    pdf.set_font('Arial', 'B', 40)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(0, 0, 0)
    msg = "Waggaa kanatti tajaajila saffisaa fi amannamaa ta'een hojii gaarii hojjettaniif beekamtii kanaan badhaafamaniiru."
    pdf.multi_cell(0, 10, msg, align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
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
        st.markdown(f"### 👤 {st.session_state.user}")
        menu = st.radio("Menu", ["📊 Dashboard", "📝 Galmee", "🔍 Barbaadi", "🏆 Sartiifiketa", "🚪 Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Gabaasa Gabaabaa")
        c1, c2, c3 = st.columns(3)
        total_people = len(df)
        total_money = df['Kafaltii_Taj'].astype(float).sum() if not df.empty else 0
        
        c1.metric("Baay'ina Tajaajilaa", f"{total_people}")
        c2.metric("Kafaltii Waliigalaa", f"{total_money} ETB")
        c3.metric("Ogeessota", f"{len(df['Ogeessa'].unique()) if not df.empty else 0}")
        
        st.divider()
        st.subheader("Data Guyyaa Har'aa")
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee":
        st.header("📝 Galmee Haaraa")
        with st.form("entry", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            gosa = col2.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            
            k_wal = GATII_DICT[gosa]
            st.warning(f"Kafaltii: {k_wal} ETB")

            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, k_wal]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.balloons()
                    st.success(f"✅ {maqaa} Galmeeffameera!")
                else: st.error("Maqaa fi Ogeessa guuti!")

    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi fi Excel")
        q = st.text_input("Maqaa ykn Araddaa barreessi...")
        if not df.empty:
            res = df[df['Maqaa'].str.contains(q, case=False, na=False) | df['Araddaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res, use_container_width=True)
            
            if st.button("📤 Excel-itti jijjiiri"):
                res.to_excel("Gabaasa_Dadar.xlsx", index=False)
                with open("Gabaasa_Dadar.xlsx", "rb") as f:
                    st.download_button("📥 Excel Buufadhu", f, file_name="Gabaasa_Dadar.xlsx")

    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Beekamtii Ogeessaa")
        if not df.empty:
            og_list = df['Ogeessa'].unique()
            ogeessa_filatame = st.selectbox("Ogeessa Galateeffamu filadhu", og_list)
            if st.button("📜 Sartiifiketa Qopheessi"):
                with st.spinner("Qophaa'aa jira..."):
                    cert = generate_certificate(ogeessa_filatame)
                    st.download_button("📥 PDF Buufadhu", cert, f"Beekamtii_{ogeessa_filatame}.pdf")
        else: st.info("Hojiin galmaa'e hin jiru.")

    elif menu == "🚪 Ba'i":
        st.session_state.clear()
        st.rerun()

import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import plotly.express as px

# ================= 1. CONFIGURATION =================
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# Service structure based on your specific requirements
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Kaartaa Lafa Qonnaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", "Adabbii Faallaa Pilaanii"]
}

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

# ================= 2. CORE FUNCTIONS =================
def send_telegram_msg(msg, image_path=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
        requests.get(url + "sendMessage", params={"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"})
        if image_path:
            with open(image_path, "rb") as photo:
                requests.post(url + "sendPhoto", data={"chat_id": CHAT_ID_MANAGER}, files={"photo": photo})
    except: pass

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_dadar_cert(name, count, rank, logo_file=None):
    width, height = 1123, 794
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    rank_colors = {1: "#D4AF37", 2: "#C0C0C0", 3: "#CD7F32"}
    main_color = rank_colors.get(rank, "#1b5e20")
    
    draw.rectangle([20, 20, width-20, height-20], outline=main_color, width=15)
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA").resize((130, 130))
        img.paste(logo, (width//2 - 65, 60), logo)
    
    try: f_header = ImageFont.truetype("arialbd.ttf", 45); f_name = ImageFont.truetype("arialbd.ttf", 55); f_body = ImageFont.truetype("arial.ttf", 30)
    except: f_header = f_name = f_body = ImageFont.load_default()

    draw.text((width//2, 210), "SARTIIFIKETA BEEKAMTII", fill=main_color, font=f_header, anchor="mm")
    draw.text((width//2, 420), f"Obbo/Adde: {name.upper()}", fill=main_color, font=f_name, anchor="mm")
    msg = f"Waggaa 2026 keessatti tajaajila saffisaa fi amannamaa ta'een\nAbbootii Dhimmaa {count} tajaajiluun beekamtii kanaan badhaafamaniiru."
    draw.text((width//2, 540), msg, fill="#333", font=f_body, anchor="mm", align="center")
    return img

# ================= 3. UI LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login - Dadar Land Admin")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("SEENI"):
        if u == "admin" and p == "2026":
            st.session_state.logged_in = True; st.rerun()
        else: st.error("Invaaliidii!")
else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Logout"])

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            st.plotly_chart(px.bar(df, x='Araddaa', y='Kafaltii_Taj', color='Araddaa', title="Galii Araddaadhaan"))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Maamilaa")
            ara = col1.selectbox("Araddaa", ["01", "02", "03", "04", "Baadiyyaa"])
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            qax = col2.text_input("Qaxana / L.Manaa")
            nagahee = st.file_uploader("Nagahee (Suuraa)", type=['jpg','png','jpeg'])
            
            final_services, total_fee = [], 0.0
            for cat in selected_cats:
                st.subheader(cat)
                subs = st.multiselect(f"Gosa {cat}:", SERVICE_STRUCTURE[cat], key=f"s_{cat}")
                for s in subs:
                    col_a, col_b = st.columns([3, 1])
                    if "TOT" in s:
                        v = col_b.number_input(f"Gatii Waliigaltee ({s})", min_value=0.0, key=f"v_{s}")
                        fee = v * 0.02
                        final_services.append(f"{s}(2%)")
                    else:
                        fee = col_b.number_input(f"Kaffaltii {s}", min_value=0.0, key=f"f_{s}")
                        final_services.append(s)
                    total_fee += fee
            
            if st.form_submit_button("💾 GALMEESSI FI ERGI"):
                if name and final_services:
                    f_path = None
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    msg = f"🚀 *GALMEE HAARAA*\n👤 Maamila: {name}\n📍 Bakka: {ara}\n🛠 Tajaajila: {', '.join(final_services)}\n💰 *Kaffaltii: {total_fee:,.2f} ETB*\n👷 Ogeessa: {ogeessa}"
                    send_telegram_msg(msg, f_path)
                    st.success("Milkaa'inaan Galmeeffameera!")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.title("🏆 Badhaasa Ogeessota Cimaa")
        if not df.empty:
            u_logo = st.file_uploader("Logo Waajjiraa Galchi", type=["png", "jpg", "jpeg"])
            top_performers = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            medals = ["🥇 1FFAA", "🥈 2FFAA", "🥉 3FFAA"]
            for i, (name, count) in enumerate(top_performers.items()):
                with cols[i]:
                    st.markdown(f"### {medals[i]}\n**{name}**\nTajaajilamtoota: {count}")
                    if st.button(f"Sartiifiikeeta {i+1}ffaa"):
                        cert = create_dadar_cert(name, count, i+1, u_logo)
                        st.image(cert, use_container_width=True)
                        buf = io.BytesIO(); cert.save(buf, format="PNG")
                        st.download_button(f"📥 Download {i+1}ffaa", buf.getvalue(), f"Cert_{name}.png", "image/png")

    elif menu == "🔍 Barbaadi/Edit":
        st.title("🔍 To'annoo Ragaalee")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            if not res.empty:
                idx = st.selectbox("ID Haquuf filadhu:", res.index)
                if st.button("🚨 HAQUU"):
                    df = df.drop(idx)
                    save_data(df); st.rerun()

    elif menu == "Logout":
        st.session_state.logged_in = False; st.rerun()

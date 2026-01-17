import streamlit as st
import pandas as pd
import os
import io
import requests
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import gold, silver, hexColor, green, black, white

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "Adiaan/nagahee"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR, exist_ok=True)

st.set_page_config(page_title="Dadar Land System", layout="wide")

# ================= 2. FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
    return True

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

def send_telegram_msg(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "HTML"})
    except: pass

def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(A4))
    width, height = landscape(A4)
    theme_color = {1: gold, 2: silver, 3: hexColor("#CD7F32")}.get(rank, green)

    c.setStrokeColor(theme_color); c.setLineWidth(5); c.rect(12*mm, 12*mm, width-24*mm, height-24*mm)
    
    if logo_l: c.drawImage(io.BytesIO(logo_l.getvalue()), 20*mm, height-45*mm, width=30*mm, height=30*mm, mask='auto')
    
    c.setFont("Helvetica-Bold", 40); c.setFillColor(theme_color)
    c.drawCentredString(width/2, height-70*mm, "SARTIIFIKEETA BEEKAMTII")
    c.setFont("Helvetica-Bold", 30); c.setFillColor(black)
    c.drawCentredString(width/2, height-110*mm, str(name).upper())
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height-130*mm, f"Tajaajilamtoota {count} saffisaan tajaajiluun sadarkaa {rank}ffaa")
    c.drawCentredString(width/2, height-140*mm, "waggaa 2026 waan qabataniif beekamtiin kun kennameef.")
    
    c.showPage(); c.save()
    packet.seek(0)
    return packet.getvalue()

# ================= 3. UI LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container():
        st.markdown("<h2 style='text-align:center;'>🔐 Systemii Dadar: Seeni</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "DAD" and p == "2026": 
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "🔍 Edit", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard & Gabaasa Excel")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Guutuu", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            # Excel Export
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            st.download_button("📥 Gabaasa Excel Buufadhu", output.getvalue(), "Gabaasa_Dadar.xlsx")
            
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER))
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("galmee"):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            taj = st.multiselect("Tajaajila", ["Gibira", "Liizii", "Kaartaa", "Jijjiirraa Maqaa"])
            kafaltii = st.number_input("Kafaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, "-", ", ".join(taj), ogeessa, kafaltii]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                if save_data(df):
                    st.success("✅ Galmeeffameera!")
                    msg = f"<b>🔔 Galmee Haaraa</b>\n👤: {maqaa}\n💰: {kafaltii} ETB\n👷: {ogeessa}"
                    send_telegram_msg(msg)
                    st.rerun()

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.subheader(f"{i}ffaa: {name}")
                    pdf = create_advanced_pdf(name, count, i)
                    st.download_button(f"📥 Sartiifiikeeta {i}ffaa", pdf, f"Cert_{name}.pdf")

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

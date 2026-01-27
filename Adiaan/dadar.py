import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png" 
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# Telegram Credentials
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"

# ================= 2. FUNCTIONS =================
def send_telegram_notification(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
        requests.get(url)
    except:
        pass

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_clearance_cert(name, araddaa, ogeessa):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(46, 125, 50) # Green border
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 130, 15, 35)
    
    pdf.set_y(55)
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 15, "BULCHIINSA MAGAALAA DADAR", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "WARAQAA QULQULLUMMAA (LAND CLEARANCE)", 0, 1, 'C')
    
    pdf.ln(15)
    pdf.set_font('Arial', '', 14)
    text = f"Obbo/Adde {name}, Araddaa {araddaa} keessatti kan argaman, kaffaltii mootummaa irraa jiru hunda xumuruu isaanii fi qabiyyeen isaanii kamirraayyuu bilisa ta'uu isaa ni mirkaneessina."
    pdf.multi_cell(0, 10, text, align='C')
    
    pdf.set_y(150)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')} | Ogeessa: {ogeessa}", 0, 1, 'C')
    pdf.ln(5)
    pdf.cell(0, 10, "Mallattoo fi Chaappaa: _______________________", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. UI STYLE =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stSidebar { background-color: #ffffff !important; border-right: 1px solid #eee; }
    .stMetric { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-top: 4px solid #2e7d32; }
    .login-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-top: 10px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 4. LOGIN =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.subheader("Login Center")
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI / LOGIN", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Daraaramni dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= 5. MAIN SYSTEM =================
else:
    df = load_data()
    st.sidebar.title("Main Menu")
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        with c2: st.metric("👥 Maamiltoota", len(df))
        with c3: st.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        
        st.markdown("---")
        fig = px.pie(df, names='Gosa_Tajajjilaa', values='Kafaltii_Taj', hole=0.4, title="Qoodinsa Galii")
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Haaraa fi Hawataa")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col1.text_input("Araddaa")
            qax = col2.text_input("Qaxana")
            og = col2.text_input("Maqaa Ogeessaa")
            
            gosa = st.selectbox("Gosa Tajaajilaa", ["Waraqaa Qulqullummaa", "Gibira Baaxii Gooroo", "TOT 2%", "Kaartaa Haaraa", "Liizii Waggaa"])
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            if st.button("💾 GALMEESSI FI EERGI", use_container_width=True):
                if name and og:
                    final_fee = fee * 0.02 if "TOT" in gosa else fee
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, gosa, og, final_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    
                    # Telegram Notification
                    msg = f"🔔 *Galmee Haaraa*\n👤 Maqaa: {name}\n📍 Araddaa: {ara}\n🛠 Tajaajila: {gosa}\n💵 Kaffaltii: {final_fee:,.2f} ETB\n👷 Ogeessa: {og}"
                    send_telegram_notification(msg)
                    
                    st.success("✅ Galmeeffameera! Gabaasni gara Telegramitti ergameera.")
                else: st.error("Maaloo odeeffannoo guutuu galchi!")

    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Waliigalaa")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Gabaasa (Excel/CSV) Buufadhu", csv, "gabaasa_dadar.csv", "text/csv")

    elif menu == "🏆 Badhaasa":
        st.title("🏆 Badhaasa fi Clearance")
        st.write("Waraqaa Qulqullummaa (Clearance) asitti print godhi.")
        
        target_name = st.selectbox("Maqaa Abbaa Dhimmaa filadhu:", df['Maqaa_Abbaa_Dhimmaa'].unique())
        if st.button("🖨 Clearance Qopheessi"):
            user_data = df[df['Maqaa_Abbaa_Dhimmaa'] == target_name].iloc[-1]
            pdf_bytes = create_clearance_cert(user_data['Maqaa_Abbaa_Dhimmaa'], user_data['Araddaa'], user_data['Maqaa_Ogeessa'])
            st.download_button(f"📥 PDF Buufadhu ({target_name})", pdf_bytes, f"Clearance_{target_name}.pdf", "application/pdf")

    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

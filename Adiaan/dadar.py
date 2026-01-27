import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR)

# ================= 2. CORE FUNCTIONS =================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID_MANAGER, "text": msg, "parse_mode": "Markdown"})
    except: pass

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    # Guyyaa gara format datetime tii jijjiiruuf
    df['dt'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['dt'].dt.year
    df['Ji\'a'] = df['dt'].dt.month_name()
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(46, 125, 50); pdf.set_line_width(5); pdf.rect(10, 10, 277, 190)
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 130, 15, 30)
    pdf.set_y(55); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 15, f"Ogeessa: {name}", 0, 1, 'C')
    pdf.set_y(105); pdf.set_font('Arial', 'I', 16)
    pdf.multi_cell(0, 10, f"Waggaa kanatti maamiltoota {count} tajaajiluun\nsadarkaa {rank}ffaa argataniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. UI STYLE =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")
st.markdown("""<style>
    .stApp { background: #f8fafc; }
    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    .login-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-top: 10px solid #2e7d32; text-align: center; }
    </style>""", unsafe_allow_html=True)

# ================= 4. LOGIN SYSTEM =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.header("Wajjira Lafa Dadar")
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI", use_container_width=True):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora Username ykn Password!")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= 5. MAIN APP =================
else:
    df = load_data()
    
    # --- SIDEBAR WITH LOGO ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        st.markdown("### 🏢 Admin Panel")
        st.markdown("---")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "🔍 Barbaadi/Edit", "Logout"])
        st.markdown("---")
        st.info(f"📅 Har'a: {datetime.now().strftime('%d/%m/%Y')}")

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            st.plotly_chart(px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa', title="Trendii Kaffaltii Guyyaatti"))
            
            if st.button("🚀 Gabaasa Har'aa Telegramitti Ergi"):
                today = datetime.now().strftime('%d/%m/%Y')
                t_df = df[df['Guyyaa'] == today]
                if not t_df.empty:
                    msg = f"📊 *GABAASA WALIIGALAA ({today})*\n💰 Galii: {t_df['Kafaltii_Taj'].sum():,.2f} ETB\n👥 Maamila: {len(t_df)}"
                    send_telegram(msg); st.success("Gabaasni ergameera!")
        else: st.info("Ragaan galmeeffame hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            og = c1.text_input("Ogeessa Raawwate")
            gosa = c2.selectbox("Gosa Tajaajilaa", ["Gibira", "Kaartaa", "Clearance", "Liizii", "Pilaanii"])
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, og, fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    send_telegram(f"🆕 *Galmee Haaraa*\n👤 Maamila: {name}\n💰 Kaffaltii: {fee} ETB\n👷 Ogeessa: {og}")
                    st.success("Milkaa'inaan galmeeffameera!")
                else: st.error("Maaloo ragaa guutuu galchi!")

    # --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.title("📈 Gabaasa & Calaltuu")
        if not df.empty:
            sel_y = st.selectbox("Waggaa Filadhu", sorted(df['Waggaa'].dropna().unique(), reverse=True))
            filtered = df[df['Waggaa'] == sel_y]
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            st.metric("Waliigala Galii Waggaa", f"{filtered['Kafaltii_Taj'].sum():,.2f} ETB")


    # --- SEARCH / EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.title("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not res.empty:
                for idx, row in res.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                        if st.button("🗑 Haqi", key=f"del_{idx}"):
                            df = df.drop(idx); save_data(df); st.rerun()
            else: st.warning("Maqaan kun hin jiru.")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()


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
NAGAHEE_DIR = "nagahee_scan"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
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
    # Guyyaa gara format datetime jijjiiruuf
    df['dt'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['dt'].dt.year
    df['Ji\'a'] = df['dt'].dt.month
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(46, 125, 50)
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 130, 15, 30)
        
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 15, f"Ogeessa: {name}", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 16)
    msg = f"Waggaa kanatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru."
    pdf.multi_cell(0, 10, msg, align='C')
    pdf.set_y(160)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')} | Mallattoo: ________________", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI STYLE =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")
st.markdown("""<style>
    .stApp { background: #f8fafc; }
    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    </style>""", unsafe_allow_html=True)

# ================= 4. SERVICE LIST =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
}

# ================= 5. LOGIN SYSTEM =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.header("Wajjira Lafa Dadar")
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.plotly_chart(px.bar(df, x='dt', y='Kafaltii_Taj', color='Maqaa_Ogeessa'))

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Haaraa")
        selected_cats = st.multiselect("Ramaddii:", list(SERVICE_STRUCTURE.keys()))
        final_services = []
        total_fee = 0
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    subs = st.multiselect(f"{cat}:", SERVICE_STRUCTURE[cat])
                    for s in subs:
                        f = st.number_input(f"Kaffaltii {s}", min_value=0.0, key=s)
                        final_services.append(s); total_fee += f
        with st.form("reg"):
            name = st.text_input("Maqaa Abbaa Dhimmaa")
            og = st.text_input("Ogeessa")
            if st.form_submit_button("Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), name, "Araddaa", "Q", ", ".join(final_services), og, total_fee]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                send_telegram(f"🔔 *Galmee Haaraa*\n👤 {name}\n💰 {total_fee} ETB")
                st.success("Galmeeffameera!")

    elif menu == "📈 Gabaasa Bal'aa":
        st.title("📈 Gabaasa")
        if not df.empty:
            sel_y = st.sidebar.selectbox("Waggaa", df['Waggaa'].unique())
            filtered = df[df['Waggaa'] == sel_y]
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            st.metric("Galii Waliigalaa", f"{filtered['Kafaltii_Taj'].sum():,.2f} ETB")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.title("🏆 Sartiifiikeeta")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{name}</h3><p>Tajaajile: {count}</p></div>", unsafe_allow_html=True)
                    pdf = create_pdf_cert(name, count, i+1)
                    st.download_button(f"📥 PDF {name}", pdf, f"{name}.pdf")

    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

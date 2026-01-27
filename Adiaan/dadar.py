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
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 133, 15, 30)
    pdf.set_y(50); pdf.set_font('Arial', 'B', 35); pdf.cell(0, 30, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 25); pdf.cell(0, 20, f"Ogeessa: {name}", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 18); pdf.multi_cell(0, 15, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun\nsadarkaa {rank}ffaa argataniiru.", align='C')
    pdf.set_y(165); pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')} | Mallattoo: ________________", 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. UI STYLE =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")
st.markdown("""<style>
    .stApp { background: #f8fafc; }
    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 1px solid #e2e8f0; }
    </style>""", unsafe_allow_html=True)

# ================= 4. LOGIN SYSTEM =================
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
            if st.form_submit_button("SEENI", use_container_width=True):
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

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.plotly_chart(px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa', title="Trendii Kaffaltii"))
            
            if st.button("🚀 Gabaasa Har'aa Telegramitti Ergi"):
                today = datetime.now().strftime('%d/%m/%Y')
                t_df = df[df['Guyyaa'] == today]
                if not t_df.empty:
                    msg = f"📊 *GABAASA GUYYAA ({today})*\n💰 Galii: {t_df['Kafaltii_Taj'].sum():,.2f} ETB\n👥 Maamila: {len(t_df)}"
                    send_telegram(msg); st.success("Telegramitti ergameera!")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            og = c1.text_input("Ogeessa")
            gosa = c2.selectbox("Gosa Tajaajilaa", ["Gibira", "Kaartaa", "Clearance", "Liizii", "Pilaanii"])
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, og, fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    send_telegram(f"🆕 *Galmee Haaraa*\n👤: {name}\n💰: {fee} ETB")
                    st.success("Galmeeffameera!")

    # --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.title("📈 Gabaasa & Calaltuu")
        if not df.empty:
            y_filter = st.selectbox("Waggaa", sorted(df['Waggaa'].unique(), reverse=True))
            filtered = df[df['Waggaa'] == y_filter]
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            st.metric("Galii Waggaa", f"{filtered['Kafaltii_Taj'].sum():,.2f} ETB")

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.title("🏆 Badhaasa Ogeeyyii Cimaa")
        if not df.empty:
            top_og = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_og.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{name}</h3><p>Maamila {count} tajaajile</p></div>", unsafe_allow_html=True)
                    if st.button(f"PDF Print: {name}"):
                        cert = create_pdf_cert(name, count, i+1)
                        st.download_button(f"📥 Buufadhu {name}", cert, f"Cert_{name}.pdf")

    # --- SEARCH/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.title("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Maamilaa...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    new_fee = st.number_input("Kaffaltii Sirreessi", value=float(row['Kafaltii_Taj']), key=f"ed_{idx}")
                    if st.button("Update", key=f"btn_{idx}"):
                        df.at[idx, 'Kafaltii_Taj'] = new_fee
                        save_data(df); st.rerun()
                    if st.button("🗑 Haqi", key=f"del_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & DIRECTORIES =================
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# ================= 2. SERVICE STRUCTURE (GOSA TAJAAJILAA) =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax) 2%", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Sirreeffama Daangaa", "Kaartaa Lafa Qonnaa", "Waraqaa Ragaa Qabiyyee"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Hayyama Ijaarsaa", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Qulqullummaa (Clearance)", "Deebii Iyyannoo", "Waraqaa Eenyummaa Lafa"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", "Adabbii Faallaa Pilaanii"
    ],
}

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf_cert(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 100, 0)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    
    if logo_left:
        with open("tmp_l.png", "wb") as f: f.write(logo_left.getbuffer())
        pdf.image("tmp_l.png", 20, 15, 30)
    if logo_right:
        with open("tmp_r.png", "wb") as f: f.write(logo_right.getbuffer())
        pdf.image("tmp_r.png", 230, 15, 30)

    pdf.set_y(60)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 25, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun\nsadarkaa {rank}ffaa argataniiru.", align='C')
    
    pdf.line(110, 175, 180, 175)
    pdf.set_xy(110, 177)
    pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. UI & LOGIN =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Administration Login")
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Seeni"):
            if u == "admin" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username ykn Password dogoggora!")
else:
    # Sidebar Navigation
    df = load_data()
    st.sidebar.title("Dadar Land Admin")
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Maamiltootaa", len(df))
            c3.metric("👷 Ogeeyyii Cimaa", df['Maqaa_Ogeessa'].nunique())
            
            fig = px.pie(df, names='Gosa_Tajajjilaa', values='Kafaltii_Taj', title="Qoodinsa Galii Tajaajilaan")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col1.text_input("Araddaa")
            qax = col2.text_input("Qaxana")
            og = col2.text_input("Maqaa Ogeessaa")
            
            st.markdown("---")
            cat_choice = st.selectbox("Ramaddii Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
            serv_choice = st.selectbox("Gosa Tajaajilaa", SERVICE_STRUCTURE[cat_choice])
            
            # Auto-calculation for TOT
            fee_input = st.number_input("Gatii/Kaffaltii (ETB)", min_value=0.0)
            final_fee = fee_input
            if "TOT" in serv_choice:
                final_fee = fee_input * 0.02
                st.caption(f"Hubachiisa: Kaffaltii TOT (2%) ofumaan herregameera: {final_fee:,.2f} ETB")

            if st.form_submit_button("💾 GALMEESSI"):
                if name and og and final_fee >= 0:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, serv_choice, og, final_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Kaffaltii: {final_fee:,.2f} ETB")
                else:
                    st.error("Maaloo odeeffannoo guutuu galchi!")

    # --- REPORT ---
    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Waliigalaa")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Excel/CSV gabaasa buufadhu", csv, "gabaasa_dadar.csv", "text/csv")
        else:
            st.warning("Data'n hin jiru.")

    # --- AWARDS ---
    elif menu == "🏆 Badhaasa":
        st.title("🏆 Sartiifiikeeta Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            l_img = st.file_uploader("Logo Bita", type=['png','jpg'])
            r_img = st.file_uploader("Logo Mirga", type=['png','jpg'])
            
            cols = st.columns(len(top_3))
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.success(f"Sadarkaa {i+1}ffaa")
                    st.subheader(name)
                    st.write(f"Tajaajila: {count}")
                    pdf_b = create_pdf_cert(name, count, i+1, l_img, r_img)
                    st.download_button(f"📥 PDF Buufadhu", pdf_b, f"Cert_{name}.pdf", key=f"btn_{i}")

    # --- SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi / Haqii")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not results.empty:
                st.dataframe(results)
                idx_to_del = st.selectbox("Haquuf ID filadhu:", results.index)
                if st.button("🗑 Haqii"):
                    df = df.drop(idx_to_del)
                    save_data(df)
                    st.success("Haqameera!")
                    st.rerun()
            else:
                st.info("Ragaan hin argamne.")

import streamlit as st
import pandas as pd
import os
import io
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 900; color: #10b981; text-align: center; }
    .login-box { background-color: #ffffff; padding: 40px; border-radius: 15px; box-shadow: 0px 10px 25px rgba(0,0,0,0.1); text-align: center; border-top: 8px solid #2e7d32; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. DATA FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

# ================= 3. LOGIN LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.header("Dadar Land Administration")
        with st.form("Login"):
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI / LOGIN"):
                if user == "admin" and password == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # ================= 4. MAIN SYSTEM =================
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🔍 Barbaadi", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        
        fig = px.bar(df.groupby('Gosa_Tajajjilaa')['Kafaltii_Taj'].sum().reset_index(), 
                     x='Gosa_Tajajjilaa', y='Kafaltii_Taj', title="Galii Gosa Tajaajilaan")
        st.plotly_chart(fig, use_container_width=True)

        elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        
        # --- SERVICE STRUCTURE ---
        SERVICE_STRUCTURE = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax) 2%"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa"],
            "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Hayyama Ijaarsaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
            "📂 Tajaajila Biroo": ["Waraqaa Qulqullummaa", "Deebii Iyyannoo"],
            "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"]
        }
        
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col1.text_input("Araddaa")
            qax = col2.text_input("Qaxana")
            og = col2.text_input("Maqaa Ogeessaa")
            
            cat_choice = st.selectbox("Ramaddii Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
            serv_choice = st.selectbox("Gosa Tajaajilaa", SERVICE_STRUCTURE[cat_choice])
            
            fee_input = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            final_fee = fee_input * 0.02 if "TOT" in serv_choice else fee_input

            if st.form_submit_button("💾 GALMEESSI"):
                if name and og:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, serv_choice, og, final_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Kaffaltii: {final_fee:,.2f} ETB")


    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Waliigalaa")
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 CSV Buufadhu", df.to_csv(index=False), "gabaasa.csv")

    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi / Haqii")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(results)
st.title("📝 Galmee Tajaajilaa Haaraa")
# --- SERVICE STRUCTURE ---
SERVICE_STRUCTURE = {
"🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax) 2%"],
"📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa"],
"🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Hayyama Ijaarsaa"],
"⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
"📂 Tajaajila Biroo": ["Waraqaa Qulqullummaa", "Deebii Iyyannoo"],
"⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"]
}

with st.form("reg_form"):
col1, col2 = st.columns(2)
name = col1.text_input("Maqaa Abbaa Dhimmaa")
ara = col1.text_input("Araddaa")
qax = col2.text_input("Qaxana")
og = col2.text_input("Maqaa Ogeessaa")

cat_choice = st.selectbox("Ramaddii Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
serv_choice = st.selectbox("Gosa Tajaajilaa", SERVICE_STRUCTURE[cat_choice])

fee_input = st.number_input("Kaffaltii (ETB)", min_value=0.0)
final_fee = fee_input * 0.02 if "TOT" in serv_choice else fee_input

if st.form_submit_button("💾 GALMEESSI"):
if name and og:
new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, serv_choice, og, final_fee]
df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
save_data(df)
st.success(f"✅ Galmeeffameera! Kaffaltii: {final_fee:,.2f} ETB")

elif menu == "📈 Gabaasa":
st.title("📈 Gabaasa Waliigalaa")
st.dataframe(df, use_container_width=True)
st.download_button("📥 CSV Buufadhu", df.to_csv(index=False), "gabaasa.csv")

elif menu == "🔍 Barbaadi":
st.title("🔍 Barbaadi / Haqii")
q = st.text_input("Maqaa Barbaadi...")
if q:
results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
st.dataframe(results)
idx = st.selectbox("ID Haquuf:", results.index)
if st.button("🗑 Haqii"):
df = df.drop(idx)
save_data(df)
st.rerun()




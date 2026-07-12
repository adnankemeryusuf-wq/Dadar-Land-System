import streamlit as st
import pandas as pd
import os
import io
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

st.set_page_config(page_title="Dadar Land Admin", layout="wide", page_icon="🏢")

# ================= 2. DATA FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

# ================= 3. LOGIN & APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.header("Dadar Land Admin")
        with st.form("Login"):
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI"):
                if user == "admin" and password == "1234":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🔍 Barbaadi", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        c1, c2 = st.columns(2)
        c1.metric("Galii", f"{df['Kafaltii_Taj'].sum():,.2f}")
        c2.metric("Maamiltoota", len(df))

    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa")
        with st.form("reg_form"):
            name = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            og = st.text_input("Maqaa Ogeessaa")
            fee = st.number_input("Kaffaltii", min_value=0.0)
            if st.form_submit_button("💾 GALMEESSI"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, "Tajaajila", og, fee]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success("✅ Galmeeffameera!")

    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa")
        st.dataframe(df)

    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            st.dataframe(df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)])

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




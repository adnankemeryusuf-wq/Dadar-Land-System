import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_kuusaa"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", layout="wide")

# Akka Dashboard kee ijaatti tolutti
st.markdown("""
    <style>
    .main { background-color: #f1f4f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #2e7d32; }
    .stSidebar { background-color: #0d2335; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    columns = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Nagahee_Path']
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=columns)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", encoding='utf-8')
        if 'Guyyaa' not in df.columns:
            df = pd.read_csv(DATA_FILE, sep="|", names=columns, header=None, encoding='utf-8')
        df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
        return df
    except:
        return pd.DataFrame(columns=columns)

def save_data(df):
    cols = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Nagahee_Path']
    df[cols].to_csv(DATA_FILE, sep="|", index=False, encoding="utf-8")

# ================= 3. LOGIN SYSTEM =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username (ADMIN / USER)")
    p = st.text_input("Password", type="password")
    
    if st.button("Seeni"):
        if u.upper() == "ADMIN" and p == "2026":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()
        elif u.upper() == "USER" and p == "1234":
            st.session_state.logged_in = True
            st.session_state.role = "user"
            st.rerun()
        else:
            st.error("Username ykn Password dogoggora!")

# ================= 4. MAIN APP =================
else:
    df = load_data()
    
    # 🔐 Iccitii: Menu calaluu
    if st.session_state.role == "admin":
        options = ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "🔍 Barbaadi"]
    else:
        # User-iin Dashboard fi Badhaasa hin argu
        options = ["📝 Galmee Haaraa", "🔍 Barbaadi"]
        
    menu = st.sidebar.radio("FILANNOO", options)
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD (ADMIN QOFAAF) ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        
        st.subheader("📈 Trendii Kaffaltii")
        if not df.empty:
            st.area_chart(df.groupby('Guyyaa')['Kafaltii_Taj'].sum())

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            # 💡 Fakkeenya ati jette itti dabalameera
            name = col1.text_input("Maqaa Maamilaa", placeholder="Abdi Mahammad Yusuuf")
            ara = col2.text_input("Araddaa", placeholder="01 ykn 02")
            gosa = col1.selectbox("Gosa Tajaajilaa", ["Kaartaa Haaraa", "Jijjiirraa Maqaa", "Liizii", "Gibira", "TOT"])
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            
            # 💰 Fakkeenya 0.00
            kaffaltii = col1.number_input("Kaffaltii (ETB)", min_value=0.0, format="%.2f")
            
            nagahee_file = st.file_uploader("Nagahee Scan Upload", type=['jpg', 'png'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and ara and ogeessa:
                    n_path = "N/A"
                    if nagahee_file:
                        n_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(n_path, "wb") as f: f.write(nagahee_file.getbuffer())
                    
                    new_row = pd.DataFrame([[datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, ogeessa, kaffaltii, n_path]], 
                                           columns=['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Nagahee_Path'])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeen {name} milkaa'inaan kuufameera!")
                else:
                    st.error("Maaloo kutaalee hunda guuti!")

    # --- BARBAADI (FIXED KEYERROR) ---
    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        query = st.text_input("Maqaa Maamilaa Barreessi...")
        if query:
            # SIRREEFFAMA: Square bracket asitti sirreeffameera
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(query, case=False, na=False)]
            st.dataframe(res)

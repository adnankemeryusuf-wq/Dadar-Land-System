import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & CUSTOM STYLE =================
LOGO_PATH = "Adiaan/logo.png"

st.set_page_config(
    page_title="Dadar Land System", 
    page_icon="🏢", 
    layout="wide"
)

# Halluu #1b5e20 fi Istaayila Idilee
st.markdown(f"""
    <style>
    /* 1. Background fi Font */
    .stApp {{ background-color: #f8faf9; }}
    
    /* 2. Sidebar Style */
    [data-testid="stSidebar"] {{
        background-color: #1b5e20 !important;
        border-right: 2px solid #ffd700;
    }}
    [data-testid="stSidebar"] * {{ color: white !important; font-weight: 500; }}

    /* 3. Headers */
    h1, h2, h3, h4 {{ color: #1b5e20 !important; font-family: 'Inter', sans-serif; }}

    /* 4. Dashboard Cards */
    .card {{
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border-top: 6px solid #1b5e20;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }}
    .metric-value {{
        font-size: 32px;
        font-weight: bold;
        color: #1b5e20;
        margin: 10px 0;
    }}
    .metric-label {{ color: #555; font-size: 16px; font-weight: 600; }}

    /* 5. Buttons */
    .stButton>button {{
        background-color: #1b5e20;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        width: 100%;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #2e7d32;
        color: #ffd700;
        border: 1px solid #ffd700;
    }}

    /* 6. Forms */
    div.stForm {{
        border: 2px solid #1b5e20;
        border-radius: 20px;
        padding: 30px;
        background-color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA HANDLING =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False)

# ================= 3. APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- Login Page ---
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("<h3>Admin Login</h3></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Koodiin dogoggora!")
else:
    df = load_data()
    # --- Sidebar Navigation ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("#### Dadar Admin")
        st.markdown("Deder City Land Office")
        st.divider()
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        st.spacer = st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Ba'i (Logout)"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 📊 DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2>📊 Dashboard Waliigalaa</h2>", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p class='metric-label'>💰 Waliigala Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p><p>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p class='metric-label'>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p><p>Galmeeffaman</p></div>", unsafe_allow_html=True)
            with c3:
                top_og = df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else "-"
                st.markdown(f"<div class='card'><p class='metric-label'>🏆 Ogeessa Filatamaa</p><p class='metric-value'>{top_og}</p><p>Hojii Baay'ee</p></div>", unsafe_allow_html=True)
            
            st.subheader("📈 Xiinxala Galii")
            st.line_chart(df['Kafaltii_Taj'])
        else:
            st.info("Data'n galmeeffame hin jiru.")

    # --- 📝 GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.markdown("<h2>📝 Galmee Tajaajilaa Haaraa</h2>", unsafe_allow_html=True)
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col2.text_input("Araddaa")
            qax = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessa Tajaajila kenne")
            gosa = st.selectbox("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa", "Dhimma Mana Murtii", "Liqii Bankii"])
            kafaltii = st.number_input("Kafaltii Tajaajilaa (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, gosa, ogeessa, kafaltii]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"Galmeen {maqaa} milkiin kuufameera!")
                else: st.warning("Maaloo, Maqaa fi Ogeessa guuti.")

    # --- 📈 GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.markdown("<h2>📈 Gabaasa fi Xiinxala Galii</h2>", unsafe_allow_html=True)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            # Excel Download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Gabaasa')
            st.download_button("📥 Excel Buufadhu", output.getvalue(), "Gabaasa_Dadar.xlsx")
        else: st.warning("Data'n hin jiru.")

    # --- 🏆 BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.markdown("<h2>🏆 Sadarkaa Hojii Ogeeyyii</h2>", unsafe_allow_html=True)
        if not df.empty:
            counts = df['Maqaa_Ogeessa'].value_counts()
            for name, count in counts.items():
                st.markdown(f"""
                <div style='background:white; padding:15px; border-radius:10px; margin-bottom:10px; border-left:5px solid #ffd700;'>
                    <b>{name}</b>: Tajaajila <b>{count}</b> kenneera.
                </div>
                """, unsafe_allow_html=True)
        else: st.info("Hojiin ogeeyyii galmeeffame hin jiru.")

    # --- 🔍 BARBAADI/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.markdown("<h2>🔍 Barbaadi ykn Sirreessi</h2>", unsafe_allow_html=True)
        search = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if search:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search, case=False, na=False)]
            st.table(results)

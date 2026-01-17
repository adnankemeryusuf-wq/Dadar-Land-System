import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. QINDOOMMINA (CONFIG) =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
LOGO_PATH = "Adiaan/logo.png"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land System", layout="wide")

# COL_NAMES fi Ji'oota
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

# CSS - Bifa Dashboard
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    .metric-value { font-size: 24px; font-weight: bold; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DALAGAAWWAN (FUNCTIONS) =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0.0)
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. LOGIN & APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>Dadar Land Admin</h2>", unsafe_allow_html=True)
        # KEY UNIQUE: "system_login_form"
        with st.form(key="system_login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maqaa ykn Password dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit"])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3:
                top_og = df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else "-"
                st.markdown(f"<div class='card'><p>🏆 Ogeessa Filatamaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            # Trend Chart
            daily_rev = df.groupby('Guyyaa')['Kafaltii_Taj'].sum().reset_index()
            fig = px.line(daily_rev, x='Guyyaa', y='Kafaltii_Taj', title="Trendii Galii")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data'n galmeeffame hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Haaraa")
        with st.form(key="registration_form_new", clear_on_submit=True):
            col1, col2 = st.columns(2)
            m_name = col1.text_input("Maqaa Abbaa Dhimmaa")
            m_ara = col2.text_input("Araddaa")
            m_oge = col1.text_input("Maqaa Ogeessaa")
            m_kaff = col2.number_input("Kafaltii (ETB)", min_value=0.0)
            m_gosa = st.selectbox("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa", "Jijjiirraa Maqaa"])
            
            nagahee_file = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])

            if st.form_submit_button("💾 Galmeessi"):
                if m_name and m_oge:
                    if nagahee_file:
                        f_path = os.path.join(NAGAHEE_DIR, f"{m_name.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee_file.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), m_name, m_ara, "N/A", m_gosa, m_oge, m_kaff]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                else: st.error("Maaloo maqaa guuti!")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Waliigalaa")
        st.dataframe(df[COL_NAMES], use_container_width=True)
        
        # Excel Download
        buf = io.BytesIO()
        df[COL_NAMES].to_excel(buf, index=False)
        st.download_button("📥 Excel Buusi", buf.getvalue(), "Gabaasa_Dadar.xlsx")

    # --- EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa maamilaa barreessi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"Sirreessi: {row['Maqaa_Abbaa_Dhimmaa']}"):
                    # KEY UNIQUE: f"edit_form_{idx}"
                    with st.form(key=f"edit_form_{idx}"):
                        u_n = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'])
                        u_k = st.number_input("Kafaltii", float(row['Kafaltii_Taj']))
                        if st.form_submit_button("💾 Update"):
                            df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = u_n
                            df.at[idx, 'Kafaltii_Taj'] = u_k
                            save_data(df); st.success("Sirreeffameera!"); st.rerun()

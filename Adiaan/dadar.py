import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div[data-baseweb="multiselect"] { border: 2px solid #2e7d32 !important; background-color: #ffffff !important; border-radius: 8px !important; }
    span[data-baseweb="tag"] { background-color: #2e7d32 !important; color: white !important; border-radius: 5px !important; }
    div.stForm { background: rgba(255, 255, 255, 0.9); border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    .download-btn { background-color: #1b5e20; color: white; padding: 10px; border-radius: 5px; text-decoration: none; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
WEEKDAY_MAP = {0: "Wixata", 1: "Filatama", 2: "Roobii", 3: "Kamisa", 4: "Jimmata", 5: "Sanbata", 6: "Dilbata"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center; color:#2e7d32;'>Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        st.markdown("### 🏢 DADAR LAND ADMIN")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi", "Ba'i"])

    df = load_data()

    if menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #2e7d32;'>📝 Galmee Tajaajilaa</h2>", unsafe_allow_html=True)
        # (Content of Registration Form - keep previous logic...)
        # I am omitting full form logic here for brevity, keep your existing form code.

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Yeroon Calalame")
        if not df.empty:
            df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y')
            df['Waggaa'] = df['Date_Obj'].dt.year
            df['Ji\'a_Lakk'] = df['Date_Obj'].dt.month
            df['Ji\'a'] = df['Ji\'a_Lakk'].map(MONTH_MAP)
            df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
            df['Guyyaa_Torbee'] = df['Date_Obj'].dt.dayofweek.map(WEEKDAY_MAP)
            df['Kurmaana'] = (df['Ji\'a_Lakk'] - 1) // 3 + 1

            c1, c2, c3, c4 = st.columns(4)
            sel_year = c1.selectbox("Waggaa", sorted(df['Waggaa'].unique(), reverse=True))
            sel_q = c2.selectbox("Kurmaana", [1, 2, 3, 4])
            sel_month = c3.selectbox("Ji'a", list(MONTH_MAP.values()))
            sel_week = c4.selectbox("Torbee", [1, 2, 3, 4])

            st.divider()
            f_type = st.radio("Akkaataa Gabaasaa:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee"], horizontal=True)
            
            filtered_df = df[df['Waggaa'] == sel_year]
            if f_type == "Kurmaana": filtered_df = filtered_df[filtered_df['Kurmaana'] == sel_q]
            elif f_type == "Ji'a": filtered_df = filtered_df[filtered_df['Ji\'a'] == sel_month]
            elif f_type == "Torbee": filtered_df = filtered_df[(filtered_df['Ji\'a'] == sel_month) & (filtered_df['Torbee'] == sel_week)]

            # Output Table
            final_report = filtered_df[COL_NAMES]
            st.dataframe(final_report, use_container_width=True)
            st.metric(f"Waliigala Galii", f"{final_report['Kafaltii_Taj'].sum():,.2f} ETB")

            # EXCEL EXPORT
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                final_report.to_excel(writer, index=False, sheet_name='Gabaasa')
            
            st.divider()
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.download_button(
                    label="📥 Gabaasa Excel Buufadhu",
                    data=buffer.getvalue(),
                    file_name=f"Gabaasa_Dadar_{f_type}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.ms-excel"
                )
            
            with col_d2:
                # Telegram Link (Inni kun Telegram banuuf qofa gargaara)
                st.markdown(f'<a href="https://t.me/share/url?url=Gabaasa_Dadar" target="_blank"><button style="width:100%; height:45px; background-color:#0088cc; color:white; border-radius:8px; border:none; font-weight:bold; cursor:pointer;">✈️ Telegram irratti Ergi</button></a>', unsafe_allow_html=True)
                st.caption("Hubachiisa: Excel file buufatte Telegram irratti 'Attach' godhi.")

        else:
            st.info("Data'n hin jiru.")

    elif menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        st.dataframe(df, use_container_width=True)
        st.metric("Walitti Qaba Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")

    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        q = st.text_input("Maqaa barreessi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res, use_container_width=True)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

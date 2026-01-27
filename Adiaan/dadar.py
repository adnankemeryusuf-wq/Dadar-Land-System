import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. STYLE & SETUP =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

# Halluu fi bareedina ati barbaaddu
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .main-title { color: #1b5e20; text-align: center; font-size: 35px; font-weight: bold; }
    .stButton>button { background-color: #1b5e20; color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

DATA_FILE = "dadar_reports.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Maamilaa', 'Araddaa', 'Gosa_Tajaajilaa', 'Ogeessa', 'Kaffaltii']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False)

# ================= 2. APP MAIN =================
st.markdown("<div class='main-title'>🏢 Bulchiinsa Lafaa Magaalaa Dadar</div>", unsafe_allow_html=True)

df = load_data()
menu = st.sidebar.radio("FILANNOO", ["📝 Galmeessi", "📊 Gabaasa", "🔍 Barbaadi"])

if menu == "📝 Galmeessi":
    st.subheader("📝 Odeeffannoo Tajaajilaa Galchi")
    
    # GOSA TAJAAJILAA HUNDA (Full List)
    tajaajila_hunda = [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "TOT (Turnover Tax)", "Jijjiirraa Maqaa (Gurgurtaa/Gift)", "Kaartaa Haaraa", 
        "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa", 
        "Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Ugura Mana Murtii", 
        "Waliigaltee Liqii Baankii", "Dhimma Dhala (Inheritance)", 
        "Waraqaa Ragaa (Clearance)", "Adabbii Ijaarsa Seeraan Alaa"
    ]

    with st.form("galmee_form"):
        c1, c2 = st.columns(2)
        maqaa = c1.text_input("Maqaa Maamilaa")
        araddaa = c2.text_input("Araddaa")
        
        # Akka ati barbaaddutti tajaajila baay'ee filachuun ni danda'ama
        tajaajiloota = st.multiselect("Gosa Tajaajilaa (Baay'ee filachuu ni dandeessa)", tajaajila_hunda)
        
        ogeessa = c1.text_input("Maqaa Ogeessaa")
        gatii = c2.number_input("Kaffaltii (ETB)", min_value=0.0)
        
        if st.form_submit_button("💾 GALMEESSI"):
            if maqaa and tajaajiloota:
                new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, ", ".join(tajaajiloota), ogeessa, gatii]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success("Milkiin galmeeffameera!")
            else:
                st.error("Maaloo odeeffannoo guuti!")

elif menu == "📊 Gabaasa":
    st.subheader("📊 Gabaasa Galii Waliigalaa")
    st.dataframe(df, use_container_width=True)
    st.write(f"### Waliigala Galii: {df['Kaffaltii'].sum():,.2f} ETB")

elif menu == "🔍 Barbaadi":
    st.subheader("🔍 Maamila Barbaadi")
    search = st.text_input("Maqaa galchi...")
    if search:
        res = df[df['Maqaa_Maamilaa'].str.contains(search, case=False, na=False)]
        st.write(res)

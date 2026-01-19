import streamlit as st
import pandas as pd
import os

# 1. SETUP - Bakka koodiin itti jalqabu
DATA_FILE = "dadar_data.txt"

# 2. DATA FUNCTIONS - Logic koodii kee
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            return pd.read_csv(DATA_FILE, sep="|")
        else:
            return pd.DataFrame(columns=["Guyyaa", "Maqaa", "Kaffaltii"])
    except Exception as e:
        st.error(f"Data dubbisuu irratti dogongorri uumame: {e}")
        return pd.DataFrame()

# 3. ACTION FUNCTIONS - Gochaalee akka Telegram erguu
def send_report(text):
    try:
        # Kodii Telegram kee asitti gala...
        # requests.post(...)
        st.success("Telegramitti ergameera!")
    except ConnectionError:
        st.error("Internet kee check godhadhu, Telegramitti hin ergamne.")
    except Exception as e:
        st.error(f"Dogongora biraa: {e}")

# 4. UI - Ijaarsa appilikeeshinii
st.title("Dadar Land Admin")
df = load_data()

# Barbaadi (Search) dabalata siif qopheessuu?
name_search = st.text_input("Maqaa barbaadi:")
if name_search:
    result = df[df['Maqaa'].str.contains(name_search, case=False)]
    st.write(result)

import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. SETUP & CONFIG =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

# Styling
st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 10px; border-top: 5px solid #2e7d32; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    try:
        if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
            return pd.DataFrame(columns=COL_NAMES)
        return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df_to_save):
    try:
        df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")
    except Exception as e:
        st.error(f"Data Save Error: {e}")

# ================= 3. UI SECTIONS =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Admin Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "2026":
            st.session_state.logged_in = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi/Edit", "Ba'i"])

    # --- REGISTRATION ---
    if menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        
        with st.form("reg_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            
            tajaajila = st.multiselect("Gosa Tajaajilaa", ["Kaartaa", "Gibira", "Liizii", "Ijaarsa"])
            kaffaltii = st.number_input("Kaffaltii Waliigalaa (ETB)", min_value=0.0)
            nagahee = st.file_uploader("Nagahee Scan (Image)", type=['jpg', 'png'])

            if st.form_submit_button("💾 Galmeessi"):
                if name and ogeessa and tajaajila:
                    # Save nagahee if exists
                    if nagahee:
                        path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(tajaajila), ogeessa, kaffaltii]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeen sirriitti kuufameera!")
                else:
                    st.warning("⚠️ Maaloo odeeffannoo guutuu galchi.")

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.title("📊 Raawwii Hojii")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("Baay'ina Galmee", len(df))
            c3.metric("Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            st.subheader("Raawwii Ogeeyyii")
            fig = px.bar(df, x='Maqaa_Ogeessa', y='Kafaltii_Taj', color='Maqaa_Ogeessa', title="Galii Ogeessa kanaan walitti qabame")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data'n galmeeffame hin jiru.")

    # --- LOGOUT ---
    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

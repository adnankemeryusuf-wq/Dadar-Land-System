import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px # Graph bareedaaf

# --- 1. SETTINGS ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

LOGO_PATH = "logo.png"
DATA_FILE = "dadar_final_report.txt"

# --- 2. CUSTOM CSS (Halluu fi Bifa Fuulaa) ---
st.markdown("""
    <style>
    /* Halluu duubaa fuula hundaatti */
    .stApp { background-color: #f4f7f9; }
    
    /* Header Box */
    .main-header {
        background: linear-gradient(90deg, #1f4e78, #0078d4);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Metric Card */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 6px solid #1f4e78;
    }
    
    /* Sidebar styling */
    .css-1d391kg { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING (Ragaa Dubbisuu) ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    # Ragaa file txt irraa gara Table (DataFrame) tti jijjiiru
    try:
        df = pd.read_csv(DATA_FILE, sep="|", header=None, 
                         names=["Date", "Name", "Phone", "Araddaa", "Service", "Officer", "Off_Phone", "Deadline", "Payment"])
        return df
    except:
        return pd.DataFrame()

df = load_data()

# --- 4. SIDEBAR (LOGO & MENU) ---
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=180)
    else:
        st.warning("Logo (logo.png) hin argamne")
    
    st.markdown("### 🏢 Dadar Land System")
    menu = st.radio("Fayyadami:", ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa Gadi Fageenyaa", "🚪 Logout"])
    st.markdown("---")
    st.info("System V7.0 - Dadar City Administration")

# --- 5. DASHBOARD MAIN PAGE ---
if menu == "🏠 Dashboard":
    # Header Area
    st.markdown("""
        <div class="main-header">
            <h1>Waajjira Bulchiinsa Lafaa Magaalaa Dadar</h1>
            <p>Sirna Bulchiinsa Ragaa Ammayyaa fi Qulqullina Qabu</p>
        </div>
        """, unsafe_allow_html=True)

    # Metrics Section (Baay'ina ragaa)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Waliigala Galmee", len(df) if not df.empty else 0)
    with col2:
        total_rev = df['Payment'].astype(float).sum() if not df.empty else 0
        st.metric("Waliigala Galii", f"{total_rev:,.0f} ETB")
    with col3:
        st.metric("Araddaawwan", df['Araddaa'].nunique() if not df.empty else 0)
    with col4:
        st.metric("Ogeessota", df['Officer'].nunique() if not df.empty else 0)

    st.markdown("---")

    # Graphs Section
    c1, c2 = st.columns([1.2, 1])
    
    if not df.empty:
        with c1:
            st.subheader("📊 Tajaajila Gosaan")
            fig = px.pie(df, names='Service', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("📈 Galmee Guyyaan")
            df['Date_Only'] = pd.to_datetime(df['Date']).dt.date
            trend = df.groupby('Date_Only').size().reset_index(name='Counts')
            fig2 = px.line(trend, x='Date_Only', y='Counts', markers=True)
            st.plotly_chart(fig2, use_container_width=True)
            
    else:
        st.info("Hanga ammaatti ragaan galmaa'e hin jiru. Maaloo 'Galmee Haaraa' irratti ragaa galchi.")

# --- 6. REGISTRATION PAGE (Kutaa Galmee) ---
elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Abbaa Dhimmaa Haaraa")
    # Koodii galmee ati duraan qabdu asitti itti fufa...
    st.write("Bakka kanatti 'Form' galmee kee isa duraa itti dabali.")

# --- 7. LOGOUT ---
elif menu == "🚪 Logout":
    st.success("Nagaatti turaa!")
    st.stop()

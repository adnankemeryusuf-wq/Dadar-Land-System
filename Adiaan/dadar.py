import streamlit as st
import pandas as pd
import os
import io
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# ================= 1. LUXURY UI DESIGN =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #f8faf8 0%, #e1eee2 100%);
    }
    
    /* Sidebar Luxury Style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #051f13 0%, #0c3d26 100%) !important;
        border-right: 3px solid #b8860b;
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; font-weight: 500; }

    /* Glassmorphism Cards */
    .luxury-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border-bottom: 5px solid #b8860b;
        transition: all 0.4s ease-in-out;
    }
    .luxury-card:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(27, 94, 32, 0.2);
    }
    .stat-val { color: #1b5e20; font-size: 35px; font-weight: 900; }
    .stat-label { color: #666; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #b8860b 0%, #8c6a06 100%);
        color: white !important;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        height: 50px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA CORE =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. APP INTERFACE =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.write("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<div style='background: white; padding: 50px; border-radius: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); border-top: 8px solid #b8860b;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #0c3d26;'>🏢 DADAR LAND</h1>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN SYSTEM"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
            else: st.error("Maaloo galmee kee sirreessi!")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    df = load_data()
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #b8860b;'>💎 PREMIER</h2>", unsafe_allow_html=True)
        menu = st.radio("MAIN MENU", ["📊 DASHBOARD", "📝 GALMEE HAARAA", "📈 GABAASA", "🔍 SEARCH/EDIT", "🚪 EXIT"])

    if menu == "📊 DASHBOARD":
        st.markdown("<h2 style='color: #0c3d26;'>📊 System Analytics</h2>", unsafe_allow_html=True)
        if not df.empty:
            # Stats Cards
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='luxury-card'><div class='stat-label'>Galii Waliigalaa</div><div class='stat-val'>{df['Kafaltii_Taj'].sum():,.2f}</div><p>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='luxury-card'><div class='stat-label'>Tajaajilamtoota</div><div class='stat-val'>{len(df)}</div><p>Total Customers</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='luxury-card'><div class='stat-label'>Ogeeyyii Aktiiwii</div><div class='stat-val'>{df['Maqaa_Ogeessa'].nunique()}</div><p>Staff Count</p></div>", unsafe_allow_html=True)
            
            # Charts Section
            st.write("<br>", unsafe_allow_html=True)
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("### 📈 Trendii Galii")
                line_fig = px.line(df, x='Guyyaa', y='Kafaltii_Taj', color_discrete_sequence=['#1b5e20'])
                st.plotly_chart(line_fig, use_container_width=True)
                
            with col_right:
                st.markdown("### 🍕 Gosa Tajaajilaa")
                pie_fig = px.pie(df, names='Gosa_Tajajjilaa', hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
                st.plotly_chart(pie_fig, use_container_width=True)
        else: st.info("Data'n galmeeffame hin jiru.")

    elif menu == "📝 GALMEE HAARAA":
        st.markdown("<h2 style='color: #0c3d26;'>📝 Galmee Haaraa Galchi</h2>", unsafe_allow_html=True)
        
        GATII_DICT = {
            "💰 GIBIRA & LIIDII": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)"],
            "📜 KAARTAA & RAGAA": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa"],
            "🏗 PILAANII & IJAARSA": ["Pilaanii Magaalaa", "Hayyama Ijaarsaa", "Humna Mahandisummaa", "Itti Fayyadama Lafaa"],
            "⚖️ SEERA & ADABBII": ["Ugura Mana Murtii", "Dhimma Dhala (Inheritance)", "Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"]
        }
        
        sel_cat = st.multiselect("Filannoo Ramaddii", list(GATII_DICT.keys()))
        tajaajiloota, kaffaltii_hunda = [], 0
        
        if sel_cat:
            cols = st.columns(len(sel_cat))
            for i, cat in enumerate(sel_cat):
                with cols[i]:
                    selected = st.multiselect(f"{cat}", GATII_DICT[cat])
                    for s in selected:
                        tajaajiloota.append(s)
                        gatii = st.number_input(f"Gatii {s}", min_value=0.0, key=f"p_{s}")
                        kaffaltii_hunda += gatii

        with st.form("luxury_form"):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Maamilaa Full Name")
            araddaa = c2.text_input("Araddaa / Qaxana")
            ogeessa = c1.text_input("Ogeessa Raawwate")
            guyyaa = c2.date_input("Guyyaa", datetime.now())
            
            if st.form_submit_button("💾 GALMEESSI FI NAGAHEE UUMI"):
                if maqaa and tajaajiloota:
                    new_data = [guyyaa.strftime('%d/%m/%Y'), maqaa, araddaa, "-", ", ".join(tajaajiloota), ogeessa, kaffaltii_hunda]
                    df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.balloons()
                    st.success(f"Maamilli {maqaa} galmeeffameera!")
                else: st.error("Maaloo odeeffannoo guuti!")

    elif menu == "🚪 EXIT":
        st.session_state.logged_in = False; st.rerun()

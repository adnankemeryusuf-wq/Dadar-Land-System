import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
import openpyxl
import plotly.express as px

# --- 1. QINDAA'INA ---
st.set_page_config(page_title="Dadar Land System V8.1", layout="wide", page_icon="🏢")

USER_NAME, PASS_WORD = "admin", "1234"
DB_FILE = "galmee_abbaa_dhimmaa.txt"
LOGO_PATH = "logo.png"

# --- 2. DATA LOADING ---
def load_data():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    data_list = []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = [x.split(":")[1].strip() for x in line.split("|")]
                data_list.append(parts)
        cols = ["ID", "Guyyaa", "Maqaa", "Bilbila", "Araddaa", "Wirtuu", "Dhimma", "Kartaa", "Lizi", "Beellama", "Ogeessa", "Status"]
        return pd.DataFrame(data_list, columns=cols)
    except: return pd.DataFrame()

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .search-box { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .header-box { background: linear-gradient(90deg, #1f4e78, #0078d4); color: white; padding: 25px; border-radius: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. APP LOGIC ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Kutaa Login (akkuma duraatti)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.subheader("Login - Dadar Land System")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
else:
    df = load_data()
    
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
        menu = st.radio("HOJJEDHU", ["🏠 Dashboard & Search", "📝 Galmee Haaraa", "✅ Xumurame Beeksisi", "📊 Gabaasa & Telegram", "🚪 Logout"])

    # --- MAIN PAGE: DASHBOARD & SEARCH ---
    if menu == "🏠 Dashboard & Search":
        st.markdown('<div class="header-box"><h1>Waajjira Lafaa Magaalaa Dadar</h1></div>', unsafe_allow_html=True)
        st.write("")

        # 🔍 SEARCH SECTION
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        search_query = st.text_input("🔍 Abbaa dhimmaa barbaadi (Maqaa ykn Bilbila galchi):", "")
        st.markdown('</div>', unsafe_allow_html=True)

        if not df.empty:
            # Filtering Logic
            filtered_df = df[
                df['Maqaa'].str.contains(search_query, case=False, na=False) | 
                df['Bilbila'].str.contains(search_query, na=False) |
                df['ID'].str.contains(search_query, na=False)
            ]

            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Waliigala Galmee", len(df))
            c2.metric("Argaman (Filtered)", len(filtered_df))
            rev = filtered_df['Kartaa'].astype(float).sum() + filtered_df['Lizi'].astype(float).sum()
            c3.metric("Galii (Filtered)", f"{rev:,.0f} ETB")

            st.markdown("---")
            
            # Display Table
            if not filtered_df.empty:
                st.subheader("📋 Ragaalee Galmee")
                st.dataframe(filtered_df, use_container_width=True)
                
                # Chart logic
                fig = px.bar(filtered_df, x="Araddaa", title="Baay'ina Galmee Araddaan", color="Dhimma")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Ragaan '"+search_query+"' jedhu hin argamne.")
        else:
            st.info("Hanga ammaatti ragaan galmaa'e hin jiru.")

    # --- Kutaawwan biroo (Registration, SMS, Telegram) akkuma koodii kee duraatti itti fufu ---
    elif menu == "📝 Galmee Haaraa":
        st.subheader("Galmee Haaraa")
        # ... (Koodii kee isa duraa as galchi)
        st.info("Koodiin galmee asitti itti fufa.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime

# --- CONFIGURATION TELEGRAM ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: rgba(255, 255, 255, 0.9); border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit", "Ba'i"])

    df = load_data()

    # --- 📝 GALMEE HAARAA (Simplified for space, use your existing form here) ---
    if menu == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Tajaajilaa Galmeessi")
        # (Your existing form code goes here...)

    # --- 🔍 BARBAADI / EDIT / DELETE ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi, Fooyyessi ykn Haqi")
        search_q = st.text_input("Maqaa abbaa dhimmaa barreessi...")
        
        if search_q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search_q, case=False, na=False)]
            
            if not results.empty:
                for idx, row in results.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} ({row['Guyyaa']})"):
                        col_edit, col_del = st.columns(2)
                        
                        # EDIT FORM
                        with col_edit:
                            st.info("Fooyyessi")
                            new_name = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                            new_ara = st.text_input("Araddaa", row['Araddaa'], key=f"a_{idx}")
                            new_fee = st.number_input("Kafaltii", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                            
                            if st.button("💾 Save Changes", key=f"save_{idx}"):
                                df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_name
                                df.at[idx, 'Araddaa'] = new_ara
                                df.at[idx, 'Kafaltii_Taj'] = new_fee
                                save_data(df)
                                st.success("✅ Fooyyeffameera!")
                                st.rerun()

                        # DELETE ACTION
                        with col_del:
                            st.warning("Haqi")
                            st.write("Galmee kana haquu ni barbaaddaa?")
                            if st.button("🗑️ Haqi (Delete)", key=f"del_{idx}"):
                                df = df.drop(idx)
                                save_data(df)
                                st.error("❌ Galmeen haqameera!")
                                st.rerun()
            else:
                st.warning("Nama maqaa kanaan galmeeffame hin arganne.")

    # --- 📈 GABAASA (Existing code) ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Calalame")
        # (Your existing report/Telegram code here...)

    elif menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        st.dataframe(df, use_container_width=True)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

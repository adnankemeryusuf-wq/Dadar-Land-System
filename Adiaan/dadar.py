import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURATION & STYLE ---
LOGO_PATH = "Adiaan/logo.png"  # Maqaa logoo keessanii sirriitti galchaa

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# CSS Interface bareechisuuf
st.markdown("""
    <style>
    /* Background fuula Login */
    .stApp {
        background: linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%);
    }
    /* Box Login gidduu */
    div.stButton > button:first-child {
        background-color: #2e7d32;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    /* Sidebar Halluu */
    [data-testid="stSidebar"] {
        background-color: #1b5e20;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. LOGIN PAGE (GIRAAFIKII BAREEDAA) ---
if not st.session_state.logged_in:
    # Fuula giddu-galeessa gochuuf column 3 fayyadamna
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.write("") # Space
        st.write("")
        # Box Login uumuu
        with st.container():
            # LOGOO DABALUU
            if os.path.exists(LOGO_PATH):
                # Logoo giddu-galeessa gochuuf
                _, img_col, _ = st.columns([1, 2, 1])
                img_col.image(LOGO_PATH, width=120)
            
            st.markdown("""
                <h2 style='text-align:center; color: #1b5e20; font-family: sans-serif; margin-bottom: 0px;'>
                    Bulchiinsa Magaalaa Dadar
                </h2>
                <p style='text-align:center; color: #4caf50; font-weight: bold;'>
                    Customer Registration System
                </p>
                <hr style='border: 1px solid #2e7d32;'>
            """, unsafe_allow_html=True)

            u = st.text_input("👤 Username", placeholder="Maqaa keessan galchaa")
            p = st.text_input("🔑 Password", type="password", placeholder="Fungulaa keessan")
            
            st.write("") # Space
            if st.button("SEENI"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.success("Milkiin seentaniittu!")
                    st.rerun()
                else:
                    st.error("Username ykn Password dogoggora!")

# --- 4. MAIN APP (LOGGED IN) ---
else:
    # Sidebar Interface
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=80)
        st.title("Dadar Land Admin")
        st.write(f"📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}")
        st.write("---")
        
        menu = st.radio("FILANNOO", 
                        ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit", "Ba'i"])
        
        st.write("---")
        if st.button("🚪 Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #1b5e20;'>📊 Dashboard Tajaajilaa</h2>", unsafe_allow_html=True)
        st.divider()
        
        # Fakkeenyaaf card-oota Dashboard (Koodii keessan isa duraa asitti deebisaa)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("💰 Waliigala Galii")
            st.subheader("0.00 ETB")
        with c2:
            st.success("👥 Maamiltoota")
            st.subheader("0")
        with c3:
            st.warning("👷 Ogeeyyii")
            st.subheader("0")

    # --- MENUWWAN KAAN ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa")
        # Formii keessan asitti itti fufa...

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

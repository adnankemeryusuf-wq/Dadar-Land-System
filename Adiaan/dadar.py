import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. CONFIGURATION & LOGO =================
# Logo path (Suuraa kee folder 'Adiaan' keessa jiru)
LOGO_PATH = "Adiaan/logo.png" 

st.set_page_config(
    page_title="Dadar Land Admin System",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢",
    layout="wide"
)

# ================= 2. STYLE (HALLUU OROMIYAA) =================
st.markdown(f"""
    <style>
    /* Sidebar style */
    [data-testid="stSidebar"] {{
        background-color: #1b5e20 !important;
        border-right: 5px solid #ff0000;
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    
    /* Header Style */
    .stHeader {{ background-color: #1b5e20; }}
    h1, h2, h3 {{ color: #1b5e20 !important; }}
    
    /* Login Box */
    .login-container {{
        text-align: center;
        padding: 20px;
        border: 2px solid #1b5e20;
        border-radius: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. MAIN APP LOGIC =================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN PAGE (LOGO WAJJIRAA KEESSA JIRU) ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150) # Logo login irratti
        else:
            st.warning("Logo'n hin argamne! 'Adiaan/logo.png' keessa kaa'i.")
            
        st.header("Waajjira Bulchiinsa Lafa Magaalaa Dadar")
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Username ykn Password dogoggora!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- AUTHENTICATED APP ---
else:
    # Sidebar Logo
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100) # Logo sidebar irratti
        st.markdown("### Dadar City Land Office")
        st.divider()
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee & Scan", "🔍 Barbaadi"])
        
        if st.button("🚪 Ba'i"):
            st.session_state.logged_in = False
            st.rerun()

    # --- Content ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        st.info("Baga nagaan dhuftan, sirna bulchiinsa lafaatti.")

    elif menu == "📝 Galmee & Scan":
        st.header("📝 Galmee fi Scan Sanadaa")
        # Koodii galmee asitti itti fufa...

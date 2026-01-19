import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. CONFIGURATION & LOGO =================
LOGO_PATH = "Adiaan/logo.png" 

st.set_page_config(
    page_title="Dadar Land Admin System",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢",
    layout="wide"
)

# ================= 2. STYLE (HALLUU #1B5E20) =================
st.markdown(f"""
    <style>
    /* 1. Background appii guutuu */
    .stApp {{
        background-color: #f4f7f6;
    }}

    /* 2. Sidebar (Bitaa) - Halluu #1b5e20 guutuu */
    [data-testid="stSidebar"] {{
        background-color: #1b5e20 !important;
        border-right: 5px solid #ff0000; /* Sarara Diimaa Oromiyaa */
    }}
    
    /* Barreeffama Sidebar adii gochuuf */
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    /* 3. Mata duree (Headers) */
    h1, h2, h3 {{
        color: #1b5e20 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    /* 4. Buttoonii (Buttons) */
    .stButton>button {{
        background-color: #1b5e20;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: #2e7d32;
        color: #ffd700; /* Halluu Warqee */
        border: 1px solid #ffd700;
    }}

    /* 5. Kaardiiwwan Gabaasaa (Metric Cards) */
    [data-testid="stMetricValue"] {{
        color: #1b5e20 !important;
        font-weight: bold;
    }}

    /* 6. Formiiwwan (Input Fields) */
    div.stForm {{
        border: 2px solid #1b5e20;
        border-radius: 15px;
        padding: 20px;
        background-color: white;
    }}

    /* 7. Login Box Style */
    .login-container {{
        text-align: center;
        padding: 30px;
        border: 2px solid #1b5e20;
        border-radius: 15px;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. MAIN APP LOGIC =================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        else:
            st.warning("Logo'n 'Adiaan/logo.png' keessa hin jiru.")
            
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
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
        st.markdown("### Dadar City Land Office")
        st.divider()
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee & Scan", "🔍 Barbaadi"])
        
        if st.button("🚪 Ba'i"):
            st.session_state.logged_in = False
            st.rerun()

    # --- Content Sections ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        col1, col2 = st.columns(2)
        col1.metric("Waliigala Galii", "500,000 ETB")
        col2.metric("Maamiltoota", "1,240")
        st.info("Baga nagaan dhuftan, sirna bulchiinsa lafaatti.")

    elif menu == "📝 Galmee & Scan":
        st.header("📝 Galmee fi Scan Sanadaa")
        with st.form("my_form"):
            st.write("Odeeffannoo maamilaa asitti galchi")
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            tajaajila = st.selectbox("Gosa Tajaajilaa", ["Kaartaa", "Liizii", "Gibira", "Waliigala"])
            sanada = st.file_uploader("Sanada Scan Godhame (Image/PDF)", type=["png", "jpg", "pdf"])
            if st.form_submit_button("💾 Save"):
                st.success(f"Galmeen {maqaa} milkiin kuufameera!")

    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        st.text_input("Maqaa maamilaa barreessi...")

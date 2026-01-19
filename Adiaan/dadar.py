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
import streamlit as st

# CSS Style Halluu #1b5e20 irratti hundaa'e
st.markdown("""
    <style>
    /* 1. Background appii guutuu */
    .stApp {
        background-color: #f4f7f6;
    }

    /* 2. Sidebar (Bitaa) - Halluu #1b5e20 guutuu */
    [data-testid="stSidebar"] {
        background-color: #1b5e20 !important;
    }
    
    /* Barreeffama Sidebar adii gochuuf */
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* 3. Mata duree (Headers) */
    h1, h2, h3 {
        color: #1b5e20 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 4. Buttoonii (Buttons) */
    .stButton>button {
        background-color: #1b5e20;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #2e7d32; /* Yeroo tuqamu xiqqoo ifa */
        color: #ffd700; /* Halluu Warqee (Gold) */
        border: 1px solid #ffd700;
    }

    /* 5. Kaardiiwwan Gabaasaa (Metric Cards) */
    [data-testid="stMetricValue"] {
        color: #1b5e20 !important;
        font-weight: bold;
    }

    /* 6. Formiiwwan (Input Fields) */
    div.stForm {
        border: 2px solid #1b5e20;
        border-radius: 15px;
        padding: 20px;
        background-color: white;
    }
    
    /* 7. Progress Bar fi Checkbox */
    .stProgress > div > div > div > div {
        background-color: #1b5e20;
    }
    </style>
    """, unsafe_allow_html=True)

# Fakkeenya itti fayyadamaa
st.title("🏢 Bulchiinsa Lafa Magaalaa")
st.sidebar.header("Dadar Admin")
st.sidebar.button("Galmee Haaraa")

col1, col2 = st.columns(2)
col1.metric("Waliigala Galii", "500,000 ETB")
col2.metric("Maamiltoota", "1,240")

with st.form("my_form"):
    st.write("Odeeffannoo asitti galchi")
    st.text_input("Maqaa")
    st.form_submit_button("💾 Save")
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


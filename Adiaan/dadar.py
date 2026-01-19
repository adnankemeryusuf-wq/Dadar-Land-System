import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. SETTINGS & STYLE =================
UPLOAD_DIR = "Sanadoota_Maamilaa"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

st.set_page_config(page_title="Dadar Land Admin", layout="wide")

# Halluu Mootummaa Naannoo Oromiyaa fi Style
st.markdown("""
    <style>
    /* Sidebar: Magaariisa Dukkanaawaa */
    [data-testid="stSidebar"] {
        background-color: #1b5e20 !important;
        border-right: 5px solid #ff0000; /* Sarara Diimaa */
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Headers: Halluu #1b5e20 */
    h1, h2, h3 { color: #1b5e20 !important; }

    /* Buttons: Halluu Diimaa fi Magaariisa */
    .stButton>button {
        background-color: #1b5e20;
        color: white;
        border-radius: 8px;
        border: 2px solid #ffffff;
    }
    .stButton>button:hover {
        background-color: #ff0000;
        color: white;
    }

    /* Cards */
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-bottom: 4px solid #ff0000;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. MAIN APP =================

st.sidebar.title("🌳 Dadar Admin")
st.sidebar.markdown("---")
menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee & Scan", "🔍 Barbaadi"])

if menu == "📊 Dashboard":
    st.title("📊 Dashboard Waliigalaa")
    # Fakkeenyaaf card gabaabaa
    st.markdown("""
        <div class='card'>
            <h3>Baga Nagaan Dhuftan!</h3>
            <p>Sirna Bulchiinsa Lafa Magaalaa Dadar</p>
        </div>
    """, unsafe_allow_html=True)

elif menu == "📝 Galmee & Scan":
    st.header("📝 Galmee Maamilaa fi Sanada Scan Gochuu")
    
    with st.form("galmee_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
        ara = col2.text_input("Araddaa")
        gosa = st.selectbox("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa"])
        
        # --- UPLOAD SECTION ---
        st.markdown("### 📄 Sanada Scan Ta'e Dabali")
        uploaded_file = st.file_uploader("Sanada (JPG/PNG/PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        submit = st.form_submit_button("💾 Galmeessi")
        
        if submit:
            if maqaa and uploaded_file:
                # Maqaa file-ichaa jijjiiruu (Maqaa_Maamilaa_Guyyaa)
                file_ext = uploaded_file.name.split('.')[-1]
                file_name = f"{maqaa.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
                save_path = os.path.join(UPLOAD_DIR, file_name)
                
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ Galmeen {maqaa} kuufameera! Sanadni asitti kuufame: {save_path}")
            else:
                st.error("Maaloo maqaa fi sanada Scan godhame galchi!")

elif menu == "🔍 Barbaadi":
    st.header("🔍 Sanada Barbaadi")
    search_name = st.text_input("Maqaa maamilaa barreessi...")
    if search_name:
        # Folder keessa barbaaduu
        files = [f for f in os.listdir(UPLOAD_DIR) if search_name.replace(' ', '_').lower() in f.lower()]
        if files:
            for f in files:
                st.write(f"📄 {f}")
                with open(os.path.join(UPLOAD_DIR, f), "rb") as file:
                    st.download_button(f"📥 Buufadhu (Download)", file, file_name=f)
        else:
            st.warning("Sanadni maqaa kanaan wal qabatu hin argamne.")

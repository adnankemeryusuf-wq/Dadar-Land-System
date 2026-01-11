import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- QINDAA'INA FUULA (Page Config) ---
st.set_page_config(
    page_title="Bulchiinsa Lafaa Dadar",
    page_icon="🏢",
    layout="wide"
)

# --- CSS Bifa Bareedaa (Custom Styling) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        background-color: #1f4e78;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    h1 {
        color: #1f4e78;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (LOGO FI MENU) ---
with st.sidebar:
    # Bakka "logo.png" jedhu irratti maqaa file logo keetii galchi
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.warning("Logo (logo.png) hin argamne. File logo keetii folder koodiin jiru keessa kaayi.")
    
    st.title("Dadar Land Office")
    st.markdown("---")
    menu = st.radio("Gara fuula kanatti deemi:", ["Fuula Jalqabaa", "Galmee Abbaa Dhimmaa", "Gabaasa Ilaali"])

# --- FUULA JALQABAA ---
if menu == "Fuula Jalqabaa":
    st.title("🏢 Bulchiinsa Lafaa Magaalaa Dadar")
    st.write("Baga nagaaan gara appilikeeshinii bulchiinsa lafaa magaalaa Dadar dhuftan.")
    st.image("https://via.placeholder.com/800x300.png?text=Baga+Nagaaan+Dhuftan", use_column_width=True)

# --- GALMEE ABBAA DHIMMAA ---
elif menu == "Galmee Abbaa Dhimmaa":
    st.header("📝 Galmee Abbaa Dhimmaa Haaraa")
    
    with st.container():
        with st.form("my_form"):
            col1, col2 = st.columns(2)
            with col1:
                maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
                bilbila = st.text_input("Lakk. Bilbilaa")
            with col2:
                tajaajila = st.selectbox("Gosa Tajaajilaa", ["Kartaa", "Jijjiirraa Maqaa", "Lizio", "Gibira"])
                ogeessa = st.text_input("Maqaa Ogeessa Hordofuu")
            
            submit = st.form_submit_button("Galmeessi")
            
            if submit:
                if maqaa and bilbila:
                    st.success(f"Abbaan dhimmaa {maqaa} galmeeffameera!")
                else:
                    st.error("Maaloo, odeeffannoo guutuu galchi.")

# --- GABAASA ILAALI ---
elif menu == "Gabaasa Ilaali":
    st.header("📊 Gabaasa Galmee")
    st.info("Ragaan asitti mul'ata.")

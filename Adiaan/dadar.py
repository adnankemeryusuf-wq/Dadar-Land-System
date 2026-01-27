import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png" 
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"

# ================= 2. PDF GENERATOR (CLEARANCE) =================
def create_clearance_pdf(name, araddaa, ogeessa):
    pdf = FPDF()
    pdf.add_page()
    # Border
    pdf.rect(5, 5, 200, 287)
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 90, 10, 30)
    
    pdf.set_y(45)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", 0, 1, 'C')
    pdf.cell(0, 10, "WAJJIRA LAFA FI MIIDHAGSINA MAGAALAA", 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'BU', 14)
    pdf.cell(0, 10, "WARAQAA QULQULLUMMAA (CLEARANCE)", 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 12)
    text = f"""Maqaan Abbaa Qabiyyee: {name}
Araddaa: {araddaa}
Guyyaa: {datetime.now().strftime('%d/%m/%Y')}

Qabiyyeen armaan olitti ibsame kun kaffaltii gibiraa, liizii fi kaffaltii tajaajilaa mootummaa irraa jiru hunda xumuruu isaa fi ugura mana murtii kamirraayyuu bilisa ta'uu isaa ni mirkaneessina."""
    
    pdf.multi_cell(0, 10, text)
    pdf.ln(20)
    pdf.cell(0, 10, f"Ogeessa Mirkaneesse: {ogeessa} ________________", 0, 1, 'L')
    pdf.cell(0, 10, "Mallattoo fi Chaappaa: ________________", 0, 1, 'L')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. UI STYLE & LOGIN =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Centering the Login
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div style="background:white; padding:30px; border-radius:15px; border-top:8px solid #2e7d32; text-align:center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.title("Dadar Land Admin")
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # ================= 4. MAIN SYSTEM =================
    menu = st.sidebar.radio("FILANNOO", ["📝 Galmee & Clearance", "📊 Dashboard", "📈 Gabaasa", "Logout"])
    
    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    elif menu == "📝 Galmee & Clearance":
        st.title("📝 Galmee Tajaajilaa fi Qulqullummaa")
        
        with st.form("main_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c1.text_input("Araddaa")
            qax = c2.text_input("Qaxana")
            og = c2.text_input("Maqaa Ogeessaa")
            
            gosa = st.selectbox("Gosa Tajaajilaa", ["Waraqaa Qulqullummaa (Clearance)", "Gibira Baaxii Gooroo", "TOT 2%", "Kaartaa Haaraa"])
            fee = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            
            submitted = st.form_submit_button("💾 GALMEESSI & XUMURI")
            
            if submitted and name and og:
                final_fee = fee * 0.02 if "TOT" in gosa else fee
                # Save data
                new_data = f"{datetime.now().strftime('%d/%m/%Y')}|{name}|{ara}|{qax}|{gosa}|{og}|{final_fee}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(new_data)
                
                # Success Message
                st.success(f"✅ {gosa} Galmeeffameera!")
                
                # If Clearance, show download button
                if "Clearance" in gosa:
                    pdf_data = create_clearance_pdf(name, ara, og)
                    st.download_button("📥 Waraqaa Qulqullummaa (PDF) Buufadhu", pdf_data, f"Clearance_{name}.pdf", "application/pdf")

    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        # Dashboard code logic as before...
        st.info("Galii fi ragaalee asitti dhiyeessi.")

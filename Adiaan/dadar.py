import streamlit as st
import pandas as pd
import os, io, requests, shutil
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURATION ---
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"

# --- HELPER FUNCTIONS ---
def send_telegram_report(excel_data, caption):
    """Excel fi Gabaasa Telegramitti erguu"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': ('Gabaasa_Dadar.xlsx', excel_data)}
    data = {'chat_id': CHAT_ID, 'caption': caption}
    try:
        res = requests.post(url, files=files, data=data)
        return res.status_code == 200
    except:
        return False

# ================= DASHBOARD WITH PLOTLY =================
def show_dashboard(df):
    st.subheader("📈 Raawwii Galii Ji'aan")
    
    # Data qindeessuu
    monthly_data = df.groupby("Ji'a")["Kafaltii_Taj"].sum().reset_index()
    
    # Plotly Chart (Modern & Interactive)
    fig = px.area(monthly_data, x="Ji'a", y="Kafaltii_Taj", 
                  title="Guraandhala - Hagayya",
                  color_discrete_sequence=['#2e7d32'])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ================= PDF WITH CLEANUP =================
def create_safe_pdf(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # ... (Koodii PDF isaa akkuma kanaan duraa)
    
    pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
    
    # Cleanup temp images (yoo uumaman)
    for tmp_file in ["temp_logo_l.png", "temp_logo_r.png"]:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
            
    return pdf_output

# ================= ADVANCED REPORTING =================
def show_advanced_reports(df):
    st.header("📈 Gabaasa Bal'aa")
    
    # Excel Export with BytesIO
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Gabaasa')
    excel_data = output.getvalue()

    c1, c2 = st.columns(2)
    c1.download_button("📥 Excel Buusi", excel_data, "Gabaasa.xlsx")
    
    if c2.button("✈️ Telegramitti Ergi"):
        total = df['Kafaltii_Taj'].sum()
        msg = f"📊 Gabaasa Dadar Land Admin\n📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}\n💰 Waliigala Galii: {total:,.2f} ETB"
        if send_telegram_report(excel_data, msg):
            st.success("✅ Gabaasni Telegramitti Ergameera!")
        else:
            st.error("❌ Erguun hin danda'amne. Token/ChatID sakatta'i.")

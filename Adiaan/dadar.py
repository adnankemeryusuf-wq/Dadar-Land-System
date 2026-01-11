import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
SMS_URL = "http://10.181.252.6:8082/send"
DEVICE_ID = "1"
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

# --- 2. CSS STYLE (MODERN UI) ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .header-box { 
        text-align: center; 
        padding: 30px; 
        background: linear-gradient(135deg, #1f4e78, #2e75b6); 
        color: white; 
        border-radius: 15px; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stMetric { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.05); 
        border-bottom: 4px solid #1f4e78;
    }
    .login-card { 
        max-width: 450px; margin: auto; padding: 40px; 
        background: white; border-radius: 20px; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.1); 
    }
    .footer-sign { text-align: center; margin-top: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKSHIINIIWWAN ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_draw_color(31, 78, 120)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)

    # Logo
    if LOGO_PATH:
        pdf.image(LOGO_PATH, x=135, y=15, w=25)
    
    pdf.ln(35)
    
    # Title - Afaan Oromoo
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(31, 78, 120)
    pdf.cell(0, 15, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
    
    # Title - English (Sarara dogoggora qaba ture)
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(100, 100, 100) # Sararri kun ammaa mallattoo ')' qaba
    pdf.cell(0, 10, 'ANNUAL AWARD CERTIFICATE', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    
    # Content
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, f"Badhaasni kun ogeessa kabajamaa:", ln=True, align='C')
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 15, name.upper(), ln=True, align='C')
    
    pdf.set_font('Arial', '', 14)
    text_oromo = f"Waggaa {year} keessa tajaajila quubsaa fi gahumsa qabuun hojjechuun badhaasa {rank}ffaa ta'uu keessaniif qophaa'e."
    pdf.multi_cell(0, 10, text_oromo, align='C')
    
    # Signatures
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_xy(40, 160)
    pdf.cell(100, 7, "Obbo Aqiil Abdujaliil", ln=True, align='L')
    pdf.set_font('Arial', '', 10)
    pdf.set_x(40)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa / Office Head", ln=True, align='L')

    return pdf.output(dest='S').encode('latin-1')
   pdf.set_text_color(100, 100, 100)


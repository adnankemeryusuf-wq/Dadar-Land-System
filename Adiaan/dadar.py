import streamlit as st
import os
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
from fpdf import FPDF
import io

# --- 1. QINDAYYII BU'URAA ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png"

# Telegram API Config
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

# --- FUNKSHINOOTA GARGAARAA ---
def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, data=payload)
    except: st.error("Ergaa Telegram erguun hin danda'amne.")

def send_telegram_file(df, filename, caption):
    csv_data = df.to_csv(index=False).encode('utf-8')
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    files = {'document': (filename, csv_data)}
    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
    try: requests.post(url, data=data, files=files)
    except: st.error("Faayila Telegram erguun hin danda'amne.")

# --- 2. SARTIIFIKETA (Signature included) ---
def generate_certificate(expert_name, total_served, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Double Gold)
    pdf.set_line_width(1.5)
    pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200)
    pdf.set_line_width(0.5)
    pdf.rect(8, 8, 281, 194)
    
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=130, y=12, w=35)
    
    pdf.ln(40)
    pdf.set_font('Arial', 'B', 40)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_font('Arial', 'I',

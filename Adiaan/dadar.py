import streamlit as st
import os
import pandas as pd
import requests
import io
from datetime import datetime
from fpdf import FPDF

# --- 1. QINDAYYII ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']

# Telegram API
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

# --- 2. FUNKSHINOOTA ---
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
        return df
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# --- 3. REPORT GENERATORS ---
def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Gabaasa')
    return output.getvalue()

def create_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Gabaasa Waajjira Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='R')
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 8, "Maqaa", 1, 0, 'C', True)
    pdf.cell(30, 8, "Araddaa", 1, 0, 'C', True)
    pdf.cell(40, 8, "Gosa", 1, 0, 'C', True)
    pdf.cell(40, 8, "Ogeessa", 1, 0, 'C', True)
    pdf.cell(30, 8, "Kafaltii", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 9)
    for _, row in df.iterrows():
        pdf.cell(40, 7, str(row['Maqaa'])[:20], 1)
        pdf.cell(30, 7, str(row['Araddaa']), 1)
        pdf.cell(40, 7, str(row['Gosa']), 1)
        pdf.cell(40, 7, str(row['Ogeessa']), 1)
        pdf.cell(30, 7, str(row['Kafaltii']), 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SARTIIFIKETA (New Style) ---
def generate_certificate(expert_name, total_served):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(1.5); pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200)
    
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, x=130, y=15, w=35)
    
    pdf.ln(45)
    pdf.set_font('Times', 'B', 45); pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', 'I', 18); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Badhaasa Gootummaa Hojii Waggaa", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Times', 'B', 35); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(15); pdf.set_font('Arial', '', 15); pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 10, f"Waggaa kanatti tajaajila saffisaa fi qulqullina qabuun Abbootii Dhimmaa {total_served} tajaajiluun bu'aa qabeessa ta'anii waan argamaniif beekamtii kanaan badhaafamaniiru.", align='C')
    
    # Signatures - Position Adjusted (Gadi buufameera)
    pdf.set_y(170) 
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 8, "__________________________", ln=0, align='C')
    pdf.cell(87, 8, "", ln=0)
    pdf.cell(100, 8, "__________________________", ln=1, align='C')
    
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, datetime.now().strftime("%d/%m/%Y"), ln=1, align='C')
    pdf.set_font('Arial', '', 11)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, "Guyyaa", ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. UI APP ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1, 1])
    with center:
        st.subheader("Login - Dadar Land")
        u =

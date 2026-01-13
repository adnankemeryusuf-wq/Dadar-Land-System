import streamlit as st
import pandas as pd
import os
import hashlib
import requests
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageOps

# ================= CONFIG =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

DATA_FILE = "dadar_final_report.txt"
USERS_FILE = "users.csv"
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

# --- ODEEFFANNOO TELEGRAM ---
TELEGRAM_TOKEN = "7864321234:AAH_F_XXXXXXXXXXXXX" # API Token kee galchi
TELEGRAM_CHAT_ID = "123456789"                   # Chat ID Manager-aa galchi

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

# Gatii Tajaajilaa (Asitti jijjiiruu dandeessa)
GATII_DICT = {
    "Ittii Fayyaddam": 50.0, 
    "Kartaa": 150.0, 
    "Jijjirra Maqaa": 200.0,
    "Dhimma Dangaa": 100.0, 
    "Dhimma Mana Murtii": 0.0, 
    "Ugura Mana Murtii": 50.0,
    "Uguraa Mana Murtii Kasuu": 50.0, 
    "Dorkka Liqii Bankii": 100.0, 
    "Dorkkaa Liqii Bankii Kasuu": 100.0
}

# ================= FUNCTIONS =================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([["admin", hash_password("123"), "admin"]], columns=["username", "password", "role"])
        df.to_csv(USERS_FILE, index=False)
    return pd.read_csv(USERS_FILE)

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_path, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": message, "parse_mode": "Markdown"}
            files = {"document": file}
            response = requests.post(url, data=payload, files=files)
            return response.status_code == 200
    except:
        return False

# ================= LOGO & CERTIFICATE FUNCTIONS =================
def get_circular_logo(path):
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        size = (400, 400)
        img = img.resize(size, Image.LANCZOS)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask)
        output = Image.new("RGB", size, (255, 255, 255))
        output.paste(img, mask=img.split()[3])
        return output
    return None

def generate_certificate(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(2); pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200) 
    circular_img = get_circular_logo(LOGO_PATH)
    if circular_img:
        pdf.image(circular_img, x=131, y=10, w=35)
    pdf.ln(35)
    pdf.set_font('Helvetica', 'B', 40)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.ln(5); pdf.set_font('Arial', 'I', 16); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, "Gootummaa Hojii Waggaa kan kennameef:", ln=True, align='C')
    pdf.

import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN")
CHAT_ID_MANAGER = os.getenv("CHAT_ID_MANAGER", "YOUR_CHAT_ID")
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
LOGO_PATH = "Adiaan/logo.png"

os.makedirs(NAGAHEE_DIR, exist_ok=True)

st.set_page_config(
    page_title="Dadar Land Customer Registration System",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢",
    layout="wide"
)

COL_NAMES = ['Guyyaa','Maqaa_Abbaa_Dhimmaa','Araddaa','Qaxana','Gosa_Tajajjilaa','Maqaa_Ogeessa','Kafaltii_Taj','Biometric_ID']
MONTH_ORDER = [...]
MONTH_MAP = {...}

# --- FUNCTIONS ---
def load_data(): ...
def save_data(df): ...
def send_to_telegram(file_data, file_name, caption): ...
def create_advanced_pdf(...): ...

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
...

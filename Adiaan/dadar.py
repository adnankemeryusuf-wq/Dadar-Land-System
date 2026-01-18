import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & SETUP =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "Adiaan/nagahee"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

    # Uploaders asitti ta'u
    menu = st.radio("FILANNOO", ["📝 Galmee & Clearance", "📊 Dashboard", "📈 Gabaasa"])

# 1. Kutaa Galmee
if menu == "📝 Galmee & Clearance":
    st.subheader("Galmee Tajaajilaa")
    # Form-ii kee asitti barreeffama...

# 2. Kutaa Dashboard
elif menu == "📊 Dashboard":
    st.subheader("Statistiksii Waajjiraa")
    # Metric-oota asitti agarsiisama...

# 3. Kutaa Gabaasa
elif menu == "📈 Gabaasa":
    st.subheader("Gabatee Gabaasaa")
    # Dataframe asitti agarsiisama...



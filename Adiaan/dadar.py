import os
import requests
from datetime import datetime
from collections import Counter
try:
    from ethiopian_date import EthiopianDateConverter 
except ImportError:
    EthiopianDateConverter = None

# Library check
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    from fpdf import FPDF
except ImportError:
    print("\n[!] Maaloo: 'pip install openpyxl requests fpdf ethiopian-date' godhaa.")

# --- CONFIGURATION ---
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700" 

# SMS Gateway Config
SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
DEVICE_ID = "1"  # Identify which phone/SIM (Usually 1 or 2)
SMS_URL = "http://10.181.252.6:8082/send" 

DATA_FILE = "dadar_final_report.txt"
OFFICE_HEAD = "Obbo Aqiil Abdujaalil" 
LOGO_PATH = "logo.png" 

# --- HELPER FUNCTIONS ---

def guyyaa_itophiyaa(year, month, day):
    """Converts G.C to E.C for official reports"""
    if EthiopianDateConverter:
        try:
            eth_year, eth_month, eth_day = EthiopianDateConverter.to_ethiopian(year, month, day)
            return f"{eth_day}/{eth_month}/{eth_year} E.C"
        except:
            pass
    return f"{day}/{month}/{year} G.C"

def send_sms(phone, message):
    """Sends SMS via Traccar/Android Gateway"""
    try:
        if phone.startswith('0'):
            phone = "+251" + phone[1:]
        
        payload = {
            'token': SMS_TOKEN,
            'device': DEVICE_ID, 
            'to': phone,
            'message': message
        }
        
        res = requests.post(SMS_URL, data=payload, timeout=10)
        if res.status_code == 200:
            print(f"[✓] SMS ergameera: {phone}")
            return True
        else:
            print(f"[!] SMS Error: {res.status_code}")
            return False
    except Exception as e:
        print(f"[!] Network Error: Check if Gateway App is running on your phone. {e}")
        return False

# --- CORE LOGIC ---

def uumi_sartifiketii(ogeessa, rank, waggaa):
    """Creates a professional Award PDF for top experts"""
    try:
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_draw_color(31, 78, 120); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
        
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, x=128, y=15, w=40)
            pdf.ln(45)
        else: pdf.ln(30)

        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 10, 'BULCHIINSA MAGAALAA DADAR', ln=True, align='C')
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 8, 'Wajjiira Lafa Bulchiinsa Magaalaa', ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 30); pdf.set_text_color(31, 78, 120)
        pdf.cell(0, 20, f'BADHAASA OGEESSA {rank}', ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 18)
        pdf.cell(0, 15, f"Sartifiketiin kun Ogeessa {ogeessa.upper()}f kan kenname,", ln=True, align='C')
        
        txt = (f"tajaajila mamiilaa haala bareedaa fi quubsaa ta'een waggaa {waggaa} "
               f"keessa kennaa turaniif tattaaffii isaaniif galateeffachuuf.")
        pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 10, txt, align='C')
        pdf.ln(20)
        
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 8, f"{OFFICE_HEAD}", ln=True, align='C')
        pdf.cell(0, 8, "Itti Gaafatamaa Wajjiraa", ln=True, align='C')
        
        f_name = f"Sartifiketii_{ogeessa.replace(' ', '_')}.pdf"
        pdf.output(f_name)
        return f_name
    except Exception as e: 
        print(f"Error PDF: {e}")
        return None

# ... [Reporting logic continues as in your draft] ...

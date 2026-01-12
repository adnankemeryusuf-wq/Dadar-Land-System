import os
import requests
from datetime import datetime
from collections import Counter

# Library-wwan mirkaneeffachuu
try:
    from ethiopian_date import EthiopianDateConverter 
except ImportError:
    EthiopianDateConverter = None

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    from fpdf import FPDF
except ImportError:
    print("\n[!] Maaloo: 'pip install openpyxl requests fpdf ethiopian-date' godhaa.")

# --- QINDAA'INA (CONFIG) ---
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700" 

SMS_TOKEN = "7b96636f-e286-4aae-ba20-b7dd310897db"
DEVICE_ID = "1" 
SMS_URL = "http://10.181.252.6:8082/send" 

DATA_FILE = "dadar_final_report.txt"
OFFICE_HEAD = "Obbo Aqiil Abdujaalil" 
LOGO_PATH = "logo.png" 

# --- HELPER FUNCTIONS ---

def guyyaa_itophiyaa(year, month, day):
    if EthiopianDateConverter:
        try:
            eth_year, eth_month, eth_day = EthiopianDateConverter.to_ethiopian(year, month, day)
            return f"{eth_day}/{eth_month}/{eth_year} E.C"
        except: pass
    return f"{day}/{month}/{year} G.C"

def send_sms(phone, message):
    try:
        if phone.startswith('0'): phone = "+251" + phone[1:]
        payload = {'token': SMS_TOKEN, 'device': DEVICE_ID, 'to': phone, 'message': message}
        res = requests.post(SMS_URL, data=payload, timeout=10)
        return res.status_code == 200
    except: return False

def send_telegram_file(file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, files={'document': f}, timeout=20)
    except: pass

# --- CORE LOGIC ---

def uumi_sartifiketii(ogeessa, rank, waggaa):
    try:
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_draw_color(31, 78, 120); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
        pdf.ln(30)
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 10, 'BULCHIINSA MAGAALAA DADAR', ln=True, align='C')
        pdf.set_font('Arial', 'B', 30); pdf.set_text_color(31, 78, 120)
        pdf.cell(0, 25, f'BADHAASA OGEESSA {rank}', ln=True, align='C')
        pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 18)
        pdf.cell(0, 15, f"Sartifiketiin kun Ogeessa {ogeessa.upper()}f kan kenname,", ln=True, align='C')
        txt = f"tajaajila waggaa {waggaa} keessa mamiilaaf kennaa turaniif galateeffachuuf."
        pdf.multi_cell(0, 10, txt, align='C')
        pdf.ln(20)
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 8, f"{OFFICE_HEAD}", ln=True, align='C')
        f_name = f"Sartifiketii_{ogeessa.replace(' ', '_')}.pdf"
        pdf.output(f_name)
        return f_name
    except: return None

def uumi_gabaasa_target(filter_type, value, label):
    if not os.path.exists(DATA_FILE): return
    wb = openpyxl.Workbook(); ws = wb.active
    ws.append(["Guyyaa", "Mamiila", "Araddaa", "Tajaajila", "Ogeessa", "Kafaltii"])
    
    ogeessota = []
    with open(DATA_FILE, "r") as f:
        for line in f:
            p = line.strip().split("|")
            dt = datetime.strptime(p[0], "%Y-%m-%d %H:%M")
            match = (filter_type=="guyyaa" and dt.strftime("%A")==value) or \
                    (filter_type=="jia" and dt.month==value) or \
                    (filter_type=="waggaa" and dt.year==value)
            if match:
                ws.append([p[0], p[1], p[2], p[5], p[6], p[10]])
                ogeessota.append(p[6])

    f_name = f"Gabaasa_{label}.xlsx"
    wb.save(f_name)
    send_telegram_file(f_name, f"📊 Gabaasa {label}")
    
    if filter_type == "waggaa":
        top = Counter(ogeessota).most_common(1)
        if top:
            sf = uumi_sartifiketii(top[0][0], "1ffaa", value)
            if sf: send_telegram_file(sf, f"📜 Badhaasa Ogeessa Waggaa: {top[0][0]}")

def galmeessi():
    print("\n--- GALMEE HAARAA ---")
    ad = input("Maqaa Mamiilaa: "); ar = input("Araddaa: "); wi = input("Wirtuu: ")
    bad = input("Bilbila Mamiilaa: "); gs = input("Gosa Tajaajilaa: ")
    og = input("Maqaa Ogeessaa: "); bog = input("Bilbila Ogeessaa: ")
    gb = input("Beellama (YYYY-MM-DD): "); sb = input("Sa'aatii: ")
    kafaltii = input("Waliigala Kafaltii (ETB): ") or "0"
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    data = f"{now}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|{bog}|{gb} {sb}|0|{kafaltii}\n"
    
    with open(DATA_FILE, "a") as f: f.write(data)
    
    # SMS & Notifications
    send_sms(bad, f"Kabajamaa {ad}, tajaajila {gs}af beellama {gb} qabattu. Ogeessa: {og}.")
    send_sms(bog, f"Ogeessa {og}, mamiila {ad} tajaajiluuf beellama {gb} qabdu.")
    print("\n[✓] Galmeeffameera!")

def barbaadi():
    print("\n--- BARBAADU (SEARCH) ---")
    maqaa = input("Maqaa mamiilaa galchi: ").lower

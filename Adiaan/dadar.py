
import csv
import os
import requests
from datetime import datetime

FILE_NAME = "galmee_lafaa.csv"

# --- KONFIGIREECHINII TRACCAR ---
TRACCAR_URL = "https://sms.traccar.org/api/send"
# Token kana Webisaayitii Traccar irraa 'User Settings' keessaa fidi
TRACCAR_API_TOKEN = "08a96817-22ab-4660-b866-b7647dbcbf82" 

# --- KONFIGIREECHINII TELEGRAM ---
TELE_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
ADMIN_CHAT_ID = "7329587700" 

# --- KUTAA LOGIN ---
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

def login():
    print("\n" + "*"*30 + "\n  W/B/L/M DADAR - LOGIN\n" + "*"*30)
    user = input("Username: ")
    pw = input("Password: ")
    return user == ADMIN_USER and pw == ADMIN_PASS

def ergaa_sms_traccar(bilbila, maqaa):
    """Traccar fayyadamee SMS dhugaa erga"""
    if not bilbila.startswith("+"):
        bilbila = "+251" + bilbila.lstrip("0")
        
    ergaa = f"Kabajamoo {maqaa}, galmeen keessan milkiin xumurameera. W/B/L/M Dadar."
    
    payload = {
        "to": bilbila,
        "message": ergaa
    }
    
    headers = {
        "Authorization": TRACCAR_API_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        # Timeout itti daballeera akka inni hin hanganne
        r = requests.post(TRACCAR_URL, json=payload, headers=headers, timeout=15)
        if r.status_code in [200, 201, 202]:
            print(f"[✓] SMS gara {bilbila} tti ergameera.")
        else:
            print(f"[!] SMS Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[!] Dogoggora Interneetii: {e}")

def galmeessi():
    print("\n--- GALMEE HAARAA GALMEESSI ---")
    headers_list = ["Maqaa AD", "Bilbila AD", "Gosa Tajaajilaa", "Ogeessa"]
    data = []
    for h in headers_list:
        data.append(input(f"{h}: "))
    
    # Save to CSV
    with open(FILE_NAME, mode='a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(data + [datetime.now()])

    print(f"\n[✓] Galmeeffameera!")
    # Ergaa ergi
    ergaa_sms_traccar(data[1], data[0])

def menu():
    while True:
        print("\n1. Galmee Haaraa\n2. Exit")
        ch = input("Filannoo: ")
        if ch == '1': galmeessi()
        elif ch == '2': break

if name == "main":
    if login():
        menu()
    else:
        print("Login kuffiseera!")


import os
import requests
from datetime import datetime, timedelta

# Library-wwan mirkaneeffachuu
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    import qrcode
except ImportError:
    print("\n[!] Maaloo Pydroid Terminal irratti: 'pip install openpyxl requests qrcode' godhaa.")

# --- QINDAA'INA (CONFIG) ---
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8586015354:AAEliISf-RtoeJ8anbVLapY3NBm7hz8dZWI"
CHAT_ID_MANAGER = "568248052" 
SMS_URL = "http://localhost:8082/" 
SMS_TOKEN = "08a96817-22ab-4660-b866-b7647dbcbf82"
DATA_FILE = "dadar_final_report.txt"

# --- FUNKSHIINIIWWAN ERGAA ---

def send_telegram(file_path, file_type="doc", caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/"
    url += "sendDocument" if file_type == "doc" else "sendPhoto"
    try:
        with open(file_path, 'rb') as f:
            payload = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
            files = {'document' if file_type == "doc" else 'photo': f}
            requests.post(url, data=payload, files=files, timeout=20)
    except: print(f"[!] Ergaan Telegram hin darbine.")

# --- FUNKSHIINII GABAASAA (EXCEL) ---

def uumi_excel(days, label):
    if not os.path.exists(DATA_FILE):
        print("[!] Ragaan kuufame hin jiru."); return
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = label
    headers = ["Guyyaa", "Abbaa Dhimmaa", "Gosa Tajaajilaa", "Ogeessa", "Beellama", "Waligala"]
    ws.append(headers)
    
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    now = datetime.now()
    total_revenue = 0
    count = 0
    
    with open(DATA_FILE, "r") as f:
        for line in f:
            p = line.strip().split("|")
            try:
                dt = datetime.strptime(p[0], "%Y-%m-%d %H:%M")
                if (now - dt).days <= days:
                    ws.append([p[0], p[1], p[5], p[6], p[8], p[15]])
                    total_revenue += float(p[15])
                    count += 1
            except: continue
            
    if count == 0:
        print(f"[!] Gabaasa {label} irratti ragaan argame hin jiru.")
        return

    file_name = f"Gabaasa_{label}.xlsx"
    wb.save(file_name)
    send_telegram(file_name, "doc", f"📊 Gabaasa {label}\n💰 Waligala Galii: {total_revenue} ETB\n📑 Baay'ina Galmee: {count}")
    print(f"[✓] Gabaasni {label} hoggantatti ergameera.")

# --- FUNCTION BARBAACHAA (SEARCH) ---

def barbaadi_galmee():
    """Maqaa abbaa dhimmaatiin ragaa barbaaduuf"""
    if not os.path.exists(DATA_FILE):
        print("[!] Ragaan galmaa'e hin jiru."); return
        
    maqaa = input("\nMaqaa Abbaa Dhimmaa barbaadu galchi: ").lower()
    found = False
    
    with open(DATA_FILE, "r") as f:
        for line in f:
            if maqaa in line.lower():
                p = line.strip().split("|")
                print("\n" + "*"*30)
                print(f"📅 Guyyaa: {p[0]}\n👤 AD: {p[1]}\n🛠️ Tajaajila: {p[5]}\n💰 Waligala: {p[15]} ETB")
                print("*"*30)
                found = True
    
    if not found:
        print(f"\n[!] Galmeen maqaa '{maqaa}' jedhuun jiru hin argamne.")

# --- NAVIGATION & OTHERS ---

def ilaali_galmee():
    if not os.path.exists(DATA_FILE): return
    with open(DATA_FILE, "r") as f: records = f.readlines()
    if not records: return
    
    idx = len(records) - 1
    while True:
        p = records[idx].strip().split("|")
        print(f"\n[{idx+1}/{len(records)}] AD: {p[1]} | Tajaajila: {p[5]} | Kafaltii: {p[15]} ETB")
        cmd = input("[N] Next | [B] Back | [E] Exit: ").lower()
        if cmd == 'n' and idx < len(records)-1: idx += 1
        elif cmd == 'b' and idx > 0: idx -= 1
        elif cmd == 'e': break


def galmeessi():
    print("\n--- GALMEE HAARAA ---")
    ad = input("Maqaa AD: "); bad = input("Bilbila AD: ")
    gs = input("Gosa Tajaajilaa: "); og = input("Maqaa Ogeessa: ")
    bog = input("Bilbila Ogeessa: "); gb = input("Beellama (YYYY-MM-DD): "); sb = input("Sa'aatii: ")
    
    k_vals = []
    for kt in ["Kartaa", "User", "Jij_Maqaa", "Lizio", "TOT", "Gibira"]:
        while True:
            v = input(f"{kt}: ") or "0"
            try: k_vals.append(float(v)); break
            except: print("[!] Maaloo lakkoofsa galchi!")
            
    waligala = sum(k_vals)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # QR Code
    qr_file = f"QR_{ad.replace(' ', '_')}.png"
    qrcode.make(f"AD: {ad}\nKafaltii: {waligala}\nBeellama: {gb}").save(qr_file)
    send_telegram(qr_file, "photo", f"✅ QR Haaraa: {ad}\n💰 Waligala: {waligala} ETB")
    
    # Save & SMS
    line = f"{now_str}|{ad}|-|-|{bad}|{gs}|{og}|{bog}|{gb} {sb}|{'|'.join(map(str, k_vals))}|{waligala}\n"
    with open(DATA_FILE, "a") as f: f.write(line)
    print(f"\n[✓] Galmeeffameera! Waligala: {waligala} ETB")

# --- MAIN LOOP ---

if name == "main":
    print("\n" + "*"*35 + "\n W/BULCHINSA LAFAA MAGAALAA DADAR\n" + "*"*35)
    u, p = input("User: "), input("Pass: ")
    if u == USER_NAME and p == PASS_WORD:
        while True:
            print("\n1. Galmee Haaraa (SMS + QR)")
            print("2. Gabaasa Excel (Hoggantatti Ergi)")
            print("3. Galmeewwan Hunda Ilaali (Next/Back)")
            print("4. Galmee Barbaadi (Search)")
            print("5. Exit")
            
            c = input("\nFilannoo kee: ")
            if c == '1': galmeessi()
            elif c == '2':
                print("\n1.Guyyaa | 2.Torbee | 3.Ji'aa | 4.Kurmaana | 5.Waggaa")
                f = input("Filadhu: ")
                days = {'1':1, '2':7, '3':30, '4':90, '5':365}.get(f, 0)
                if days: uumi_excel(days, "Gabaasa")
            elif c == '3': ilaali_galmee()
            elif c == '4': barbaadi_galmee()
            elif c == '5': break
    else: print("[!] Login Dogoggora!")




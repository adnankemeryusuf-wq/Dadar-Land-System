import os
import requests
import json
from datetime import datetime
from collections import Counter
from ethiopian_date import EthiopianDateConverter 

# Library-wwan mirkaneeffachuu
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from fpdf import FPDF
except ImportError:
    print("\n[!] Maaloo: 'pip install openpyxl requests fpdf ethiopian-date' godhaa.")

# --- QINDAA'INA (CONFIG) ---
USER_NAME = "admin"
PASS_WORD = "1234"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700" 

# SMS Gateway Config (Traccar/Android App)
SMS_TOKEN = "08a96817-22ab-4660-b866-b7647dbcbf82"
DEVICE_ID = "D2gwdbQERJim97FArrhdeh:APA91bGi6mG3iiqNOMOlU4A6hgV7PqrrpuDip8cxS54du5nEkDuCHRW3aBT1o9fY35sEhMzvUHNm_5qLkep0XVTsmWndNMLCY-WCBmMzH64-Kpvp3y_rUVQ"
SMS_URL = "http://10.181.252.6:8082/send" # IP kee kan amma argituun bakka buusi

DATA_FILE = "dadar_land_database.txt"
OFFICE_HEAD = "Obbo Aqiil Abdujaalil" 
LOGO_PATH = "logo.png" 

# --- FUNKSHIINIIWWAN GARGAARTUU ---

def guyyaa_itophiyaa(year, month, day):
    try:
        eth_year, eth_month, eth_day = EthiopianDateConverter.to_ethiopian(year, month, day)
        return f"{eth_day}/{eth_month}/{eth_year} E.C"
    except:
        return f"{day}/{month}/{year} G.C"

def send_ethio_sms(phone, message):
    """Traccar SMS Gateway fayyadamuun SMS dhugaa erga"""
    headers = {
        "Authorization": SMS_TOKEN,
        "Content-Type": "application/json"
    }
    
    if phone.startswith('0'):
        phone = "+251" + phone[1:]
    elif not phone.startswith('+'):
        phone = "+251" + phone
            
    payload = {
        "to": phone,
        "message": message,
        "device": DEVICE_ID
    }

    try:
        res = requests.post(SMS_URL, json=payload, headers=headers, timeout=12)
        if res.status_code in [200, 202]:
            print(f"[✓] SMS gara {phone} tti ergameera.")
            return True
        else:
            print(f"[!] Gateway Error: {res.status_code}")
            return False
    except Exception as e:
        print(f"[!] Network Error: {e}")
        return False

def send_telegram_file(file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, files={'document': f}, timeout=20)
    except: pass

# --- KUTAA DOOKUMANTIIWWANII ---

def uumi_sartifiketii(ogeessa, rank, waggaa):
    try:
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_draw_color(31, 78, 120); pdf.set_line_width(1.5); pdf.rect(10, 10, 277, 190)
        
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 10, 'BULCHIINSA MAGAALAA DADAR', ln=True, align='C')
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 8, 'Wajjiira Lafa Bulchiinsa Magaalaa', ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 30); pdf.set_text_color(31, 78, 120)
        pdf.cell(0, 20, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 16)
        pdf.cell(0, 15, f"Sartifiketiin kun Ogeessa kabajamaa {ogeessa.upper()}f", ln=True, align='C')
        
        txt = (f"tajaajila mamiilaa haala bareedaa fi quubsaa ta'een waggaa {waggaa} "
               f"kennaa turaniif badhaasa {rank} ta'uun qophaa'eef.")
        pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 8, txt, align='C')
        pdf.ln(20)
        
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 8, f"{OFFICE_HEAD}", ln=True, align='C')
        pdf.cell(0, 8, "Itti Gaafatamaa Wajjiraa", ln=True, align='C')
        
        f_name = f"Sartifiketii_{ogeessa.replace(' ', '_')}.pdf"
        pdf.output(f_name)
        return f_name
    except: return None

# --- KUTAA HOJII ---

def galmeessi():
    print("\n" + "="*15 + " GALMEE HAARAA " + "="*15)
    ad = input("Maqaa Abbaa Dhimmaa: ")
    bad = input("Bilbila AD: ")
    ar = input("Araddaa: ")
    wi = input("Wirtuu: ")
    gs = input("Gosa Tajaajilaa (Dhimma): ")
    og = input("Maqaa Ogeessaa: ")
    bog = input("Bilbila Ogeessaa: ")
    gb = input("Guyyaa Beellamaa (YYYY-MM-DD): ") or "2026-01-01"
    
    print("\n--- Kafaltiiwwan ---")
    k_vals = []
    for kt in ["Kartaa", "Lizi", "TOT", "Gibira", "Kan_Biro"]:
        v = input(f"{kt}: ") or "0"
        try: k_vals.append(float(v))
        except: k_vals.append(0.0)
            
    waligala = sum(k_vals)
    now = datetime.now()
    now_s = now.strftime("%Y-%m-%d %H:%M")
    id_sys = now.strftime("%f")[:4] # ID gabaabaa uumuuf
    
    # Data Format: ID|Date|Client|Phone|Aradda|Wirtuu|Service|Expert|ExpPhone|Deadline|Payments|Total|Status
    k_str = "/".join(map(str, k_vals))
    line = f"{id_sys}|{now_s}|{ad}|{bad}|{ar}|{wi}|{gs}|{og}|{bog}|{gb}|{k_str}|{waligala}|Pending\n"
    
    with open(DATA_FILE, "a") as f: f.write(line)

    # 1. SMS Ogeessaaf
    sms_og = f"Ogeessa {og}, Ajaja Safaraa: {ad}, Araddaa {ar}, Bilbila: {bad}. Maaloo itti dhihaadhaa."
    send_ethio_sms(bog, sms_og)

    # 2. SMS Abbaa Dhimmaaf
    sms_ad = f"Kabajamoo {ad}, tajaajila {gs}af ID:{id_sys} galmaa'eera. Ogeessi: {og}. W/B/L/M/Dadar."
    send_ethio_sms(bad, sms_ad)

    print(f"\n[✓] Galmeeffameera! ID: {id_sys}")

def notify_xumurame():
    print("\n--- DHIMMA XUMURAME BEEKSISU ---")
    id_barbaadu = input("ID abbaa dhimmaa galchi: ")
    sararoota = []
    found = False
    
    if not os.path.exists(DATA_FILE): return

    with open(DATA_FILE, "r") as f:
        for sarara in f:
            p = sarara.strip().split("|")
            if len(p) > 0 and p[0] == id_barbaadu:
                # p[2]=Maqaa, p[3]=Bilbila, p[6]=Dhimma, p[9]=Beellama
                sms_abbaa = f"Kabajamoo {p[2]}, Dhimmi keessan ({p[6]}) xumurameera. Guyyaa beellamaa dhuftanii fudhadhaa. W/Lafaa Dadar."
                send_ethio_sms(p[3], sms_abbaa)
                sarara = sarara.replace("Pending", "Finished")
                found = True
            sararoota.append(sarara)
            
    if found:
        with open(DATA_FILE, "w") as f: f.writelines(sararoota)
        print("[✓] Mamiilli beeksifameera, Status 'Finished' tti jijjiirameera.")
    else:
        print("[!] ID kanaan galmee hin argine.")

def uumi_gabaasa_target(filter_type=None, value=None, label="Gabaasa_Waliigalaa"):
    """Excel uumee Telegram-itti erga"""
    if not os.path.exists(DATA_FILE): return
    
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Gabaasa"
    headers = ["ID", "Guyyaa", "Abbaa Dhimmaa", "Bilbila", "Araddaa", "Wirtuu", "Service", "Ogeessa", "Beellama", "Waligala", "Status"]
    ws.append(headers)
    
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", start_color="1F4E78")
    
    total_rev, count, ogeessota = 0, 0, []
    with open(DATA_FILE, "r") as f:
        for line in f:
            p = line.strip().split("|")
            if len(p) < 12: continue
            
            # Match Logic
            dt = datetime.strptime(p[1], "%Y-%m-%d %H:%M")
            match = True
            if filter_type == "jia": match = (dt.month == value)
            elif filter_type == "waggaa": match = (dt.year == value)
            
            if match:
                ws.append([p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[9], p[11], p[12]])
                total_rev += float(p[11]); ogeessota.append(p[7]); count += 1

    f_name = f"{label}.xlsx"
    wb.save(f_name)
    
    # Yoo Gabaasa waggaa ta'e sartifiketii uumi
    if filter_type == "waggaa" and count > 0:
        top_3 = Counter(ogeessota).most_common(3)
        ranks = ["1ffaa", "2ffaa", "3ffaa"]
        for i, (name, _) in enumerate(top_3):
            sf = uumi_sartifiketii(name, ranks[i], value)
            if sf: send_telegram_file(sf, f"📜 Sartifiketii Badhaasaa: {name}")

    caption = f"📊 {label}\n💰 Galii: {total_rev} ETB\n📑 Galmeewwan: {count}"
    send_telegram_file(f_name, caption)
    print(f"[✓] Gabaasaan ergameera.")

# --- NAVIGATION ---

if __name__ == "__main__":
    print("\n" + "*"*40 + "\n WAJJIRA LAFAA MAGAALAA DADAR - V6\n" + "*"*40)
    u, p = input("User: "), input("Pass: ")
    
    if u == USER_NAME and p == PASS_WORD:
        while True:
            print("\n1. Galmee Haaraa (SMS ni erga)")
            print("2. Dhimma Xumurame Beeksisi (Status Update)")
            print("3. Gabaasa Excel (Telegram-itti)")
            print("4. Gabaasa Ji'aa/Waggaa")
            print("5. Exit")
            c = input("\nFilannoo kee: ")
            
            if c == '1': galmeessi()
            elif c == '2': notify_xumurame()
            elif c == '3': uumi_gabaasa_target(label="Gabaasa_Guyyaa")
            elif c == '4':
                print("a. Ji'aan | b. Waggaan")
                sub = input("Filadhu: ")
                if sub == 'a':
                    m = int(input("Ji'a (1-12): "))
                    uumi_gabaasa_target("jia", m, f"Gabaasa_Ji'a_{m}")
                elif sub == 'b':
                    y = int(input("Waggaa (YYYY): "))
                    uumi_gabaasa_target("waggaa", y, f"Gabaasa_Waggaa_{y}")
            elif c == '5': break
    else: print("[!] Login Dogoggora!")

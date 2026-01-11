import os
import requests
import json
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# --- CONFIGURATION ---
# Note: Keep these secret in a real production environment!
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700" 
TRACCAR_URL = "http://localhost:8082/" 
TOKEN = "08a96817-22ab-4660-b866-b7647dbcbf82" 
DB_FILE = "galmee_abbaa_dhimmaa.txt"

def send_ethio_sms(bilbila, ergaa):
    """Traccar SMS Gateway integration"""
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
    
    # Ensure international format for Ethiopia
    bilbila_sirrii = bilbila
    if bilbila.startswith('0'):
        bilbila_sirrii = "+251" + bilbila[1:]
    elif not bilbila.startswith('+'):
        bilbila_sirrii = "+251" + bilbila

    payload = {"to": bilbila_sirrii, "message": ergaa}

    try:
        response = requests.post(TRACCAR_URL, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 202]:
            print(f"[✓] SMS ergameera: {bilbila_sirrii}")
        else:
            print(f"[!] Ergaan hin dabarre. Code: {response.status_code}")
    except Exception as e:
        print(f"[!] Dogoggora SMS: {e}")

def send_telegram_report(maqaa_file):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(maqaa_file, 'rb') as doc:
            files = {'document': doc}
            payload = {'chat_id': CHAT_ID_MANAGER, 'caption': f"Gabaasa Mana Hojii: {maqaa_file}"}
            requests.post(url, files=files, data=payload)
            print(f"[✓] Gabaasni Telegram irratti ergameera.")
    except Exception as e:
        print(f"[!] Error Telegram: {e}")

def safe_input(prompt):
    """Prevents users from entering '|' which breaks our text database"""
    user_data = input(prompt)
    return user_data.replace("|", "-")

def galmeessi():
    print("\n" + "="*45)
    print("--- GALMEE ABBAA DHIMMMAA FI OGEESSAA ---")
    
    maqaa = safe_input("Maqaa Abbaa Dhimmaa: ")
    bilbila_a = safe_input("Bilbila Abbaa Dhimmaa: ")
    araddaa = safe_input("Araddaa: ") 
    wirtuu = safe_input("Wirtuu: ") 
    dhimma = safe_input("Dhimma: ")
    beellama = safe_input("Guyyaa Beellamaa (YYYY-MM-DD): ")
    kartaa = safe_input("Kafaltii Kartaa: ") or "0"
    lizi = safe_input("Kafaltii Lizi: ") or "0"
    
    ogeessa = "-"
    bilbila_o = "-"
    
    if "kartaa" in dhimma.lower():
        ogeessa = safe_input("Maqaa Ogeessa Safaraa: ")
        bilbila_o = safe_input("Bilbila Ogeessaa: ")
        sms_ogeessaa = f"Kabajamoo {ogeessa}, Ajaja Safaraa: {maqaa}, Araddaa {araddaa}, Bilbila: {bilbila_a}. Maaloo itti dhihaadhaa."
        send_ethio_sms(bilbila_o, sms_ogeessaa)

    guyyaa_ammaa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_system = guyyaa_ammaa[-4:].replace(":", "") # Ensure ID is clean
    
    dataa = (f"ID:{id_system} | Guyyaa:{guyyaa_ammaa} | Maqaa:{maqaa} | Bilbila:{bilbila_a} | "
             f"Araddaa:{araddaa} | Wirtuu:{wirtuu} | Dhimma:{dhimma} | Kartaa:{kartaa} | "
             f"Lizi:{lizi} | Beellama:{beellama} | Ogeessa:{ogeessa} | Status:Pending\n")
    
    with open(DB_FILE, "a") as file:
        file.write(dataa)
    print(f"\n[✓] Galmeeffameera! ID: {id_system}")

def notify_xumurame():
    print("\n--- DHIMMA XUMURAME BEEKSISU (SMS) ---")
    id_barbaadu = input("ID abbaa dhimmaa galchi: ")
    sararoota = []
    found = False
    
    if not os.path.exists(DB_FILE): 
        print("[!] Galmeen hin jiru.")
        return

    with open(DB_FILE, "r") as f:
        lines = f.readlines()

    for sarara in lines:
        if f"ID:{id_barbaadu}" in sarara and "Status:Pending" in sarara:
            parts = [x.split(":")[1].strip() for x in sarara.split("|")]
            maqaa, bilbila, dhimma, beellama = parts[2], parts[3], parts[6], parts[9]
            
            sms_abbaa = (f"Kabajamoo {maqaa}, Dhimmi keessan ({dhimma}) xumurameera. "
                         f"Guyyaa {beellama} dhuftanii fudhadhaa. Wajjira Lafaa Dadar.")
            send_ethio_sms(bilbila, sms_abbaa)
            
            sarara = sarara.replace("Status:Pending", "Status:Finished")
            found = True
        sararoota.append(sarara)
            
    with open(DB_FILE, "w") as f:
        f.writelines(sararoota)
    
    if found: print("[✓] Status 'Finished' tti jijjirameera.")
    else: print("[!] ID hin argamne ykn duraan xumurameera.")

def uumi_excel_gabaasa():
    if not os.path.exists(DB_FILE): 
        print("[!] Data'n hin jiru.")
        return
        
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Gabaasa"
    headers = ["ID", "Guyyaa", "Maqaa", "Bilbila", "Araddaa", "Wirtuu", "Dhimma", "Kartaa", "Lizi", "Beellama", "Ogeessa", "Status"]
    sheet.append(headers)
    
    # Style header
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")

    with open(DB_FILE, "r") as f:
        for line in f:
            row = [x.split(":")[1].strip() for x in line.split("|")]
            sheet.append(row)
            
    file_name = f"gabaasa_{datetime.now().strftime('%Y%m%d')}.xlsx"
    wb.save(file_name)
    send_telegram_report(file_name)

if __name__ == "__main__":
    while True:
        print("\n" + "="*40 + "\n  WAJJIRA LAFAA DADAR - V5 (LIVE SMS)\n" + "="*40)
        print("1. Abbaa Dhimmaa Galmeessi (SMS Ogeessaaf)")
        print("2. Dhimma Xumurame Beeksisi (SMS Customer)")
        print("3. Gabaasa Excel Hoggantootaaf (Telegram)")
        print("4. Exit")
        
        f = input("\nFilannoo kee: ")
        if f == '1': galmeessi()
        elif f == '2': notify_xumurame()
        elif f == '3': uumi_excel_gabaasa()
        elif f == '4': break

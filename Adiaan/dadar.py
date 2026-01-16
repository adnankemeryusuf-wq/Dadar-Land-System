mport os
import requests
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# --- CONFIGURATION ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"  # Telegram Hoggantootaaf

# --- SMS FUNCTION (Ethio Telecom Simulation) ---
def send_ethio_sms(bilbila, ergaa):
    """SMS Simulation: Bilbila {bilbila} irratti ergaa dabarsa."""
    print(f"\n[📡 SMS ETHIO-TELECOM ERGAME] -> Bilbila: {bilbila}")
    print(f"[✉️ MESSAGE]: {ergaa}")

# --- TELEGRAM FUNCTION (Manager Report) ---
def send_telegram_report(maqaa_file):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(maqaa_file, 'rb') as doc:
            files = {'document': doc}
            payload = {'chat_id': CHAT_ID_MANAGER, 'caption': f"Gabaasa Mana Hojii: {datetime.now().strftime('%Y-%m-%d')}"}
            r = requests.post(url, files=files, data=payload)
            if r.status_code == 200:
                print(f"[✓] Gabaasni {maqaa_file} hoggantootaaf Telegram irratti ergameera.")
    except Exception as e:
        print(f"[!] Error Telegram: {e}")

def galmeessi():
    print("\n" + "="*45)
    print("--- GALMEE ABBAA DHIMMMAA FI OGEESSAA ---")
    maqaa = input("Maqaa Abbaa Dhimmaa: ")
    # Bilbila default: 0912266121
    bilbila_a = input("Bilbila Abbaa Dhimmaa (Fkn: 0912266121): ") or "0912266121"
    araddaa = input("Araddaa: ") 
    wirtuu = input("Wirtuu: ") 
    dhimma = input("Dhimma (Kartaa/Jijjiira...): ")
    beellama = input("Guyyaa Beellamaa (YYYY-MM-DD): ")
    
    print("\n--- KAFALTII GALII ---")
    kartaa = input("Kafaltii Kartaa: ") or "0"
    lizi = input("Kafaltii Lizi: ") or "0"
    
    ogeessa = "-"
    bilbila_o = "-"
    if "kartaa" in dhimma.lower():
        ogeessa = input("Maqaa Ogeessa Safaraa: ")
        # Bilbila default: 0912266121
        bilbila_o = input("Bilbila Ogeessaa (Fkn: 0912266121): ") or "0912266121"
        
        sms_ogeessaa = f"Kabajamoo {ogeessa}, Ajaja Safaraa: {maqaa}, Araddaa {araddaa}, Bilbila: {bilbila_a}. Maaloo itti dhihaadhaa."
        send_ethio_sms(bilbila_o, sms_ogeessaa)

    guyyaa_ammaa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_system = guyyaa_ammaa[-4:] 
    
    dataa = (f"ID:{id_system} | Guyyaa:{guyyaa_ammaa} | Maqaa:{maqaa} | Bilbila:{bilbila_a} | "
             f"Araddaa:{araddaa} | Wirtuu:{wirtuu} | Dhimma:{dhimma} | Kartaa:{kartaa} | "
             f"Lizi:{lizi} | Beellama:{beellama} | Ogeessa:{ogeessa} | B_Ogeessa:{bilbila_o} | Status:Pending\n")
    
    with open("galmee_abbaa_dhimmaa.txt", "a") as file:
        file.write(dataa)
    print(f"\n[✓] Galmeeffameera! ID: {id_system}")

def notify_xumurame():
    print("\n--- DHIMMA XUMURAME BEEKSISU (SMS) ---")
    id_barbaadu = input("ID abbaa dhimmaa galchi: ")
    sararoota = []
    found = False
    
    if not os.path.exists("galmee_abbaa_dhimmaa.txt"): return

    with open("galmee_abbaa_dhimmaa.txt", "r") as f:
        for sarara in f:
            if f"ID:{id_barbaadu}" in sarara:
                p = [x.split(":")[1].strip() for x in sarara.split("|")]
                maqaa, bilbila, dhimma, beellama = p[2], p[3], p[6], p[9]
                
                sms_abbaa = f"Kabajamoo {maqaa}, Dhimmi keessan ({dhimma}) xumurameera. Guyyaa {beellama} dhuftanii fudhadhaa. Wajjira Lafaa Dadar."
                send_ethio_sms(bilbila, sms_abbaa)
                
                sarara = sarara.replace("Status:Pending", "Status:Finished")
                found = True
            sararoota.append(sarara)
            
    with open("galmee_abbaa_dhimmaa.txt", "w") as f:
        f.writelines(sararoota)
    if not found: print("[!] ID sun hin argamne.")

def uumi_excel_gabaasa(guyyaa_calalu):

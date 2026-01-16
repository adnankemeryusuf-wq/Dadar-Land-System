import os
import requests
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # TOKEN hin maxxansin
CHAT_ID_MANAGER = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID_MANAGER:
    print("❌ TELEGRAM_BOT_TOKEN ykn TELEGRAM_CHAT_ID hin guutamne!")
    exit()

# --- SMS FUNCTION (Simulation) ---
def send_ethio_sms(bilbila, ergaa):
    print(f"\n[📡 SMS ERGAME] -> {bilbila}")
    print(f"[✉️] {ergaa}")

# --- TELEGRAM FUNCTION ---
def send_telegram_report(maqaa_file):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(maqaa_file, 'rb') as doc:
        files = {'document': doc}
        payload = {
            'chat_id': CHAT_ID_MANAGER,
            'caption': f"Gabaasa Guyyaa: {datetime.now().strftime('%Y-%m-%d')}"
        }
        r = requests.post(url, files=files, data=payload)
        if r.status_code == 200:
            print("[✓] Gabaasni Telegramtti ergameera.")
        else:
            print("[!] Telegram error:", r.text)

def galmeessi():
    print("\n--- GALMEE ABBAA DHIMMAA ---")
    maqaa = input("Maqaa: ")
    bilbila_a = input("Bilbila: ") or "0912266121"
    araddaa = input("Araddaa: ")
    wirtuu = input("Wirtuu: ")
    dhimma = input("Dhimma: ")
    beellama = input("Guyyaa Beellamaa (YYYY-MM-DD): ")

    kartaa = input("Kafaltii Kartaa: ") or "0"
    lizi = input("Kafaltii Lizi: ") or "0"

    ogeessa = "-"
    bilbila_o = "-"
    if "kartaa" in dhimma.lower():
        ogeessa = input("Maqaa Ogeessa: ")
        bilbila_o = input("Bilbila Ogeessa: ") or "0912266121"
        send_ethio_sms(
            bilbila_o,
            f"Ogeessa {ogeessa}, Safaraa {maqaa}, Araddaa {araddaa}, Bilbila {bilbila_a}"
        )

    yeroo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_sys = datetime.now().strftime("%H%M%S")

    dataa = (
        f"ID:{id_sys} | Guyyaa:{yeroo} | Maqaa:{maqaa} | Bilbila:{bilbila_a} | "
        f"Araddaa:{araddaa} | Wirtuu:{wirtuu} | Dhimma:{dhimma} | "
        f"Kartaa:{kartaa} | Lizi:{lizi} | Beellama:{beellama} | "
        f"Ogeessa:{ogeessa} | B_Ogeessa:{bilbila_o} | Status:Pending\n"
    )

    with open("galmee_abbaa_dhimmaa.txt", "a", encoding="utf-8") as f:
        f.write(dataa)

    print(f"[✓] Galmeeffameera! ID={id_sys}")

def notify_xumurame():
    id_barbaadu = input("ID galchi: ")
    if not os.path.exists("galmee_abbaa_dhimmaa.txt"):
        return

    lines = []
    found = False

    with open("galmee_abbaa_dhimmaa.txt", "r", encoding="utf-8") as f:
        for line in f:
            if f"ID:{id_barbaadu}" in line:
                parts = [x.split(":",1)[1].strip() for x in line.split("|")]
                maqaa, bilbila, dhimma, beellama = parts[2], parts[3], parts[6], parts[9]
                send_ethio_sms(
                    bilbila,
                    f"{maqaa}, Dhimma {dhimma} xumurameera. Guyyaa {beellama} dhuftanii fudhadhaa."
                )
                line = line.replace("Status:Pending", "Status:Finished")
                found = True
            lines.append(line)

    with open("galmee_abbaa_dhimmaa.txt", "w", encoding="utf-8") as f:
        f.writelines(lines)

    if not found:
        print("[!] ID hin argamne.")

def uumi_excel_gabaasa(guyyaa):
    if not os.path.exists("galmee_abbaa_dhimmaa.txt"):
        return

    amma = datetime.now()
    records = []

    with open("galmee_abbaa_dhimmaa.txt", "r", encoding="utf-8") as f:
        for l in f:
            try:
                g = l.split("|")[1].split(":")[1].strip()
                if amma - datetime.strptime(g, "%Y-%m-%d %H:%M:%S") <= timedelta(days=guyyaa):
                    records.append(l.strip())
            except:
                continue

    if not records:
        print("[!] Daataan hin jiru.")
        return

    wb = openpyxl.Workbook()
    sh = wb.active
    sh.title = "Gabaasa"

    headers = ["ID","Guyyaa","Maqaa","Bilbila","Araddaa","Wirtuu","Dhimma",
               "Kartaa","Lizi","Beellama","Ogeessa","B_Ogeessa","Status"]
    sh.append(headers)

    for c in sh[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="002060")
        c.alignment = Alignment(horizontal="center")

    for r in records:
        sh.append([x.split(":",1)[1].strip() for x in r.split("|")])

    file = f"gabaasa_{datetime.now().strftime('%H%M%S')}.xlsx"
    wb.save(file)
    send_telegram_report(file)

# --- MAIN ---
if __name__ == "__main__":
    while True:
        print("\nWAJJIRA LAFAA DADAR - SYSTEM V5")
        print("1. Galmeessi")
        print("2. Xumurame Beeksisi (SMS)")
        print("3. Gabaasa Excel Ergi")
        print("4. Exit")

        f = input("Filannoo: ")
        if f == "1":
            galmeessi()
        elif f == "2":
            notify_xumurame()
        elif f == "3":
            uumi_excel_gabaasa(1)
        elif f == "4":
            break

import os
import requests
from datetime import datetime, timedelta
from fpdf import FPDF

# --- Telegram Setup (TOKEN KEE ASITTI GALMEEFFAMEERA) ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
# CHAT_ID kee asitti galchi (Fkn: "987654321")
CHAT_ID = "ID_KEE_ASITTI_GALCHI" 

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'GABAASA WAJJIRA LAFAA DADAR', 0, 1, 'C')
        self.ln(5)

def galmeessi():
    print("\n--- GALMEE ABBAA DHIMMMAA ---")
    maqaa = input("Maqaa Abbaa Dhimmaa: ")
    iddoo = input("Ganda/Iddoo: ")
    dhimma = input("Dhimma dhufeef: ")
    guyyaa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dataa = f"Guyyaa: {guyyaa} | Maqaa: {maqaa} | Iddoo: {iddoo} | Dhimma: {dhimma}\n"
    with open("galmee_abbaa_dhimmaa.txt", "a") as file:
        file.write(dataa)
    print(f"\n[✓] Abbaan dhimmaa {maqaa} galmeeffameera!")

def gara_telegram_ergi(maqaa_file):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(maqaa_file, 'rb') as doc:
            files = {'document': doc}
            payload = {'chat_id': CHAT_ID, 'caption': f"Gabaasa Wajjira Lafaa: {maqaa_file}"}
            response = requests.post(url, files=files, data=payload)
            if response.status_code == 200:
                print(f"[✓] Gabaasni kallattiin Telegram irratti ergameera!")
            else:
                print(f"[!] Erguun hin danda'amne. Status: {response.status_code}")
    except Exception as e:
        print(f"[!] Dogoggora Telegram: {e}")

def uumi_fi_ergi_pdf(data_list, maqaa_file):
    if not data_list:
        print("\n[!] Daataan gabaasaa kutaawwan kanaan wal qabatu hin jiru!")
        return
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for line in data_list:
        pdf.multi_cell(0, 10, txt=line)
        pdf.ln(2)
    pdf.output(maqaa_file)
    print(f"\n[✓] PDF '{maqaa_file}' uumameera.")
    gara_telegram_ergi(maqaa_file)

def gabaasa_calali(guyyaa):
    if not os.path.exists("galmee_abbaa_dhimmaa.txt"): return []
    amma = datetime.now()
    daataa = []
    with open("galmee_abbaa_dhimmaa.txt", "r") as f:
        for sarara in f:
            try:
                part = sarara.split("|")[0].split("Guyyaa:")[1].strip()
                if amma - datetime.strptime(part, "%Y-%m-%d %H:%M:%S") <= timedelta(days=guyyaa):
                    daataa.append(sarara.strip())
            except: continue
    return daataa

if name == "main":
    while True:
        print("\n* SIRNA GALMEE WAJJIRA LAFAA DADAR *")
        print("1. Abbaa Dhimmaa Galmeessi")
        print("2. Gabaasa Guyyaa Ergi (PDF)")
        print("3. Gabaasa Torbee Ergi (PDF)")
        print("4. Gabaasa Ji'aa Ergi (PDF)")
        print("5. Exit")
        
        filannoo = input("\nFilannoo kee (1-5): ")
        if filannoo == '1':
            galmeessi()
        elif filannoo in ['2', '3', '4']:
            guyyaa = 1 if filannoo == '2' else (7 if filannoo == '3' else 30)
            maqaa = f"gabaasa_{guyyaa}.pdf"
            d = gabaasa_calali(guyyaa)
            uumi_fi_ergi_pdf(d, maqaa)
        elif filannoo == '5':
            print("Nagaan turaa!")
            break

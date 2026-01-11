import os
import requests
from datetime import datetime, timedelta
from fpdf import FPDF

# --- CONFIGURATION ---
# Replace with your actual Bot Token
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
# Replace "ID_KEE_ASITTI_GALCHI" with your actual numeric Chat ID (e.g., "7329587700")
CHAT_ID = "7329587700" 
DB_FILE = "galmee_abbaa_dhimmaa.txt"

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'GABAASA WAJJIRA LAFAA DADAR', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Fuula {self.page_no()}', 0, 0, 'C')

def galmeessi():
    print("\n" + "="*30)
    print("--- GALMEE ABBAA DHIMMMAA ---")
    maqaa = input("Maqaa Abbaa Dhimmaa: ")
    iddoo = input("Ganda/Iddoo: ")
    dhimma = input("Dhimma dhufeef: ")
    
    guyyaa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dataa = f"Guyyaa: {guyyaa} | Maqaa: {maqaa} | Iddoo: {iddoo} | Dhimma: {dhimma}\n"
    
    with open(DB_FILE, "a") as file:
        file.write(dataa)
    print(f"\n[✓] Abbaan dhimmaa '{maqaa}' galmeeffameera!")

def gara_telegram_ergi(maqaa_file):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(maqaa_file, 'rb') as doc:
            files = {'document': doc}
            payload = {'chat_id': CHAT_ID, 'caption': f"Gabaasa Wajjira Lafaa: {maqaa_file}"}
            response = requests.post(url, files=files, data=payload)
            if response.status_code == 200:
                print(f"[✓] Gabaasni '{maqaa_file}' Telegram irratti ergameera!")
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
        # Clean text for PDF compatibility
        clean_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, txt=clean_line, border=1)
        pdf.ln(2)
        
    pdf.output(maqaa_file)
    print(f"\n[✓] PDF '{maqaa_file}' uumameera.")
    gara_telegram_ergi(maqaa_file)

def gabaasa_calali(guyyaa_baayina):
    if not os.path.exists(DB_FILE): 
        return []
        
    amma = datetime.now()
    daataa = []
    with open(DB_FILE, "r") as f:
        for sarara in f:
            try:
                # Extracts date string from "Guyyaa: YYYY-MM-DD HH:MM:SS"
                part = sarara.split("|")[0].split("Guyyaa:")[1].strip()
                guyyaa_galmee = datetime.strptime(part, "%Y-%m-%d %H:%M:%S")
                if amma - guyyaa_galmee <= timedelta(days=guyyaa_baayina):
                    daataa.append(sarara.strip())
            except Exception:
                continue
    return daataa

if __name__ == "__main__":
    while True:
        print("\n" + "*"*35)
        print("  SIRNA GALMEE WAJJIRA LAFAA DADAR  ")
        print("*"*35)
        print("1. Abbaa Dhimmaa Galmeessi")
        print("2. Gabaasa Guyyaa Ergi (PDF)")
        print("3. Gabaasa Torbee Ergi (PDF)")
        print("4. Gabaasa Ji'aa Ergi (PDF)")
        print("5. Exit")
        
        filannoo = input("\nFilannoo kee (1-5): ")
        
        if filannoo == '1':
            galmeessi()
        elif filannoo in ['2', '3', '4']:
            # Mapping menu selection to number of days
            guyyaawwan = {'2': 1, '3': 7, '4': 30}
            target_days = guyyaawwan[filannoo]
            
            label = "guyyaa" if filannoo == '2' else ("torbee" if filannoo == '3' else "jia")
            file_name = f"gabaasa_{label}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            data_filtered = gabaasa_calali(target_days)
            uumi_fi_ergi_pdf(data_filtered, file_name)
        elif filannoo == '5':
            print("Hojii gaarii, nagaan turaa!")
            break
        else:
            print("[!] Filannoo dogoggoraa, irra deebi'i.")

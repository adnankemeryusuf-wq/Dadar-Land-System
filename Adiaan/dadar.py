import os
import requests
from datetime import datetime, timedelta
from fpdf import FPDF

# === TELEGRAM SETUP (Nageenyaaf environment variable fayyadami) ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # set TELEGRAM_BOT_TOKEN
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")      # set TELEGRAM_CHAT_ID

if not BOT_TOKEN or not CHAT_ID:
    print("❌ BOT_TOKEN ykn CHAT_ID hin guutamne!")
    exit()

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'GABAASA WAJJIRA LAFAA DADAR', 0, 1, 'C')
        self.ln(5)

def galmeessi():
    print("\n--- GALMEE ABBAA DHIMMAA ---")
    maqaa = input("Maqaa Abbaa Dhimmaa: ")
    iddoo = input("Ganda/Iddoo: ")
    dhimma = input("Dhimma dhufeef: ")

    guyyaa = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dataa = f"Guyyaa: {guyyaa} | Maqaa: {maqaa} | Iddoo: {iddoo} | Dhimma: {dhimma}\n"

    with open("galmee_abbaa_dhimmaa.txt", "a", encoding="utf-8") as file:
        file.write(dataa)

    print(f"\n[✓] Abbaan dhimmaa {maqaa} galmeeffameera!")

def gara_telegram_ergi(maqaa_file):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(maqaa_file, 'rb') as doc:
            files = {'document': doc}
            payload = {
                'chat_id': CHAT_ID,
                'caption': f"Gabaasa Wajjira Lafaa: {maqaa_file}"
            }
            r = requests.post(url, files=files, data=payload)

            if r.status_code == 200:
                print("[✓] PDF Telegramtti ergameera!")
            else:
                print(f"[!] Erguun hin danda'amne: {r.text}")
    except Exception as e:
        print(f"[!] Dogoggora Telegram: {e}")

def gabaasa_calali(guyyaa):
    if not os.path.exists("galmee_abbaa_dhimmaa.txt"):
        return []

    amma = datetime.now()
    daataa = []

    with open("galmee_abbaa_dhimmaa.txt", "r", encoding="utf-8") as f:
        for sarara in f:
            try:
                part = sarara.split("|")[0].split("Guyyaa:")[1].strip()
                yeroo = datetime.strptime(part, "%Y-%m-%d %H:%M:%S")
                if amma - yeroo <= timedelta(days=guyyaa):
                    daataa.append(sarara.strip())
            except:
                continue
    return daataa

def uumi_fi_ergi_pdf(data_list, maqaa_file):
    if not data_list:
        print("\n[!] Daataan gabaasaa hin argamne!")
        return

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    for line in data_list:
        pdf.multi_cell(0, 8, line)
        pdf.ln(1)

    pdf.output(maqaa_file)
    print(f"[✓] PDF '{maqaa_file}' uumameera.")

    gara_telegram_ergi(maqaa_file)

# === MAIN PROGRAM ===
if __name__ == "__main__":
    while True:
        print("\n* SIRNA GALMEE WAJJIRA LAFAA DADAR *")
        print("1. Abbaa Dhimmaa Galmeessi")
        print("2. Gabaasa Guyyaa (PDF)")
        print("3. Gabaasa Torbee (PDF)")
        print("4. Gabaasa Ji'aa (PDF)")
        print("5. Ba'i")

        filannoo = input("\nFilannoo kee (1-5): ")

        if filannoo == '1':
            galmeessi()
        elif filannoo in ['2', '3', '4']:
            guyyaa = 1 if filannoo == '2' else (7 if filannoo == '3' else 30)
            maqaa = f"gabaasa_{guyyaa}_guyyaa.pdf"
            data = gabaasa_calali(guyyaa)
            uumi_fi_ergi_pdf(data, maqaa)
        elif filannoo == '5':
            print("Nagaan turaa 👋")
            break
        else:
            print("❌ Filannoo dogoggoraa!")

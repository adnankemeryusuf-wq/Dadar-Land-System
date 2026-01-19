import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & SETUP =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "Adiaan/nagahee"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR, exist_ok=True)

# ================= 2. CORE FUNCTIONS =================

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# --- WARAQAA RAGAA (CLEARANCE) PDF ---
def create_clearance_pdf(name, araddaa, qaxana, services):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.5); pdf.rect(10, 10, 190, 277)
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 90, 15, 25)
    pdf.set_y(45); pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'U', 14)
    pdf.cell(0, 10, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.set_y(85); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    date_str = datetime.now().strftime('%d/%m/%Y')
    text = (f"Waraqaan ragaa kun Obbo/Adde {name.upper()}, Araddaa {araddaa}, "
            f"Qaxana {qaxana} keessatti tajaajila argachaa turaniif kan kennameedha.\n\n"
            f"Maamilli kun hanga guyyaa har'aa ({date_str}) tatti tajaajiloota: \n"
            f"'{services}' \n"
            f"jedhamaniif kaffaltii barbaachisu hunda raawwatanii waan xumuraniif, "
            f"waajjirri keenya ragaa qulqullinaa kana akka tajaajiluuf kenneeraaf.")
    pdf.multi_cell(170, 10, text, align='L')
    pdf.set_y(220); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "__________________________", ln=True, align='C')
    pdf.cell(0, 10, "Itti Gaafatamaa Waajjiraa", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- EXCEL TELEGRAM FORMATTED ---
def send_excel_to_telegram(df_to_send):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_to_send[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            workbook, worksheet = writer.book, writer.sheets['Gabaasa']
            header_f = workbook.add_format({'bold':True,'bg_color':'#2E7D32','font_color':'white','border':1})
            for col_num, val in enumerate(df_to_send[COL_NAMES].columns.values):
                worksheet.write(0, col_num, val, header_f)
                worksheet.set_column(col_num, col_num, 20)
        output.seek(0)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': "📊 Gabaasa Dadar"}, files={'document': ('Gabaasa.xlsx', output)})
        return True
    except: return False

# ================= 3. UI LAYOUT =================
st.set_page_config(page_title="Dadar Land Management", layout="wide")
df = load_data()

menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    c1, c2, c3 = st.columns(3)
    c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
    c2.metric("Maamiltoota", len(df))
    c3.metric("Ogeeyyii", df['Maqaa_Ogeessa'].nunique())

# --- GALMEE HAARAA ---
elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa Haaraa")
    GATII_DICT = {
        "🏷️ Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)"],
        "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
        "🏗️ Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa"],
        "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
        "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"]
    }
    
    selected_cats = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
    details, d_fees = [], {}
    
    for cat in selected_cats:
        with st.expander(f"Kaffaltii {cat}"):
            subs = st.multiselect(f"Tajaajiloota {cat}:", GATII_DICT[cat], key=cat)
            for s in subs:
                details.append(f"{cat}({s})")
                d_fees[f"{cat}_{s}"] = st.number_input(f"Kaffaltii {s}", min_value=0.0, key=f"f_{s}")

    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_maqaa = c1.text_input("Maqaa Maamilaa *")
        m_qaxana = c2.text_input("Qaxana")
        m_araddaa = c1.text_input("Araddaa *")
        m_ogeessa = c2.text_input("Ogeessa Raawwate *")
        nagahee = st.file_uploader("Nagahee Scan", type=['jpg','png','jpeg'])
        
        if st.form_submit_button("💾 Galmeessi"):
            if m_maqaa and m_araddaa and details:
                new_row = [datetime.now().strftime('%d/%m/%Y'), m_maqaa, m_araddaa, m_qaxana, ", ".join(details), m_ogeessa, sum(d_fees.values())]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success(f"Galmeen {m_maqaa} milkaa'eera!")
                
                # --- PDF CLEARANCE GENERATION ---
                if any("Waraqaa Ragaa (Clearance)" in d for d in details):
                    pdf_c = create_clearance_pdf(m_maqaa, m_araddaa, m_qaxana, ", ".join(details))
                    st.download_button("📄 Waraqaa Ragaa (Clearance) Buufadhu", pdf_c, f"Clearance_{m_maqaa}.pdf")
            else: st.error("Maaloo guutuu guuti!")

# --- GABAASA ---
elif menu == "📈 Gabaasa":
    st.header("📈 Gabaasa Bal'aa")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        if st.button("🚀 Excel Gara Telegram-itti Ergi"):
            if send_excel_to_telegram(df): st.success("Ergameera!")
            else: st.error("Dogoggora!")

# --- BADHAASA ---
elif menu == "🏆 Badhaasa":
    st.header("🏆 Badhaasa Ogeeyyii")
    if not df.empty:
        top = df['Maqaa_Ogeessa'].value_counts().head(3)
        st.write(top)

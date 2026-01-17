import streamlit as st
import pandas as pd
import os
import io
import requests
import threading
import time
import schedule
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_excel_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try: return requests.post(url, files=files, data=data).status_code == 200
    except: return False

def create_customer_cert(customer_name, service_type, date_str):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(27, 94, 32)
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    pdf.set_font('Arial', 'B', 35)
    pdf.set_y(50)
    pdf.cell(0, 20, "WARAQAA RAGAA TAJAAJILAA", ln=True, align='C')
    pdf.set_font('Arial', '', 22)
    pdf.ln(10)
    pdf.multi_cell(0, 15, f"Obbo/Adde {customer_name.upper()}\n\nTajaajila '{service_type}' argachuu keessaniif\nwaraqaan ragaa kun guyyaa {date_str} kennameera.", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. AUTO-REPORTING (BACKGROUND) =================
def auto_report_job():
    df_auto = load_data()
    if not df_auto.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_auto[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
        excel_data = output.getvalue()
        caption = f"🤖 **GABAASA AUTO-REPORT**\n📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}\n💰 Galii: {df_auto['Kafaltii_Taj'].sum():,.2f} ETB"
        send_excel_to_telegram(excel_data, "Auto_Report.xlsx", caption)

def run_scheduler():
    schedule.every().day.at("17:30").do(auto_report_job) # Sa'aatii 11:30 PM irratti
    while True:
        schedule.run_pending()
        time.sleep(60)

if 'scheduler_started' not in st.session_state:
    threading.Thread(target=run_scheduler, daemon=True).start()
    st.session_state.scheduler_started = True

# ================= 4. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center;'>Dadar Land Admin</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi/Edit", "📈 Gabaasa"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><h3>{df['Kafaltii_Taj'].sum():,.2f} ETB</h3></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><h3>{len(df)}</h3></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><h3>{df['Maqaa_Ogeessa'].nunique()}</h3></div>", unsafe_allow_html=True)
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {"Gibira": ["Gibira Manaa", "Gibira Lafa"], "Liizii": ["TOT", "Liizii Waggaa"], "Kaartaa": ["Kaartaa Lafa", "Kaartaa Lafa Qonnaa"]}
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa (Dirqama)", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        for g in selected_main:
            subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"s_{g}")
            for s in subs:
                details.append(f"{g}({s})")
                d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}")

        with st.form("entry_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara = c2.text_input("Araddaa *")
            qax = c1.text_input("Qaxana *")
            ogeessa = c2.text_input("Maqaa Ogeessaa *")
            nagahee_file = st.file_uploader("Nagahee Scan", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if not maqaa or not ara or not qax or not ogeessa or not details:
                    st.warning("⚠️ Maaloo! Iddoo mallattoo (*) qabu hunda guuti.")
                else:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.balloons()
                    st.success("✅ Galmeeffameera!")

    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("🔍 Maqaa Barbaadi")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                    st.write(f"Tajaajila: {row['Gosa_Tajajjilaa']} | Kafaltii: {row['Kafaltii_Taj']} ETB")
                    if st.button(f"📜 Sartiifiketa Qopheessi", key=f"btn_{idx}"):
                        pdf_data = create_customer_cert(row['Maqaa_Abbaa_Dhimmaa'], row['Gosa_Tajajjilaa'], row['Guyyaa'])
                        st.download_button("📥 PDF Buusi", pdf_data, f"Sartiifiketa_{idx}.pdf", "application/pdf")

    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa fi Telegram")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
            excel_data = output.getvalue()
            
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel Bareedaa Buusi", excel_data, "Gabaasa.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            if c2.button("✈️ Gabaasa Telegramitti Ergi"):
                caption = f"📊 Gabaasa Manual: {datetime.now().strftime('%d/%m/%Y')}\n💰 Galii: {df['Kafaltii_Taj'].sum():,.2f} ETB"
                if send_excel_to_telegram(excel_data, "Gabaasa_Dadar.xlsx", caption):
                    st.success("✅ Telegramitti ergameera!")
                else: st.error("❌ Error!")

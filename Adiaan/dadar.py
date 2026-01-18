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
    try:
        return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_clearance_pdf(name, araddaa, qaxana, services, nagahee_lakk):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.5)
    pdf.rect(10, 10, 190, 277)
    
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 90, 15, 25)
    
    pdf.set_y(45)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'U', 14)
    pdf.cell(0, 10, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    
    pdf.set_y(85)
    pdf.set_font('Arial', '', 12)
    pdf.set_x(20)
    
    date_str = datetime.now().strftime('%d/%m/%Y')
    text = (
        f"Waraqaan ragaa kun Obbo/Adde {str(name).upper()}, Araddaa {araddaa}, "
        f"Qaxana {qaxana} keessatti tajaajila argachaa turaniif kan kennameedha.\n\n"
        f"Maamilli kun kaffaltii tajaajila gosa '{services}' jedhamaniif "
        f"Lakk. Nagahee {nagahee_lakk} kaffaltii barbaachisu hunda raawwatanii waan xumuraniif, "
        f"guyyaa har'aa ({date_str}) ragaa qulqullinaa kana akka tajaajiluuf waajjirri keenya kenneeraaf."
    )
    pdf.multi_cell(170, 10, text, align='L')
    
    pdf.set_y(220)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "__________________________", ln=True, align='C')
    pdf.cell(0, 10, "Itti Gaafatamaa Waajjiraa", ln=True, align='C')
    pdf.cell(0, 10, "(Mallattoo fi Chaappaa)", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

def send_excel_to_telegram(df_to_send):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_to_send[COL_NAMES].to_excel(writer, index=False, sheet_name='Gabaasa')
        output.seek(0)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': "📊 Gabaasa Dadar"}, files={'document': ('Gabaasa_Dadar.xlsx', output)})
        return True
    except: return False

# ================= 3. UI LAYOUT =================
st.set_page_config(page_title="Dadar Land Management", layout="wide")
df = load_data()

# Session State Setup
if 'show_download' not in st.session_state: st.session_state.show_download = False
if 'pdf_data' not in st.session_state: st.session_state.pdf_data = None
if 'pdf_filename' not in st.session_state: st.session_state.pdf_filename = ""

menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa"])

if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Waliigala Galii", f"{pd.to_numeric(df['Kafaltii_Taj']).sum():,.2f} ETB")
        c2.metric("Maamiltoota", len(df))
        c3.metric("Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
    else: st.info("Data'n hin jiru.")

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
        with st.expander(f"Kaffaltii {cat}", expanded=True):
            subs = st.multiselect(f"Tajaajiloota {cat}:", GATII_DICT[cat], key=cat)
            for s in subs:
                details.append(f"{s}")
                d_fees[f"{cat}_{s}"] = st.number_input(f"Kaffaltii {s}", min_value=0.0, key=f"f_{s}")

    st.divider()

    with st.form("main_form", clear_on_submit=True):
        st.subheader("Odeeffannoo Maamilaa")
        c1, c2 = st.columns(2)
        m_maqaa = c1.text_input("Maqaa Maamilaa *")
        m_araddaa = c2.text_input("Araddaa *")
        m_qaxana = c1.text_input("Qaxana")
        m_nagahee_lakk = c2.text_input("Lakk. Nagahee (Receipt No.) *")
        m_ogeessa = c1.text_input("Ogeessa Raawwate *")
        nagahee_file = st.file_uploader("Nagahee Scan", type=['jpg','png','jpeg'])
        
        submit = st.form_submit_button("💾 Galmeessi fi Kuusi")
        
        if submit:
            if m_maqaa and m_araddaa and m_nagahee_lakk and details:
                kafallti_hunda = sum(d_fees.values())
                new_row = [datetime.now().strftime('%d/%m/%Y'), m_maqaa, m_araddaa, m_qaxana, ", ".join(details), m_ogeessa, kafallti_hunda]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success(f"✅ Galmeen {m_maqaa} milkaa'eera!")
                
                if "Waraqaa Ragaa (Clearance)" in details:
                    st.session_state.pdf_data = create_clearance_pdf(m_maqaa, m_araddaa, m_qaxana, ", ".join(details), m_nagahee_lakk)
                    st.session_state.pdf_filename = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
                    st.session_state.show_download = True
                else:
                    st.session_state.show_download = False
            else:
                st.error("⚠️ Maaloo hunda guuti!")
                st.session_state.show_download = False

    # Download button Form-ii alatti akka hin badneef
    if st.session_state.show_download:
        st.info("📄 Waraqaan Ragaa (Clearance) Maamila kanaaf qophaa'eera.")
        st.download_button(
            label="📥 Waraqaa Ragaa (Clearance) Download Godhuuf As Cuqaasi",
            data=st.session_state.pdf_data,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
            key="final_dl_btn"
        )

elif menu == "📈 Gabaasa":
    st.header("📈 Gabaasa Bal'aa")
    st.dataframe(df, use_container_width=True)
    if st.button("🚀 Excel Gara Telegram"):
        if send_excel_to_telegram(df): st.success("✅ Ergameera!")

elif menu == "🏆 Badhaasa":
    st.header("🏆 Sadarkaa Ogeeyyii")
    if not df.empty: st.table(df['Maqaa_Ogeessa'].value_counts().head(3))

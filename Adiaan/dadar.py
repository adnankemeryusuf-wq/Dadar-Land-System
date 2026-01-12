import streamlit as st
import os
import pandas as pd
import requests
import io
from datetime import datetime
from fpdf import FPDF

# --- 1. QINDAYYII ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Status', 'C1', 'C2', 'C3', 'Kafaltii']

# Telegram API
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

import streamlit as st
import os
import pandas as pd
import requests
import io
from datetime import datetime
from fpdf import FPDF

# --- 1. QINDAYYII BU'URAA ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

USER_NAME = "Lafa"
PASS_WORD = "1234"
DATA_FILE = "dadar_final_report.txt"
LOGO_FILE = "logo.png"

# Tarree Haaraa (Columns)
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj', 'Kafaltii_Wal', 'C1', 'C2', 'C3']

# Telegram API
TELEGRAM_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
TELEGRAM_CHAT_ID = "7329587700"

# --- 2. FUNKSHINOOTA ---
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, on_bad_lines='skip', encoding='utf-8')
        return df
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# --- 3. REPORTING (Excel & PDF) ---
def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Gabaasa_Dadar')
    return output.getvalue()

def create_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "GABAASA WAAJJIRA LAFAA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(5)
    
    # Table Header
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 9)
    cols = ["Maqaa", "Gosa", "Ogeessa", "K.Taj", "K.Wal"]
    for col in cols:
        pdf.cell(38, 8, col, 1, 0, 'C', True)
    pdf.ln()

    pdf.set_font("Arial", '', 8)
    for _, row in df.iterrows():
        pdf.cell(38, 7, str(row['Maqaa'])[:20], 1)
        pdf.cell(38, 7, str(row['Gosa']), 1)
        pdf.cell(38, 7, str(row['Ogeessa']), 1)
        pdf.cell(38, 7, str(row['Kafaltii_Taj']), 1)
        pdf.cell(38, 7, str(row['Kafaltii_Wal']), 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SARTIIFIKETA (Professional Design) ---
def generate_certificate(expert_name, total_served):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(1.5); pdf.set_draw_color(184, 134, 11) # Golden Border
    pdf.rect(5, 5, 287, 200)
    
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, x=130, y=10, w=35)
    
    pdf.ln(35)
    pdf.set_font('Times', 'B', 40); pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Arial', 'I', 16); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, "Gootummaa Hojii Waggaa kan kennameef:", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Times', 'B', 32); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 14); pdf.set_text_color(50, 50, 50)
    msg = (f"Waggaa kanatti tajaajila saffisaa fi amannamaa ta'een Abbootii Dhimmaa {total_served} "
           "tajaajiluun bu'aa qabeessa ta'anii waan argamaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    
    # Signature Area - Gadi siqee jira
    pdf.set_y(175)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 8, "__________________________", ln=0, align='C')
    pdf.cell(87, 8, "", ln=0)
    pdf.cell(100, 8, "__________________________", ln=1, align='C')
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, datetime.now().strftime("%d/%m/%Y"), ln=1, align='C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, "Guyyaa", ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. MAIN APP ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1, 1])
    with center:
        st.title("Seensa")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    with st.sidebar:
        st.header("Admin Panel")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaaduu & Sirreessu", "📊 Gabaasa Telegr_Pro", "🏆 Sartiifiketa", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)

    df = load_data()

    if choice == "🏠 Dashboard":
        st.markdown("<h2 style='text-align:center;'>Dashboard</h2>", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Waligala Galmee", len(df))
            c2.metric("Galii Waliigalaa", f"{pd.to_numeric(df['Kafaltii_Wal'], errors='coerce').sum():,.2f}")
            c3.metric("Hardha", len(df[pd.to_datetime(df['Yeroo'], errors='coerce').dt.date == datetime.now().date()]))
        else: st.info("Ragaan galmeeffame hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        st.subheader("📝 Galmee Haaraa Guuti")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            ad = col1.text_input("Maqaa Abbaa Dhimmaa")
            ar = col1.text_input("Araddaa")
            qx = col1.text_input("Qaxana")
            gs = col2.selectbox("Gosa Tajaajilaa", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"])
            og = col2.text_input("Maqaa Ogeessaa")
            kf_t = col2.number_input("Kafaltii Tajaajilaa (ETB)", min_value=0.0)
            kf_d = col2.number_input("Kafaltii Dabalataa/Biirro (ETB)", min_value=0.0)
            
            if st.form_submit_button("✅ GALMEESSI"):
                if ad and og:
                    waligala = kf_t + kf_d
                    yeroo = datetime.now().strftime('%Y-%m-%d %H:%M')
                    line = f"{yeroo}|{ad}|{ar}|{qx}|{gs}|{og}|{kf_t}|{waligala}|0|0|0\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                    st.success(f"Galmee {ad} milkaa'inaan raawwatameera! Waliigala: {waligala} ETB")
                    st.rerun()

    elif choice == "🔍 Barbaaduu & Sirreessu":
        st.subheader("🔍 Barbaadi, Sirreessi ykn Haqui")
        query = st.text_input("Maqaa Abbaa Dhimmaa barreessi...")
        if not df.empty:
            results = df[df['Maqaa'].str.contains(query, case=False, na=False)]
            st.dataframe(results)
            if not results.empty:
                name_to_act = st.selectbox("Nama filadhu:", results['Maqaa'].tolist())
                idx = df[df['Maqaa'] == name_to_act].index[0]
                
                with st.expander("🛠️ Tarkaanfii"):
                    col1, col2 = st.columns(2)
                    new_gs = col1.selectbox("Gosa Tajaajilaa", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"], key="edit_gs")
                    new_kf_t = col2.number_input("Kafaltii Tajaajilaa", value=float(df.at[idx, 'Kafaltii_Taj']))
                    
                    if st.button("💾 FOOYYEESSI"):
                        df.at[idx, 'Gosa'] = new_gs
                        df.at[idx, 'Kafaltii_Taj'] = new_kf_t
                        df.at[idx, 'Kafaltii_Wal'] = new_kf_t # Asume update total
                        save_data(df)
                        st.success("Sirreeffameera!")
                        st.rerun()
                    
                    if st.button("🗑️ HAQI (DELETE)", type="primary"):
                        df = df.drop(idx)
                        save_data(df)
                        st.warning("Galmeen sun haqameera!")
                        st.rerun()

    elif choice == "📊 Gabaasa Telegr_Pro":
        st.subheader("📊 Gabaasa Guutuu")
        if not df.empty:
            st.dataframe(df)
            c1, c2, c3 = st.columns(3)
            
            # Excel
            ex_data = create_excel(df)
            c1.download_button("📥 Excel Buufadhu", ex_data, "Gabaasa_Dadar.xlsx")
            
            # PDF
            pdf_data = create_pdf_report(df)
            c2.download_button("📥 PDF Buufadhu", pdf_data, "Gabaasa_Dadar.pdf")
            
            # Telegram
            if c3.button("🚀 Telegram-itti Ergi"):
                msg = f"📊 *GABAASA DADAR*\n👤 Namoota: {len(df)}\n💰 Galii Waliigalaa: {pd.to_numeric(df['Kafaltii_Wal'], errors='coerce').sum():,.2f} ETB"
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                st.success("Ergameera!")

    elif choice == "🏆 Sartiifiketa":
        if not df.empty:
            best_og = df['Ogeessa'].value_counts().idxmax()
            st.success(f"Ogeessa Waggaa: {best_og}")
            if st.button("📜 SARTIIFIKETA QOPHEESSI"):
                cert = generate_certificate(best_og, df['Ogeessa'].value_counts().max())
                st.download_button("📥 Sartiifiketa Buufadhu (PDF)", cert, f"Certificate_{best_og}.pdf")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()
# --- 3. REPORT GENERATORS ---
def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Gabaasa')
    return output.getvalue()

def create_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Gabaasa Waajjira Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='R')
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 8, "Maqaa", 1, 0, 'C', True)
    pdf.cell(30, 8, "Araddaa", 1, 0, 'C', True)
    pdf.cell(40, 8, "Gosa", 1, 0, 'C', True)
    pdf.cell(40, 8, "Ogeessa", 1, 0, 'C', True)
    pdf.cell(30, 8, "Kafaltii", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 9)
    for _, row in df.iterrows():
        pdf.cell(40, 7, str(row['Maqaa'])[:20], 1)
        pdf.cell(30, 7, str(row['Araddaa']), 1)
        pdf.cell(40, 7, str(row['Gosa']), 1)
        pdf.cell(40, 7, str(row['Ogeessa']), 1)
        pdf.cell(30, 7, str(row['Kafaltii']), 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SARTIIFIKETA (New Style) ---
def generate_certificate(expert_name, total_served):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(1.5); pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200)
    
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, x=130, y=15, w=35)
    
    pdf.ln(45)
    pdf.set_font('Times', 'B', 45); pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', 'I', 18); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Badhaasa Gootummaa Hojii Waggaa", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Times', 'B', 35); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(15); pdf.set_font('Arial', '', 15); pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 10, f"Waggaa kanatti tajaajila saffisaa fi qulqullina qabuun Abbootii Dhimmaa {total_served} tajaajiluun bu'aa qabeessa ta'anii waan argamaniif beekamtii kanaan badhaafamaniiru.", align='C')
    
    # Signatures - Position Adjusted (Gadi buufameera)
    pdf.set_y(170) 
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 8, "__________________________", ln=0, align='C')
    pdf.cell(87, 8, "", ln=0)
    pdf.cell(100, 8, "__________________________", ln=1, align='C')
    
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, datetime.now().strftime("%d/%m/%Y"), ln=1, align='C')
    pdf.set_font('Arial', '', 11)
    pdf.cell(100, 5, "Itti Gaafatamaa Waajjiraa", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, "Guyyaa", ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. UI APP ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 1, 1])
    with center:
        st.subheader("Login - Dadar Land")
        u =


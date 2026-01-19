import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
import plotly.express as px

# ================= 1. SETUP & CONFIGURATION =================
DATA_FILE = "dadar_land_data.txt"
NAGAHEE_DIR = "nagahee_scan"
LOGO_BITTA = "logo_bitta.jpg"
LOGO_MIRGA = "logo_mirga.jpg"

# TELEGRAM CONFIG (Maaloo kan kee galchi)
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide")

# ================= 2. FUNCTIONS =================

def load_data():
    cols = ['Guyyaa', 'Maqaa', 'Bilbila', 'Araddaa', 'Mana', 'Iddoo', 'Kaartaa', 'Tajaajila', 'Ogeessa', 'Kafaltii', 'Nagahee_Img']
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=cols)
    return pd.read_csv(DATA_FILE, sep="|", names=cols, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def get_ethiopian_date_str():
    now = datetime.now()
    e_date = EthiopianDateConverter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}"

def send_to_telegram(df):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Gabaasa')
        output.seek(0)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        files = {'document': ('Gabaasa_Dadar.xlsx', output, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        payload = {'chat_id': CHAT_ID_MANAGER, 'caption': f"📊 Gabaasa Hojii\nGuyyaa: {get_ethiopian_date_str()}"}
        res = requests.post(url, data=payload, files=files)
        return res.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    if os.path.exists(LOGO_BITTA): pdf.image(LOGO_BITTA, 15, 18, 23)
    if os.path.exists(LOGO_MIRGA): pdf.image(LOGO_MIRGA, 172, 18, 23)

    pdf.set_y(22); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(3); pdf.line(20, 56, 190, 56)

    pdf.ln(12); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    pdf.write(5, "Lakk. Galmee: "); pdf.set_font('Arial', 'B', 12)
    pdf.write(5, f"DAD/WL/{datetime.now().year}/____")
    pdf.set_x(140); pdf.set_font('Arial', '', 12)
    pdf.write(5, f"Guyyaa: {get_ethiopian_date_str()}"); pdf.ln(18)

    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    
    body = (f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Lakk. Bilbilaa {data['bilbila']} "
            f"Araddaa {data['araddaa']} Qaxana {data['qaxana']} keessatti qabiyye mana/lafa Lakk. Manaa {data['lakk_manaa']} "
            f"Lakk. Iddoo (Plot) {data['lakk_iddoo']} fi Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\n"
            f"Maamilli kun kaffaltii gibira waggaa hanga bara {data['bara']} E.C guutummaatti kaffalaniiru. "
            f"Qabiyyeen kun dhorkaa mana murtii ykn dhimma seeraa kamirrayyuu bilisa ta'uu isaa ni mirkaneessina.")
    pdf.multi_cell(0, 9, body)

    pdf.set_y(240); pdf.set_x(20); pdf.set_font('Arial', 'B', 12)
    pdf.write(8, f"Maqaa Itti Gaafatamaa: {data['head_name']}\nMallattoo: _________________")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = None

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026":
            st.session_state.logged_in = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📜 CLEARANCE", "📈 Gabaasa", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            st.metric("💰 Waliigala Galii", f"{df['Kafaltii'].sum():,.2f} ETB")
            fig = px.bar(df, x='Guyyaa', y='Kafaltii', title="Raawwii Galii")
            st.plotly_chart(fig, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("reg_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa *")
            phone = c2.text_input("Lakk. Bilbilaa *")
            ara = c1.text_input("Araddaa *")
            mana = c2.text_input("Lakk. Manaa")
            idd = c1.text_input("Lakk. Iddoo (Plot)")
            kaartaa = c2.text_input("Lakk. Kaartaa")
            taj = st.text_input("Gosa Tajaajilaa")
            ogeessa = c1.text_input("Ogeessa Raawwate")
            kaffaltii = c2.number_input("Kafaltii (ETB)", min_value=0.0)
            img_file = st.file_uploader("Nagahee Scan", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                img_name = "No_Image"
                if img_file:
                    img_name = f"{name.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg"
                    with open(os.path.join(NAGAHEE_DIR, img_name), "wb") as f: f.write(img_file.getbuffer())
                
                new_data = [get_ethiopian_date_str(), name, phone, ara, mana, idd, kaartaa, taj, ogeessa, kaffaltii, img_name]
                df = pd.concat([df, pd.DataFrame([new_data], columns=df.columns)], ignore_index=True)
                save_data(df)
                st.success("✅ Galmeeffameera!")

    elif menu == "📜 CLEARANCE":
        st.header("📜 Qophii Clearance")
        if st.session_state.pdf_ready:
            st.download_button("📥 PDF Buufadhu", st.session_state.pdf_ready, "Clearance.pdf", "application/pdf")
        
        with st.form("clr_form"):
            c1, c2 = st.columns(2)
            data = {
                'maqaa': c1.text_input("Maqaa Maamilaa *"),
                'bilbila': c2.text_input("Lakk. Bilbilaa *"),
                'araddaa': c1.text_input("Araddaa *"),
                'qaxana': c2.text_input("Qaxana"),
                'lakk_manaa': c1.text_input("Lakk. Manaa *"),
                'lakk_iddoo': c2.text_input("Lakk. Iddoo (Plot) *"),
                'kaartaa': c1.text_input("Lakk. Kaartaa *"),
                'bara': c2.text_input("Bara Gibiraa Xumurame"),
                'head_name': st.text_input("Maqaa Itti Gaafatamaa *")
            }
            if st.form_submit_button("📄 PDF UUMI"):
                st.session_state.pdf_ready = create_clearance_pdf(data)
                st.rerun()

    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa & Telegram")
        st.dataframe(df, use_container_width=True)
        if st.button("📤 Gabaasa Telegram-atti Ergi"):
            res = send_to_telegram(df)
            if res.get("ok"): st.success("✅ Ergameera!")
            else: st.error("Rakkoo uumame!")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

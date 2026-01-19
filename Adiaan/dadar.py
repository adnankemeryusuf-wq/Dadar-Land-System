import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. FUNCTIONS & LOGIC =================

try:
    from ethiopian_date import EthiopianDateConverter
except ImportError:
    class EthiopianDateConverter:
        def to_ethiopian(self, y, m, d):
            from dataclasses import dataclass
            @dataclass
            class EDate: day: int; month: int; year: int
            return EDate(d, m, y-8)

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date.day:02d}/{e_date.month:02d}/{e_date.year}"

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 18, 23)

    pdf.set_y(22)
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)

    pdf.ln(12); pdf.set_font('Arial', '', 12)
    pdf.set_x(20); pdf.write(5, "Lakk. Galmee: DAD/WL/2018/____")
    pdf.set_x(140); pdf.write(5, f"Guyyaa: {get_ethiopian_date_str()}")
    pdf.ln(18)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8)

    pdf.set_font('Arial', '', 12); pdf.set_x(20)
    pdf.write(9, f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} Qaxana {data['qaxana']} keessatti mana/lafa Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\n")

    pdf.write(9, f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} guutummaatti kaffalaniiru.\n")
    pdf.write(9, f"2. Kaffaltii {data['gosa_qabiyyee']} waliin wal-qabatu hunda raawwatanii xumuraniiru.\n")
    
    pdf.set_font('Arial', 'B', 12); pdf.write(9, "3. DHORKAA MANA MURTII: "); pdf.set_font('Arial', '', 12)
    pdf.write(9, "Qabiyyeen kun dhorkaa mana murtii kamirrayyuu bilisa ta'uu isaa mirkaneessineera.\n\n")

    pdf.write(9, f"Kanaafuu, dhimma {data['dhimma']} raawwachuuf mormii hin qabnu.")
    pdf.set_y(240); pdf.set_x(20); pdf.write(8, f"Maqaa Itti Gaafatamaa: {data['head_name']}\nMallattoo: _________________")
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ================= 2. CONFIGURATION =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0: 
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. UI & NAVIGATION =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'pdf_to_download' not in st.session_state: st.session_state.pdf_to_download = None

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.header("🏢 Admin Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📜 Qophii Clearance", "📈 Gabaasa", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Overview")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            st.plotly_chart(px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa', title="Trendii Kaffaltii"))

    elif menu == "📝 Galmee Tajaajilaa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c2.text_input("Araddaa")
            ogeessa = c1.text_input("Ogeessa Raawwate")
            fee = c2.number_input("Kaffaltii (ETB)", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "1", "Tajaajila Lafa", ogeessa, fee]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success("✅ Galmeeffameera!")

    elif menu == "📜 Qophii Clearance":
        st.header("📜 Qophii Waraqaa Qulqullinaa")
        with st.form("clear_form"):
            c1, c2 = st.columns(2)
            m_maqaa = c1.text_input("Maqaa Maamilaa *")
            m_kaartaa = c2.text_input("Lakk. Kaartaa *")
            m_bara = c1.text_input("Bara Gibiraa (Fkn: 2017)")
            m_head = c2.text_input("Itti Gaafatamaa *")
            m_dhimma = st.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa"])
            if st.form_submit_button("💾 PDF UUMI"):
                data = {'maqaa': m_maqaa, 'araddaa': "01", 'qaxana': "1", 'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 'head_name': m_head, 'gosa_qabiyyee': 'Liizii'}
                st.session_state.pdf_to_download = create_clearance_pdf(data)
                st.rerun()
        
        if st.session_state.pdf_to_download:
            st.download_button("📥 PDF BUUFADHU", st.session_state.pdf_to_download, "Clearance.pdf")

    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa Waliigalaa")
        st.dataframe(df)
        st.download_button("📥 CSV Buusi", df.to_csv(index=False).encode('utf-8'), "Gabaasa.csv")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()
        import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

# ================= 1. FUNCTIONS =================

def create_clearance_pdf(data, left_logo, right_logo):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # --- LOGO UPLOAD LOGIC ---
    # Logo Bittaa
    if left_logo:
        # Suuraa upload ta'e yeroo gabaabaaf ol kaaya
        with open("temp_left.png", "wb") as f:
            f.write(left_logo.getbuffer())
        pdf.image("temp_left.png", 15, 18, 23)
    
    # Logo Mirgaa
    if right_logo:
        with open("temp_right.png", "wb") as f:
            f.write(right_logo.getbuffer())
        pdf.image("temp_right.png", 172, 18, 23)

    # --- Header Section ---
    pdf.set_y(22)
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)

    # Subject & Body
    pdf.ln(25); pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    pdf.write(9, f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} keessatti mana/lafa Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\n")
    
    pdf.write(9, f"Kaffaltii gibiraa hanga bara {data['bara_gibiraa']} xumuran qabiyyeen kun dhorkaa mana murtii irraa bilisa ta'uu ni mirkaneessina.")

    # Signature
    pdf.set_y(240); pdf.set_x(20)
    pdf.write(8, f"Maqaa Itti Gaafatamaa: {data['head_name']}\nMallattoo: _________________")

    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ================= 2. STREAMLIT UI =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

# --- SIDEBAR UPLOAD ---
st.sidebar.header("🖼️ Logo Waajjiraa")
logo_l = st.sidebar.file_uploader("Logo Bittaa (Left)", type=['jpg', 'png', 'jpeg'])
logo_r = st.sidebar.file_uploader("Logo Mirgaa (Right)", type=['jpg', 'png', 'jpeg'])

if logo_l: st.sidebar.image(logo_l, caption="Logo Bittaa", width=100)
if logo_r: st.sidebar.image(logo_r, caption="Logo Mirgaa", width=100)

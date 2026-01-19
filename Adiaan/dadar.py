import streamlit as st
import pandas as pd
import os, io
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & CONSTANTS =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
    "🏗 Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"]
}

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def get_ethiopian_date_str():
    now = datetime.now()
    e_date = EthiopianDateConverter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}"

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)
    
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 18, 23)

    pdf.set_y(22); pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 50, 190, 50)
    pdf.ln(12); pdf.set_font('Arial', '', 12)
    
    e_date = EthiopianDateConverter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)
    pdf.set_x(20); pdf.write(5, f"Lakk. Galmee: DAD/WL/{e_date[0]}/____")
    pdf.set_x(140); pdf.write(5, f"Guyyaa: {e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}")
    
    pdf.ln(18); pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    
    pdf.ln(8); pdf.set_font('Arial', '', 12); pdf.set_x(20)
    body = f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} Araddaa {data['araddaa']} Qaxana {data['qaxana']} keessatti mana/lafa Lakk. Kaartaa {data['kaartaa']} qabaniif kan kennameedha.\n\nMaamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} E.C guutummaatti kaffalaniiru.\n2. Kaffaltii tajaajilaa hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina.\n3. Lafni/Manni kun DHORKAA MANA MURTII kamirrayyuu bilisa ta'uu isaa qulqulleessineera.\n\nKanaafuu, dhimma {data['dhimma']} raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan ni mirkaneessina."
    pdf.multi_cell(170, 8, body)
    
    pdf.set_y(240); pdf.set_x(20); pdf.write(8, f"Maqaa Itti Gaafatamaa: {data['head_name']}\nMallattoo: _________________")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'pdf_to_download' not in st.session_state: st.session_state.pdf_to_download = None

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
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📜 CLEARANCE", "🏆 Badhaasa", "📈 Gabaasa", "Ba'i"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Maamiltootaa", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.subheader("Trendii Kaffaltii")
            fig = px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa')
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Data'n galmeeffame hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        final_services, total_fee = [], 0
        
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    subs = st.multiselect(f"{cat}:", SERVICE_STRUCTURE[cat], key=cat)
                    for s in subs:
                        fee = st.number_input(f"Kafaltii {s}:", min_value=0.0, key=f"f_{s}")
                        final_services.append(s); total_fee += fee

        with st.form("reg_form"):
            name = st.text_input("Maqaa Maamilaa")
            ara = st.text_input("Araddaa")
            ogeessa = st.text_input("Ogeessa Raawwate")
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", ", ".join(final_services), ogeessa, total_fee]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df); st.success("Galmeeffameera!")

    # --- CLEARANCE ---
    elif menu == "📜 CLEARANCE":
        st.header("📝 Qophii Waraqaa Qulqullinaa")
        if st.session_state.pdf_to_download:
            st.download_button("📥 PDF Buufadhu", st.session_state.pdf_to_download, "Clearance.pdf", "application/pdf")
            if st.button("🔄 Haaraa Jalqabi"): st.session_state.pdf_to_download = None; st.rerun()

        with st.form("clearance_form"):
            c1, c2 = st.columns(2)
            m_maqaa = c1.text_input("Maqaa Maamilaa *")
            m_kaartaa = c2.text_input("Lakk. Kaartaa *")
            m_bara = c1.text_input("Bara Gibiraa (E.C)")
            m_dhimma = c2.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa"])
            m_head = st.text_input("Maqaa Itti Gaafatamaa")
            m_bilisa = st.checkbox("Dhorkaa irraa bilisa ta'uu nan mirkaneessa")
            
            if st.form_submit_button("💾 PDF UUMI"):
                data = {'maqaa': m_maqaa, 'araddaa': "-", 'qaxana': "-", 'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 'head_name': m_head}
                st.session_state.pdf_to_download = create_clearance_pdf(data)
                st.rerun()

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeeyyii")
        if not df.empty:
            top = df['Maqaa_Ogeessa'].value_counts().head(3)
            st.write(top)
        else: st.info("Data'n hin jiru.")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa":
        st.header("📋 Galmeewwan Hundi")
        st.dataframe(df, use_container_width=True)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

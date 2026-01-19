import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from PIL import Image

# ================= 1. SETUP =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

if 'pdf_to_download' not in st.session_state:
    st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

# ================= 2. FUNCTIONS =================

def get_ethiopian_date_str():
    now = datetime.now()
    converter = EthiopianDateConverter()
    e_date = converter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date.day:02d}/{e_date.month:02d}/{e_date.year}"

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Double line)
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Logos
    if os.path.exists("logo_bitta.jpg"): pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): pdf.image("logo_mirga.jpg", 172, 18, 23)

    # --- Header Section (Tartiiba Ati Gaafatte) ---
    pdf.set_y(22)
    pdf.set_font('Times', 'B', 15)
    # 1. Naannoo
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    
    pdf.set_font('Times', 'B', 14)
    # 2. Waajjira
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    # 3. Bulchiinsa Magaalaa
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    # Header Underline
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)

    # Date and Ref No
    pdf.ln(12); pdf.set_font('Times', '', 12)
    guyyaa_ec = get_ethiopian_date_str()
    converter = EthiopianDateConverter()
    now_ec = converter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)

    pdf.set_x(20)
    pdf.write(5, "Lakk. Galmee: ")
    pdf.set_font('Times', 'B', 12) 
    pdf.write(5, f"DAD/WL/{now_ec.year}/____")
    pdf.set_font('Times', '', 12)
    pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {guyyaa_ec}")
    pdf.ln(18)

    # Subject
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8)

    # Body
    pdf.set_font('Times', '', 12)
    pdf.set_x(20)
    
    pdf.write(9, "Waraqaan ragaa kun Obbo/Adde/Dhaabbata ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['maqaa'].upper()}")
    pdf.set_font('Times', '', 12); pdf.write(9, " Araddaa ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['araddaa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " Qaxana ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['qaxana']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " keessatti mana/lafa Lakk. Kaartaa ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['kaartaa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " qabaniif kan kennameedha.\n\n")

    pdf.write(9, "Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n")

    # Items
    pdf.write(9, "1. Kaffaltii Gibira waggaa hanga bara ")
    pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['bara_gibiraa']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " guutummaatti kaffalaniiru.\n")

    if data.get('gosa_qabiyyee') == "Liizii":
        pdf.write(9, "2. Kaffaltii "); pdf.set_font('Times', 'B', 12); pdf.write(9, "Liizii")
        pdf.set_font('Times', '', 12); pdf.write(9, " waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")
    else:
        pdf.write(9, "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")

    pdf.write(9, "3. Lafni/Manni kun "); pdf.set_font('Times', 'B', 12); pdf.write(9, "DHORKAA MANA MURTII")
    pdf.set_font('Times', '', 12); pdf.write(9, " ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n")

    pdf.write(9, "Kanaafuu, maamilli kun dhimma "); pdf.set_font('Times', 'B', 12); pdf.write(9, f"{data['dhimma']}")
    pdf.set_font('Times', '', 12); pdf.write(9, " raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina.")

    # --- SIGNATURE SECTION ---
    pdf.set_y(235)
    pdf.set_x(20)
    pdf.set_font('Times', '', 12); pdf.write(8, "Maqaa Itti Gaafatamaa: ")
    pdf.set_font('Times', 'B', 12); pdf.write(8, f"{data['head_name']}")
    
    pdf.ln(8); pdf.set_x(20)
    pdf.set_font('Times', '', 12); pdf.write(8, "Mallattoo: _________________")
    
    # Stamp (Right)
    pdf.set_y(243); pdf.set_x(120)
    pdf.set_font('Times', 'B', 11)
    pdf.cell(70, 8, "(Chaappaa Waajjiraa)", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')
    
 ================= 3. STREAMLIT UI =================
st.header("📝 Sirna Qophii Waraqaa Qulqullinaa (Clearance)")
with st.form("clearance_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    m_maqaa = c1.text_input("Maqaa Maamilaa *")
    m_araddaa = c2.text_input("Araddaa *")
    m_qaxana = c1.text_input("Lakk. Qaxana *")
    m_kaartaa = c2.text_input("Lakk. Kaartaa *")
    m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii (Permit)"])
    m_bara = c2.text_input("Bara Gibiraa Xumurame (Fkn: 2017)")
    m_dhimma = c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
    st.markdown("---")
    m_head = st.text_input("Maqaa Itti Gaafatamaa *")
    m_dhorkaa_bilisa = st.checkbox("Qabiyyeen kun dhorkaa irraa bilisa ta'uu nan mirkaneessa.")

    if st.form_submit_button("💾 PDF UUMI"):
        if all([m_maqaa, m_kaartaa, m_head, m_dhorkaa_bilisa]):
            data_map = {
                'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 
                'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 
                'gosa_qabiyyee': m_gosa, 'head_name': m_head
            }
            st.session_state.pdf_to_download = create_clearance_pdf(data_map)
            st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
            st.rerun()
# ================= 2. CONFIGURATION & DATA =================
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

SERVICE_STRUCTURE = {
    "🏷️ Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Jijjiirraa Maqaa", "Sirreeffama Daangaa"],
    "🏗️ Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"]
}

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0: 
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. UI & NAVIGATION =================
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
            else:
                st.error("Dogoggora! Maaloo irra deebi'ii yaali.")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📜 Qophii Clearance", "📈 Gabaasa", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Overview")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.plotly_chart(px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa', title="Trendii Kaffaltii"))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        selected_cats = st.multiselect("Gosa Tajaajilaa Filadhu:", list(SERVICE_STRUCTURE.keys()))
        final_services, total_fee = [], 0
        
        if selected_cats:
            for cat in selected_cats:
                subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat], key=cat)
                for s in subs:
                    final_services.append(s)
                    total_fee += st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"f_{s}")

        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                else:
                    st.error("Maaloo odeeffannoo guutuu galchi.")

    elif menu == "📜 Qophii Clearance":
        st.header("📜 Qophii Waraqaa Qulqullinaa")
        
        if st.session_state.pdf_to_download:
            st.download_button("📥 PDF BUUFADHU", st.session_state.pdf_to_download, "Clearance.pdf")
            if st.button("🔄 Galmee Haaraa"): 
                st.session_state.pdf_to_download = None
                st.rerun()
        
       ================= 3. STREAMLIT UI =================
st.header("📝 Sirna Qophii Waraqaa Qulqullinaa (Clearance)")
with st.form("clearance_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    m_maqaa = c1.text_input("Maqaa Maamilaa *")
    m_araddaa = c2.text_input("Araddaa *")
    m_qaxana = c1.text_input("Lakk. Qaxana *")
    m_kaartaa = c2.text_input("Lakk. Kaartaa *")
    m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii (Permit)"])
    m_bara = c2.text_input("Bara Gibiraa Xumurame (Fkn: 2017)")
    m_dhimma = c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
    st.markdown("---")
    m_head = st.text_input("Maqaa Itti Gaafatamaa *")
    m_dhorkaa_bilisa = st.checkbox("Qabiyyeen kun dhorkaa irraa bilisa ta'uu nan mirkaneessa.")

    if st.form_submit_button("💾 PDF UUMI"):
        if all([m_maqaa, m_kaartaa, m_head, m_dhorkaa_bilisa]):
            data_map = {
                'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 
                'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 
                'gosa_qabiyyee': m_gosa, 'head_name': m_head
            }
            st.session_state.pdf_to_download = create_clearance_pdf(data_map)
            st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
            st.rerun()
:
        st.header("📈 Gabaasa Waliigalaa")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV Buusi", csv, "Gabaasa_Dadar.csv", "text/csv")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()





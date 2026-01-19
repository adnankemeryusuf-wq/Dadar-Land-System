
import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Admin Pro", 
    page_icon="🏢", 
    layout="wide"
)

# Halluu fi Style
st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. SERVICE LIST (GOSA TAJAAJILAA) =================
# Gosa tajaajilaa hunda akka gosa gurguddaatti addaan baasuu
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"
    ]
}

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_certificate(name, count, rank, l_l, l_r, sig):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_draw_color(0, 100, 0); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    
    # Logo
    if l_l: 
        with open("tmp_l.png", "wb") as f: f.write(l_l.getbuffer())
        pdf.image("tmp_l.png", 20, 15, 30)
    
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    
    # Signature
    if sig:
        with open("tmp_sig.png", "wb") as f: f.write(sig.getbuffer())
        pdf.image("tmp_sig.png", 50, 160, 30)
    
    pdf.line(40, 180, 100, 180); pdf.set_xy(40, 182); pdf.cell(60, 10, "Itti Gaafatamaa", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Section
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026": 
            st.session_state.logged_in = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa"])

# --- REGISTRATION ---
    if menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        
        # Filannoo Tajaajilaa
        st.subheader("🟢 Gosa Tajaajilaa Filadhu")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        
        final_services = []
        total_fee = 0
        
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    st.write(f"{cat}")
                    subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat], key=cat)
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"fee_{s}")
                        final_services.append(s)
                        total_fee += fee

        st.divider()
        
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Maamilaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            
            # Nagahee Upload
            nagahee = st.file_uploader("Nagahee Scan (Image)", type=['jpg','png','jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services:
                    # Save Image
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    
                    # Save Data
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Waliigala: {total_fee} ETB")
                else:
                    st.error("Maaloo odeeffannoo guutuu galchi!")

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Maamiltootaa", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            st.subheader("Trendii Kaffaltii")
            fig = px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa')
            st.plotly_chart(fig, use_container_width=True)

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeeyyii")
        sig = st.file_uploader("Mallattoo Itti Gaafatamaa (PNG)", type=['png'])
        if not df.empty:
            top = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (n, c) in enumerate(top.items(), 1):
                st.write(f"{i}. {n} ({c} tajaajila)")
                pdf = create_certificate(n, c, i, None, None, sig)
                st.download_button(f"📥 Sartiifikeeta {n}", pdf, f"Cert_{n}.pdf")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa":
        st.header("📋 Galmeewwan Hundi")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Excel/CSV Buusi", csv, "Gabaasa.csv", "text/csv")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF
# Library kana 'pip install ethiopian-date' godhii fe'adhu
from ethiopian_date import EthiopianDateConverter

# ================= 1. SETUP =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide", page_icon="🏢")

if 'pdf_to_download' not in st.session_state:
    st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

# ================= 2. FUNCTIONS =================

def get_ethiopian_date_str():
    """Guyyaa har'aa gara Itoophiyaatti jijjiiruuf"""
    now = datetime.now()
    # Tooftaa sirrii library ethiopian-date itti fayyadaman
    e_date = EthiopianDateConverter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}"

def create_clearance_pdf(data):
    # 'latin-1' bakka 'Arial' ykn 'Times' itti fayyadamnuuf 'FPDF' qofaan gahaa dha
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Double line)
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Logos (Checking if they exist before drawing)
    if os.path.exists("logo_bitta.jpg"): 
        pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): 
        pdf.image("logo_mirga.jpg", 172, 18, 23)

    # --- Header Section ---
    pdf.set_y(22)
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    # Header Underline
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 50, 190, 50)

    # Date and Ref No
    pdf.ln(12); pdf.set_font('Arial', '', 12)
    guyyaa_ec = get_ethiopian_date_str()
    
    # Lakk Galmee (Year calculation in EC)
    now = datetime.now()
    e_year = EthiopianDateConverter.to_ethiopian(now.year, now.month, now.day)[0]

    pdf.set_x(20)
    pdf.write(5, "Lakk. Galmee: ")
    pdf.set_font('Arial', 'B', 12) 
    pdf.write(5, f"DAD/WL/{e_year}/____")
    
    pdf.set_font('Arial', '', 12)
    pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {guyyaa_ec}")
    pdf.ln(18)

    # Subject
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8)

    # Body
    pdf.set_font('Arial', '', 12)
    pdf.set_x(20)
    
    # Multi-cell or writing for better flow
    body_text = (
        f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} "
        f"Araddaa {data['araddaa']} Qaxana {data['qaxana']} keessatti mana/lafa Lakk. Kaartaa "
        f"{data['kaartaa']} qabaniif kan kennameedha.\n\n"
        f"Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n"
    )
    pdf.set_x(20)
    pdf.multi_cell(170, 8, body_text)

    # Items
    pdf.set_x(20)
    pdf.write(8, "1. Kaffaltii Gibira waggaa hanga bara ")
    pdf.set_font('Arial', 'B', 12); pdf.write(8, f"{data['bara_gibiraa']} E.C"); pdf.set_font('Arial', '', 12)
    pdf.write(8, " guutummaatti kaffalaniiru.\n")

    pdf.set_x(20)
    if data.get('gosa_qabiyyee') == "Liizii":
        pdf.write(8, "2. Kaffaltii ")
        pdf.set_font('Arial', 'B', 12); pdf.write(8, "Liizii"); pdf.set_font('Arial', '', 12)
        pdf.write(8, " waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")
    else:
        pdf.write(8, "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")

    pdf.set_x(20)
    pdf.write(8, "3. Lafni/Manni kun ")
    pdf.set_font('Arial', 'B', 12); pdf.write(8, "DHORKAA MANA MURTII"); pdf.set_font('Arial', '', 12)
    pdf.write(8, " ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n")

    pdf.set_x(20)
    pdf.multi_cell(170, 8, f"Kanaafuu, maamilli kun dhimma {data['dhimma']} raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina.")

    # --- SIGNATURE SECTION ---
    pdf.set_y(235); pdf.set_x(20)
    pdf.set_font('Arial', '', 12); pdf.write(8, "Maqaa Itti Gaafatamaa: ")
    pdf.set_font('Arial', 'B', 12); pdf.write(8, f"{data['head_name']}")
    
    pdf.ln(8); pdf.set_x(20)
    pdf.set_font('Arial', '', 12); pdf.write(8, "Mallattoo: _________________")
    
    # Stamp (Right)
    pdf.set_y(243); pdf.set_x(120)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(70, 8, "(Chaappaa Waajjiraa)", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')

# ================= 3. STREAMLIT UI =================
st.header("📝 Sirna Qophii Waraqaa Qulqullinaa (Clearance)")

# To show download button if PDF is ready
if st.session_state.pdf_to_download:
    st.success(f"✅ PDF'n {st.session_state.pdf_name} qophaa'eera!")
    st.download_button(
        label="📥 PDF Buufadhu",
        data=st.session_state.pdf_to_download,
        file_name=st.session_state.pdf_name,
        mime="application/pdf"
    )
    if st.button("🔄 Haaraa Jalqabi"):
        st.session_state.pdf_to_download = None
        st.rerun()

with st.form("clearance_form", clear_on_submit=False):
    st.info("Odeeffannoo maamilaa guuti")
    c1, c2 = st.columns(2)
    m_maqaa = c1.text_input("Maqaa Maamilaa *")
    m_araddaa = c2.text_input("Araddaa *")
    m_qaxana = c1.text_input("Lakk. Qaxana *")
    m_kaartaa = c2.text_input("Lakk. Kaartaa *")
    m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii (Permit)"])
    m_bara = c2.text_input("Bara Gibiraa Xumurame (E.C)")
    m_dhimma = c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
    
    st.markdown("---")
    m_head = st.text_input("Maqaa Itti Gaafatamaa *")
    m_dhorkaa_bilisa = st.checkbox("Qabiyyeen kun dhorkaa irraa bilisa ta'uu nan mirkaneessa.")

    submit = st.form_submit_button("💾 PDF UUMI")
    
    if submit:
        if m_maqaa and m_kaartaa and m_head and m_dhorkaa_bilisa:
            data_map = {
                'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 
                'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 
                'gosa_qabiyyee': m_gosa, 'head_name': m_head
            }
            try:
                st.session_state.pdf_to_download = create_clearance_pdf(data_map)
                st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
                st.rerun()
            except Exception as e:
                st.error(f"Dogoggora: {e}")
        else:
            st.warning("Maaloo, dirree '*' qaban hunda guuti, akkasumas mirkaneessi.")



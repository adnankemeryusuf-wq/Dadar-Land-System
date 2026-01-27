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
LOGO_FILE = "logo_waajjiraa.png" # Suuraa logo keetii folder tokko keessa kaa'i

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

# Miidhagina Appichaa
st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #2e7d32; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            text-align: center; border-top: 5px solid #2e7d32; }
    .sidebar .sidebar-content { background: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CONSTANTS & DATA =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
    "🏗 Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"]
}

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Nagahee_Img']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    # Border
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    
    # Logo on PDF
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, 10, 12, 25)
        pdf.image(LOGO_FILE, 175, 12, 25)
    
    pdf.set_y(15); pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "WAAJJIRA LAFAA BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(10)
    
    e_date = EthiopianDateConverter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Lakk: DAD/WL/{e_date[0]}/____ \t\t\t\t\t\t\t Guyyaa: {e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}", ln=True)
    
    pdf.ln(5); pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 12)
    body = (f"Waraqaan ragaa kun Obbo/Adde {data['maqaa'].upper()} kaartaa lakk {data['kaartaa']} "
            f"Araddaa {data['araddaa']} keessatti qabaniif kan kennameedha. Maamilli kun "
            f"gibira waggaa hanga bara {data['bara']} E.C guutummaatti kaffalaniiru. "
            f"Qabiyyeen kun dhorkaa murtii kamirrayyuu bilisa ta'uu isaa ni mirkaneessina.")
    pdf.multi_cell(0, 10, body)
    
    pdf.set_y(240); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Itti Gaafatamaa: {data['head_name']}", ln=True)
    pdf.cell(0, 10, "Mallattoo: _________________", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP NAVIGATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = None

if not st.session_state.logged_in:
    # LOGIN PAGE
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=150)
        st.title("🔐 Dadar Land Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni", use_container_width=True):
            if u == "DAD" and p == "2026": 
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    # SIDEBAR LOGO
    if os.path.exists(LOGO_FILE):
        st.sidebar.image(LOGO_FILE, width=100)
    st.sidebar.title("Dadar Land Admin")
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📜 CLEARANCE", "🏆 Badhaasa", "📈 Gabaasa", "Ba'i"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Raawwii Hojii")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h3>💰 Waliigala Galii</h3><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h3>👥 Maamiltoota</h3><h2>{len(df)}</h2><p>Tajaajilaman</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h3>👷 Ogeeyyii</h3><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Hojii irra jiran</p></div>", unsafe_allow_html=True)
            
            st.subheader("📈 Galii Guyyaan")
            df_plot = df.groupby('Guyyaa')['Kafaltii_Taj'].sum().reset_index()
            fig = px.bar(df_plot, x='Guyyaa', y='Kafaltii_Taj', color_discrete_sequence=['#2e7d32'])
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Data'n galmeeffame hin jiru.")

    # --- GALMEE HAARAA (WITH SCAN) ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa fi Nagahee Scan")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa Filadhu:", list(SERVICE_STRUCTURE.keys()))
        
        final_services, total_fee = [], 0
        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    subs = st.multiselect(f"{cat}:", SERVICE_STRUCTURE[cat], key=f"sel_{cat}")
                    for s in subs:
                        fee = st.number_input(f"Kafaltii {s}:", min_value=0.0, key=f"f_{s}")
                        final_services.append(s); total_fee += fee

        with st.form("reg_form_main"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee_file = st.file_uploader("Nagahee Scan (Suuraa)", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and ogeessa and final_services:
                    img_name = "No_Image"
                    if nagahee_file:
                        img_name = f"{name.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, img_name), "wb") as f:
                            f.write(nagahee_file.getbuffer())
                    
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee, img_name]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Waliigala: {total_fee} ETB")
                else: st.error("Maaloo odeeffannoo guutuu galchi!")

    # --- CLEARANCE ---
    elif menu == "📜 CLEARANCE":
        st.header("📜 Qophii Waraqaa Qulqullinaa")
        if st.session_state.pdf_ready:
            st.download_button("📥 PDF Buufadhu", st.session_state.pdf_ready, "Clearance_Dadar.pdf", "application/pdf")
            if st.button("🔄 Haaraa Jalqabi"): st.session_state.pdf_ready = None; st.rerun()

        with st.form("clearance_form_pro"):
            col1, col2 = st.columns(2)
            c_name = col1.text_input("Maqaa Maamilaa")
            c_ara = col2.text_input("Araddaa")
            c_kaartaa = col1.text_input("Lakk. Kaartaa")
            c_bara = col2.text_input("Bara Gibiraa (E.C)")
            c_dhimma = st.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
            c_head = st.text_input("Maqaa Itti Gaafatamaa")
            
            if st.form_submit_button("📄 PDF UUMI"):
                if c_name and c_kaartaa:
                    clr_data = {'maqaa': c_name, 'araddaa': c_ara, 'kaartaa': c_kaartaa, 'bara': c_bara, 'head_name': c_head, 'dhimma': c_dhimma}
                    st.session_state.pdf_ready = create_clearance_pdf(clr_data)
                    st.rerun()
                else: st.warning("Maaqaa fi Kaartaa galchi!")

    # --- GABAASA (WITH IMAGE VIEW) ---
    elif menu == "📈 Gabaasa":
        st.header("📋 Galmeewwan Hundi fi Ragaa Nagahee")
        if not df.empty:
            st.dataframe(df.drop(columns=['Nagahee_Img']), use_container_width=True)
            
            st.divider()
            st.subheader("🔍 Nagahee Scan godhame Ilaali")
            search_name = st.selectbox("Maqaa Maamilaa Filadhu:", ["---"] + df['Maqaa_Abbaa_Dhimmaa'].tolist())
            if search_name != "---":
                row = df[df['Maqaa_Abbaa_Dhimmaa'] == search_name].iloc[-1] # Isa dhumaa fidi
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.write(f"**Guyyaa:** {row['Guyyaa']}")
                    st.write(f"**Tajaajila:** {row['Gosa_Tajajjilaa']}")
                    st.write(f"**Kafaltii:** {row['Kafaltii_Taj']} ETB")
                    st.write(f"**Ogeessa:** {row['Maqaa_Ogeessa']}")
                with c2:
                    img_path = os.path.join(NAGAHEE_DIR, str(row['Nagahee_Img']))
                    if os.path.exists(img_path) and row['Nagahee_Img'] != "No_Image":
                        st.image(img_path, caption=f"Nagahee {search_name}", use_container_width=True)
                    else: st.warning("Suuraan nagahee hin argamne.")
        else: st.info("Gabaasni argamu hin jiru.")

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeeyyii")
        if not df.empty:
            top = df['Maqaa_Ogeessa'].value_counts()
            for name, count in top.items():
                st.write(f"⭐ **{name}**: {count} tajaajila kennaan.")
        else: st.info("Data'n hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

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

# Folder nagaheen itti kuufamu yoo hin jirre uumi
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", page_icon="🏢", layout="wide")

# Miidhagina Appichaa (CSS)
st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #2e7d32; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
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

# Column'n 8ffaan (Index 7) maqaa suuraa nagahee ti
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
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277) # Border
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    body = f"Maamilli maqaan isaanii {data['maqaa']} ta'an, kaartaa lakk {data['kaartaa']} irratti gibira bara {data['bara']} xumuraniiru. Dhorkaa murtii kamirrayyuu bilisa ta'uu isaanii ni mirkaneessina."
    pdf.multi_cell(0, 10, body)
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
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📜 CLEARANCE", "🏆 Badhaasa", "📈 Gabaasa", "Ba'i"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Raawwii Hojii")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h3>💰 Galii</h3><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h3>👥 Maamiltoota</h3><h2>{len(df)}</h2><p>Walitti qabaa</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h3>👷 Ogeeyyii</h3><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Hojii irra jiran</p></div>", unsafe_allow_html=True)
            
            st.subheader("📈 Trendii Galii Guyyaan")
            fig = px.line(df.groupby('Guyyaa')['Kafaltii_Taj'].sum().reset_index(), x='Guyyaa', y='Kafaltii_Taj', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Data'n galmeeffame hin jiru.")

    # --- GALMEE HAARAA (REGISTRATION WITH SCAN) ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa fi Nagahee Scan")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa Filadhu:", list(SERVICE_STRUCTURE.keys()))
        
        final_services, total_fee = [], 0
        if selected_cats:
            for cat in selected_cats:
                subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat])
                for s in subs:
                    fee = st.number_input(f"Kaffaltii {s} (ETB):", min_value=0.0, key=s)
                    final_services.append(s); total_fee += fee

        with st.form("main_reg_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col2.text_input("Araddaa")
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            nagahee_file = st.file_uploader("Nagahee Scan (Suuraa)", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("💾 Galmeessi"):
                if name and ogeessa and final_services:
                    img_name = "No_Image"
                    if nagahee_file:
                        img_name = f"{name.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.jpg"
                        with open(os.path.join(NAGAHEE_DIR, img_name), "wb") as f:
                            f.write(nagahee_file.getbuffer())
                    
                    new_data = [datetime.now().strftime('%d/%m/%Y'), name, ara, "-", ", ".join(final_services), ogeessa, total_fee, img_name]
                    df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeen Milka'inaan Raawwatameera!")
                else: st.error("Maaloo odeeffannoo guutuu galchi!")

    # --- CLEARANCE ---
    elif menu == "📜 CLEARANCE":
        st.header("📜 Qophii Waraqaa Qulqullinaa")
        if st.session_state.pdf_ready:
            st.download_button("📥 PDF Buufadhu", st.session_state.pdf_ready, "Clearance.pdf", "application/pdf")

        with st.form("clr_form"):
            c_name = st.text_input("Maqaa Maamilaa")
            c_kaartaa = st.text_input("Lakk. Kaartaa")
            c_bara = st.text_input("Bara Gibiraa (E.C)")
            if st.form_submit_button("📄 PDF UUMI"):
                clr_data = {'maqaa': c_name, 'kaartaa': c_kaartaa, 'bara': c_bara}
                st.session_state.pdf_ready = create_clearance_pdf(clr_data)
                st.rerun()

    # --- GABAASA (REPORT WITH IMAGE VIEW) ---
    elif menu == "📈 Gabaasa":
        st.header("📋 Galmeewwan Hundi fi Ragaa Nagahee")
        if not df.empty:
            st.dataframe(df.iloc[:, :-1], use_container_width=True) # Suuraa malee table fidi
            
            st.subheader("🔍 Nagahee Ilaaluuf")
            search_name = st.selectbox("Maqaa Filadhu:", ["---"] + df['Maqaa_Abbaa_Dhimmaa'].tolist())
            if search_name != "---":
                row = df[df['Maqaa_Abbaa_Dhimmaa'] == search_name].iloc[0]
                st.write(f"**Ogeessa:** {row['Maqaa_Ogeessa']} | **Kafaltii:** {row['Kafaltii_Taj']} ETB")
                
                img_path = os.path.join(NAGAHEE_DIR, row['Nagahee_Img'])
                if os.path.exists(img_path) and row['Nagahee_Img'] != "No_Image":
                    st.image(img_path, caption=f"Nagahee {search_name}", width=500)
                else:
                    st.warning("Nagaheen suuraa hin qabu.")
        else: st.info("Data'n hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

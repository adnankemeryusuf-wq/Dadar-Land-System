import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from PIL import Image

# ================= 1. FUNCTIONS & PDF LOGIC =================

def get_ethiopian_date_str():
    # Herrega salphaa (Approximate for 2018 E.C)
    now = datetime.now()
    e_year = now.year - 8 if now.month > 9 or (now.month == 9 and now.day >= 11) else now.year - 9
    e_month = (now.month + 3) % 12 + 1
    e_day = now.day 
    return f"{e_day:02d}/{e_month:02d}/{e_year}"

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Double line)
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # --- LOGOS (BITTAA FI MIRGA) ---
    if os.path.exists("logo_bitta.jpg"): 
        pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): 
        pdf.image("logo_mirga.jpg", 172, 18, 23)

    # --- Header Section ---
    pdf.set_y(22)
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 56, 190, 56)

    # Date and Ref No
    pdf.ln(12); pdf.set_font('Arial', '', 12)
    pdf.set_x(20)
    pdf.write(5, "Lakk. Galmee: ")
    pdf.set_font('Arial', 'B', 12); pdf.write(5, f"DAD/WL/2018/____")
    pdf.set_font('Arial', '', 12); pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {get_ethiopian_date_str()}")
    pdf.ln(18)

    # Subject
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8)

    # Body
    pdf.set_font('Arial', '', 12); pdf.set_x(20)
    pdf.write(9, "Waraqaan ragaa kun Obbo/Adde/Dhaabbata ")
    pdf.set_font('Arial', 'B', 12); pdf.write(9, f"{data['maqaa'].upper()}")
    pdf.set_font('Arial', '', 12); pdf.write(9, f" Araddaa {data['araddaa']} keessatti qabiyyee Lakk. Kaartaa ")
    pdf.set_font('Arial', 'B', 12); pdf.write(9, f"{data['kaartaa']}")
    pdf.set_font('Arial', '', 12); pdf.write(9, " qabaniif kan kennameedha.\n\n")

    pdf.write(9, f"1. Kaffaltii Gibira waggaa hanga bara {data['bara_gibiraa']} guutummaatti kaffalaniiru.\n")
    pdf.write(9, "2. Kaffaltii tajaajilaa hunda raawwatanii kan xumuran ta'uu ni mirkaneessina.\n")

    # --- DHORKAA MANA MURTII ---
    pdf.set_font('Arial', 'B', 12)
    pdf.write(9, "3. DHORKAA MANA MURTII: ")
    pdf.set_font('Arial', '', 12)
    
    if data['haala_dhorkaa'] == "Dhorkaa qaba":
        pdf.set_text_color(200, 0, 0) # Halluu Diimaa
        pdf.write(9, "Qabiyyeen kun DHORKAA MANA MURTII waan qabuuf tajaajilli kamiyyuu akka hin kennamne ni hubachiifna.")
    else:
        pdf.write(9, "Lafni/Manni kun dhorkaa mana murtii ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa mirkaneessineera.")
    
    pdf.set_text_color(0, 0, 0) 
    pdf.ln(12)
    pdf.write(9, f"Kanaafuu, dhimma {data['dhimma']} raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan ni mirkaneessina.")

    # --- Signature ---
    pdf.set_y(240); pdf.set_x(20)
    pdf.write(8, f"Maqaa Itti Gaafatamaa: {data['head_name']}\nMallattoo: _________________")
    pdf.set_y(245); pdf.set_x(130); pdf.set_font('Arial', 'B', 11)
    pdf.cell(60, 8, "(Chaappaa Waajjiraa)", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1', 'ignore')

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
        
        with st.form("clear_form"):
            c1, c2 = st.columns(2)
            m_maqaa = c1.text_input("Maqaa Maamilaa *")
            m_kaartaa = c2.text_input("Lakk. Kaartaa *")
            m_araddaa = c1.text_input("Araddaa")
            m_bara = c2.text_input("Bara Gibiraa (Fkn: 2017)")
            m_dhorkaa = c1.selectbox("Haala Dhorkaa Mana Murtii *", ["Bilisa", "Dhorkaa qaba"])
            m_dhimma = c2.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
            m_head = st.text_input("Maqaa Itti Gaafatamaa *")
            
            if st.form_submit_button("💾 PDF UUMI"):
                if m_maqaa and m_kaartaa and m_head:
                    data = {
                        'maqaa': m_maqaa, 'araddaa': m_araddaa, 'kaartaa': m_kaartaa,
                        'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 'head_name': m_head,
                        'haala_dhorkaa': m_dhorkaa
                    }
                    st.session_state.pdf_to_download = create_clearance_pdf(data)
                    st.rerun()

    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa Waliigalaa")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV Buusi", csv, "Gabaasa_Dadar.csv", "text/csv")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

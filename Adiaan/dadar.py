import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & SETUP =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# Session State
if 'pdf_to_download' not in st.session_state: st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state: st.session_state.pdf_name = ""

# ================= 2. CORE FUNCTIONS =================

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)
        df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_clearance_pdf(name, araddaa, qaxana, services, nagahee_lakk):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.5)
    pdf.rect(10, 10, 190, 277)
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 90, 15, 25)
    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.cell(0, 10, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'U', 14)
    pdf.cell(0, 10, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.set_y(90)
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
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI LAYOUT =================
st.set_page_config(page_title="Dadar Land Management", layout="wide")
df = load_data()

# CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Dashboard - Dadar Land Management")
    if not df.empty:
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        total_income = df['Kafaltii_Taj'].sum()
        m1.metric("Waliigala Galii", f"{total_income:,.2f} ETB")
        m2.metric("Baay'ina Maamiltootaa", len(df))
        m3.metric("Ogeeyyii Hirmaatan", df['Maqaa_Ogeessa'].nunique())
        m4.metric("Araddaalee", df['Araddaa'].nunique())
        
        st.divider()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📈 Galii Gosa Tajaajilaan")
            # Grouping for chart
            chart_data = df.groupby('Gosa_Tajajjilaa')['Kafaltii_Taj'].sum().sort_values(ascending=False)
            st.bar_chart(chart_data)
            
        with c2:
            st.subheader("📍 Galii Araddaan")
            araddaa_data = df.groupby('Araddaa')['Kafaltii_Taj'].sum()
            st.write(araddaa_data)

        st.subheader("📋 Galmee dhihoo darbe")
        st.dataframe(df.tail(10), use_container_width=True)
    else: 
        st.info("Odeeffannoon agarsiifamu hin jiru. Maaloo dura galmeessi.")

# --- GALMEE HAARAA ---
elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa Haaraa")

    # DOWNLOAD BUTTON (Gubbaatti yoo qophaa'e)
    if st.session_state.pdf_to_download:
        st.success("📄 WARAQAAN RAGAA (CLEARANCE) QOPHAA'EERA!")
        st.download_button(
            label="📥 AS CUQAASII IRRA BUUFADHU (PDF)",
            data=st.session_state.pdf_to_download,
            file_name=st.session_state.pdf_name,
            mime="application/pdf"
        )
        if st.button("Linkii Download Balleessi"):
            st.session_state.pdf_to_download = None
            st.rerun()
        st.divider()

    GATII_DICT = {
        "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
        "🏷️ Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii"],
        "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Jijjiirraa Maqaa"]
    }
    
    selected_cats = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
    details, d_fees = [], {}
    
    for cat in selected_cats:
        with st.expander(f"Kaffaltii {cat}", expanded=True):
            subs = st.multiselect(f"Tajaajiloota {cat}:", GATII_DICT[cat], key=cat)
            for s in subs:
                details.append(s)
                d_fees[s] = st.number_input(f"Kaffaltii {s}", min_value=0.0, key=f"f_{s}")

    with st.form("main_form", clear_on_submit=True):
        st.subheader("Odeeffannoo Maamilaa")
        c1, c2 = st.columns(2)
        m_maqaa = c1.text_input("Maqaa Maamilaa *")
        m_araddaa = c2.text_input("Araddaa *")
        m_qaxana = c1.text_input("Qaxana")
        m_nagahee_lakk = c2.text_input("Lakk. Nagahee *")
        m_ogeessa = c1.text_input("Ogeessa Raawwate *")
        
        submit = st.form_submit_button("💾 GALMEESSI FI KUUSI")
        
        if submit:
            if m_maqaa and m_araddaa and details:
                total_f = sum(d_fees.values())
                new_row = [datetime.now().strftime('%d/%m/%Y'), m_maqaa, m_araddaa, m_qaxana, ", ".join(details), m_ogeessa, total_f]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                
                if "Waraqaa Ragaa (Clearance)" in details:
                    st.session_state.pdf_to_download = create_clearance_pdf(m_maqaa, m_araddaa, m_qaxana, ", ".join(details), m_nagahee_lakk)
                    st.session_state.pdf_name = f"Clearance_{m_maqaa}.pdf"
                
                st.success(f"✅ Galmeen {m_maqaa} milkaa'eera!")
                st.rerun()
            else:
                st.error("⚠️ Maaloo odeeffannoo guutuu galchi!")

# --- BADHAASA ---
elif menu == "🏆 Badhaasa":
    st.header("🏆 Sadarkaa Ogeeyyii")
    if not df.empty:
        top = df['Maqaa_Ogeessa'].value_counts().reset_index()
        top.columns = ['Maqaa Ogeessaa', 'Baay\'ina Tajaajilaa']
        st.table(top)
    else: st.info("Hojiin galmaa'e hin jiru.")

# --- GABAASA ---
elif menu == "📈 Gabaasa":
    st.header("📈 Gabaasa Waliigalaa")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Gabaasa CSV Buufadhu", data=csv, file_name="Gabaasa_Dadar.csv", mime="text/csv")
    else: st.info("Galmeen agarsiifamu hin jiru.")

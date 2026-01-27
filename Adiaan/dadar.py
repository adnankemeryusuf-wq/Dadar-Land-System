import streamlit as st
import pandas as pd
import os
import io
import plotly.express as px
from datetime import datetime
from fpdf import FPDF

# ================= 1. UI SETUP =================
st.set_page_config(page_title="Dadar Land Admin Final", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    [data-testid="stSidebar"] { background: #0b2b1a !important; }
    .main-header { color: #1b5e20; text-align: center; padding: 20px; font-size: 30px; font-weight: bold; border-bottom: 2px solid #b8860b; }
    .card-stat {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 5px solid #b8860b;
        text-align: center;
    }
    .stButton>button { background: #1b5e20; color: white; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA ENGINE =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Ref_No', 'Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Waajjira Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, "Nagahee Kaffaltii Tajaajilaa", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    labels = ["Lakk_Eenyummaa (Ref):", "Guyyaa:", "Maqaa Maamilaa:", "Araddaa:", "Gosa Tajaajilaa:", "Ogeessa:", "Waliigala Kaffaltii:"]
    for label, value in zip(labels, data):
        pdf.cell(50, 10, label)
        pdf.set_font("Arial", '')
        pdf.cell(100, 10, str(value), ln=True)
        pdf.set_font("Arial", 'B')
    pdf.ln(20)
    pdf.cell(200, 10, "Mallattoo fi Mohora Waajjiraa", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. SYSTEM LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#1b5e20;'>🏢 Deder Land Login</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u, p = st.text_input("Username"), st.text_input("Password", type="password")
            if st.form_submit_button("LOG IN"):
                if u == "admin" and p == "123":
                    st.session_state.logged_in, st.session_state.user = True, u
                    st.rerun()
                else: st.error("Maaloo sirriitti galchi!")
else:
    df = load_data()
    with st.sidebar:
        st.title("Deder Land Admin")
        st.write(f"👤 User: {st.session_state.user}")
        menu = st.radio("MENU", ["📊 Analytics", "📝 Galmee Haaraa", "📂 Gabaasa & Backup", "🔍 Search & Filter", "🚪 Ba'i"])

    if menu == "📊 Analytics":
        st.markdown("<div class='main-header'>📊 Dashboard & Analytics</div>", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='card-stat'>💰 Galii Waliigalaa<br><b>{df['Kafaltii_Taj'].sum():,.2f} ETB</b></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card-stat'>👥 Maamiltoota<br><b>{len(df)}</b></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card-stat'>👷 Ogeeyyii<br><b>{df['Maqaa_Ogeessa'].nunique()}</b></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='card-stat'>📍 Araddaa<br><b>{df['Araddaa'].nunique()}</b></div>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.plotly_chart(px.pie(df, names='Gosa_Tajajjilaa', title="Gosa Tajaajilaa"), use_container_width=True)
            with col_b:
                st.plotly_chart(px.bar(df.groupby('Maqaa_Ogeessa').size().reset_index(name='Count'), x='Maqaa_Ogeessa', y='Count', title="Hojii Ogeeyyii"), use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {
            "Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Liizii Waggaa", "TOT"],
            "Kaartaa & Ragaa": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Jijjiirraa Maqaa", "Sirreeffama Daangaa"],
            "Ijaarsa & Seera": ["Hayyama Ijaarsaa", "Ugura Kaasuu", "Waliigaltee Liqii", "Adabbii"]
        }
        
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            maqaa, araddaa = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")
            ogeessa = c1.text_input("Maqaa Ogeessaa")
            sel_cat = st.multiselect("Ramaddii Tajaajilaa", list(GATII_DICT.keys()))
            final_services, total_pay = [], 0
            
            if sel_cat:
                for cat in sel_cat:
                    subs = st.multiselect(f"Tajaajiloota {cat}", GATII_DICT[cat])
                    for s in subs:
                        final_services.append(s)
                        total_pay += st.number_input(f"Kaffaltii {s}", min_value=0.0)
            
            if st.form_submit_button("GALMEESSI"):
                if maqaa and final_services:
                    ref = f"DL-{datetime.now().strftime('%H%M%S')}"
                    new_row = [ref, datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, ", ".join(final_services), ogeessa, total_pay]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"Maamilli {maqaa} galmeeffameera!")
                    pdf_data = generate_pdf(new_row)
                    st.download_button("📥 Nagahee PDF Buufadhu", pdf_data, f"Nagahee_{maqaa}.pdf", "application/pdf")
                    st.balloons()
                else: st.warning("Maaloo odeeffannoo guuti!")

    elif menu == "🔍 Search & Filter":
        st.header("🔍 Barbaadi fi Calali")
        c1, c2 = st.columns(2)
        search_n, search_o = c1.text_input("Maqaa Maamilaa"), c2.text_input("Maqaa Ogeessaa")
        filtered = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search_n, case=False, na=False) & df['Maqaa_Ogeessa'].str.contains(search_o, case=False, na=False)]
        st.table(filtered)

    elif menu == "📂 Gabaasa & Backup":
        st.header("📂 Gabaasa Galii Guutuu")
        st.dataframe(df, use_container_width=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
        st.download_button("📥 Excel Buufadhu", buf.getvalue(), "Dadar_Land_Report.xlsx")

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False
        st.rerun()

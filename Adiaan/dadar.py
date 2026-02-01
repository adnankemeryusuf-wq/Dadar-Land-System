import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: #f0f4f0; }
    [data-testid="stSidebar"] { background-color: #0e3020 !important; }
    .main-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-left: 8px solid #1b5e20;
    }
    .stat-val { color: #1b5e20; font-size: 28px; font-weight: bold; }
    .stButton>button {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white; border-radius: 12px; font-weight: bold; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_receipt_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A5')
    pdf.add_page()
    pdf.set_draw_color(27, 94, 32); pdf.rect(5, 5, 138, 200)
    pdf.set_y(15); pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "NAGAHEE TAJAAJILAA", ln=True, align='C')
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, "Waajjira Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 10)
    fields = [("Maqaa:", data[1]), ("Araddaa:", data[2]), ("Tajaajila:", data[4]), ("Ogeessa:", data[5]), ("Kaffaltii:", f"{data[6]:,.2f} ETB")]
    for label, val in fields:
        pdf.cell(30, 8, label); pdf.set_font('Arial', ''); pdf.cell(0, 8, str(val), ln=True); pdf.set_font('Arial', 'B')
    pdf.set_y(180); pdf.cell(0, 10, "Mallattoo fi To'annoo", border='T', align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
            else: st.error("Maaloo ragaa sirrii galchi!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🚪 Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Analytics")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='main-card'>Galii Waliigalaa<br><span class='stat-val'>{df['Kafaltii_Taj'].sum():,.2f} ETB</span></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='main-card'>Tajaajilamtoota<br><span class='stat-val'>{len(df)}</span></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='main-card'>Ogeeyyii<br><span class='stat-val'>{df['Maqaa_Ogeessa'].nunique()}</span></div>", unsafe_allow_html=True)
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Tajaajilaa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Jijjiirraa Maqaa"],
            "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Hayyama Ijaarsaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Dhimma Dhala (Inheritance)"],
            "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsaa", "Kaffaltii Seeressuu"]
        }
        
        sel_main = st.multiselect("🟢 Ramaddii Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if sel_main:
            for g in sel_main:
                st.write(f"**{g}**")
                subs = st.multiselect(f"Tajaajiloota {g}:", GATII_DICT[g], key=f"s_{g}")
                if subs:
                    sub_cols = st.columns(len(subs))
                    for idx, s in enumerate(subs):
                        with sub_cols[idx]:
                            fee = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"v_{idx}_{s}")
                            details.append(s)
                            d_fees[f"{idx}_{s}"] = fee
                            if "Jijjiirraa" in s or "TOT" in s: is_tot = True

        with st.form("main_form"):
            c1, c2 = st.columns(2)
            if is_tot:
                name_f = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
            else:
                name_f, ara_f = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")
            
            qax_f = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            
            total_sum = sum(d_fees.values())
            st.write(f"### Waliigala Kaffaltii: {total_sum:,.2f} ETB")
            
            if st.form_submit_button("💾 GALMEESSI"):
                if name_f and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name_f, ara_f, qax_f, ", ".join(details), ogeessa, total_sum]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                    receipt = create_receipt_pdf(new_row)
                    st.download_button("📥 Nagahee (PDF) Buufadhu", receipt, f"Nagahee_{name_f}.pdf", "application/pdf")
                else: st.warning("Maaloo odeeffannoo guuti!")

    elif menu == "📈 Gabaasa Galii":
        st.header("📈 Gabaasa Waliigalaa")
        st.dataframe(df, use_container_width=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
            df.to_excel(wr, index=False)
        st.download_button("📥 Excel Buufadhu", buf.getvalue(), "Gabaasa_Dadar.xlsx")

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False; st.rerun()

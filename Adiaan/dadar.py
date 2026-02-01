import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import xlsxwriter

# ================= 1. CONFIGURATION & STYLE =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
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
    div[data-testid="stExpander"] { border: 1px solid #1b5e20; border-radius: 10px; background: white; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map({9:"Fulbaana", 10:"Onkololeessa", 11:"Sadaasa", 12:"Muddee", 1:"Amajjii", 2:"Guraandhala", 3:"Bitootessa", 4:"Eebila", 5:"Caamsaa", 6:"Waxabajjii", 7:"Adooleessa", 8:"Hagayya"})
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF GENERATORS (CERT & RECEIPT) =================
def create_receipt_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A5')
    pdf.add_page()
    pdf.set_draw_color(27, 94, 32); pdf.rect(5, 5, 138, 200)
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 10, 10, 20)
    pdf.set_y(15); pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "NAGAHEE TAJAAJILAA", ln=True, align='C')
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, "Waajjira Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 10)
    fields = [("Maqaa:", data[1]), ("Araddaa:", data[2]), ("Tajaajila:", data[4]), ("Ogeessa:", data[5]), ("Kaffaltii:", f"{data[6]:,.2f} ETB")]
    for label, val in fields:
        pdf.cell(30, 8, label); pdf.set_font('Arial', ''); pdf.cell(0, 8, str(val), ln=True); pdf.set_font('Arial', 'B')
    pdf.set_y(180); pdf.cell(0, 10, "Mallattoo fi To'annoo", border='T', align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container():
            if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
            st.title("Dadar Land Admin")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("SEENI"):
                if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🏆 Beekamtii Ogeeyyii", "🔍 Barbaadi/Edit", "🚪 Ba'i"])

    if menu == "📊 Dashboard":
        st.markdown("## 📊 Dashboard Analysis")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='main-card'>Total Galii<br><span class='stat-val'>{df['Kafaltii_Taj'].sum():,.2f} ETB</span></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='main-card'>Maamiltoota<br><span class='stat-val'>{len(df)}</span></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='main-card'>Ogeeyyii<br><span class='stat-val'>{df['Maqaa_Ogeessa'].nunique()}</span></div>", unsafe_allow_html=True)
            
            st.subheader("📈 Galii Ji'aan")
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Tajaajilaa":
        st.markdown("## 📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Jijjiirraa Maqaa (Gift/Sale)"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa", "Kaartaa Haaromsuu", "Kaartaa Lafa Qonnaa"],
            "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa", "Hayyama Ijaarsaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
            "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Xalayaa Deeggarsaa"],
            "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", "Adabbii Faallaa Pilaanii"]
        }
        
        sel_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if sel_main:
            for g in sel_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"s_{g}")
                for s in subs:
                    details.append(f"{g}-{s}")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"v_{g}_{s}")
                    if "TOT" in s or "Jijjiirraa" in s: is_tot = True

        with st.form("main_form"):
            c1, c2 = st.columns(2)
            if is_tot:
                maqaa_f = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
                qax_f = f"G: {c1.text_input('Qaxana G')} / B: {c2.text_input('Qaxana B')}"
            else:
                maqaa_f, ara_f = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")
                qax_f = c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 GALMEESSI FI NAGAHEE UUMI"):
                if maqaa_f and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!")
                    receipt = create_receipt_pdf(new_row)
                    st.download_button("📥 Nagahee (PDF) Buufadhu", receipt, f"Nagahee_{maqaa_f}.pdf", "application/pdf")
                else: st.warning("Odeeffannoo guuti!")

    elif menu == "📈 Gabaasa Galii":
        st.header("📈 Gabaasa Galii & Hojii")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df[COL_NAMES].to_excel(wr, index=False)
            st.download_button("📥 Gabaasa Excel Buufadhu", buf.getvalue(), "Gabaasa_Dadar.xlsx")
        else: st.info("Data'n hin jiru.")

    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Maamilaa...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    u_name = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"e_{idx}")
                    if st.button("💾 Update", key=f"b_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = u_name
                        save_data(df); st.rerun()

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False; st.rerun()

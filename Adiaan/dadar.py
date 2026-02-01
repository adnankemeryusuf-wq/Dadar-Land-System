import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF

# ================= 1. PREMIUM STYLE & COLORS =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

# Custom CSS for Luxury Look
st.markdown("""
    <style>
    /* Background and Font */
    .stApp { background-color: #f4f7f6; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #062c1a !important;
        border-right: 2px solid #d4af37;
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Custom Cards for Dashboard */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-top: 5px solid #0b6623;
        text-align: center;
    }
    .metric-val { color: #0b6623; font-size: 30px; font-weight: bold; }
    .metric-label { color: #555; font-size: 14px; font-weight: 500; }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #0b6623 0%, #14522d 100%);
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #d4af37 !important;
        color: #062c1a !important;
        transform: translateY(-2px);
    }
    
    /* Form Background */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
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
    pdf.set_draw_color(11, 102, 35)
    pdf.rect(5, 5, 138, 200)
    pdf.set_y(15); pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "NAGAHEE TAJAAJILAA", ln=True, align='C')
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, "Waajjira Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 10)
    fields = [("Maqaa:", data[1]), ("Araddaa:", data[2]), ("Tajaajila:", data[4]), ("Ogeessa:", data[5]), ("Kaffaltii:", f"{data[6]:,.2f} ETB")]
    for label, val in fields:
        pdf.cell(30, 8, label); pdf.set_font('Arial', ''); pdf.cell(0, 8, str(val), ln=True); pdf.set_font('Arial', 'B')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #0b6623;'>🏢 DADAR LAND</h1>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN SYSTEM", use_container_width=True):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("### 🛠 Navigation")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🚪 Ba'i"])

    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #0b6623;'>📊 Analytics Overview</h2>", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Galii Waliigalaa</div><div class='metric-val'>{df['Kafaltii_Taj'].sum():,.2f}</div><p>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Maamiltoota</div><div class='metric-val'>{len(df)}</div><p>Customers</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Ogeeyyii</div><div class='metric-val'>{df['Maqaa_Ogeessa'].nunique()}</div><p>Staff</p></div>", unsafe_allow_html=True)
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Tajaajilaa":
        st.markdown("<h2 style='color: #0b6623;'>📝 Galmee Haaraa</h2>", unsafe_allow_html=True)
        GATII_DICT ={
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
}
        
        sel_main = st.multiselect("🟢 Ramaddii Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if sel_main:
            for g in sel_main:
                st.markdown(f"**🔹 {g}**")
                subs = st.multiselect(f"Filadhu ({g}):", GATII_DICT[g], key=f"s_{g}")
                if subs:
                    sub_cols = st.columns(len(subs))
                    for idx, s in enumerate(subs):
                        with sub_cols[idx]:
                            fee = st.number_input(f"Gatii {s}", min_value=0.0, key=f"v_{idx}_{s}")
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
            st.markdown(f"### 💰 Waliigala: <span style='color:#0b6623;'>{total_sum:,.2f} ETB</span>", unsafe_allow_html=True)
            
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
        st.markdown("<h2 style='color: #0b6623;'>📈 Gabaasa Waliigalaa</h2>", unsafe_allow_html=True)
        st.dataframe(df.style.highlight_max(axis=0, color='#d1e7dd'), use_container_width=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
            df.to_excel(wr, index=False)
        st.download_button("📥 Excel Download", buf.getvalue(), "Gabaasa_Dadar.xlsx")

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False; st.rerun()


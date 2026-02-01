import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime, timedelta
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
# Telegram Bot Info (Asirratti kan kee sirriitti galchi)
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

MONTH_ORDER = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

st.markdown("""
    <style>
    div[data-testid="stSidebarUserContent"] .stRadio label {
        background-color: #10b981 !important;
        color: #000000 !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 15px 25px !important;
        margin-bottom: 10px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(12, 173, 120, 0.4) !important;
        display: block;
        cursor: pointer;
    }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-left: 5px solid #10b981; }
    .metric-value { font-size: 2rem; font-weight: 900; color: #10b981; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT & TELEGRAM =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    df['Date_Temp'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Ji\'a'] = df['Date_Temp'].dt.month_name()
    df['Kurmaana'] = df['Date_Temp'].dt.quarter.map({1: "Q1 (Jan-Mar)", 2: "Q2 (Apr-Jun)", 3: "Q3 (Jul-Sep)", 4: "Q4 (Oct-Dec)"})
    return df

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

def send_telegram_report(file_bytes, filename):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (filename, file_bytes)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': f"📊 Gabaasa Galii Dadar\n📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}"}
    try:
        response = requests.post(url, data=data, files=files)
        return response.json()
    except Exception as e:
        return str(e)

def create_receipt_pdf(data_row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Wajjira Lafaa Bul/Magaalaa Dadar", ln=True, align='C')
    pdf.set_font("Arial", size=11)
    pdf.ln(10)
    for i in range(len(COL_NAMES)):
        pdf.cell(200, 10, txt=f"{COL_NAMES[i].replace('_', ' ')}: {data_row[i]}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        with st.form("login_form"):
            st.markdown("<h2 style='text-align: center;'>Admin Login</h2>", unsafe_allow_html=True)
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI", use_container_width=True):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Ragaan galchaa sirrii miti!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("<h3 style='text-align:center;'>Wajjira Lafaa Bul/Magaalaa Dadar</h3>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("Filannoo", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🚪 Logout"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        h_c1, h_c2 = st.columns([0.1, 0.9])
        with h_c1: 
            if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=70)
        with h_c2: st.title("Dashboard Waliigalaa")
        
        if not df.empty:
            f1, f2, f3 = st.columns(3)
            with f1: period = st.selectbox("Yeroon Calali:", ["Hunda", "Torban Darbe", "Ji'aan", "Kurmaanaan"])
            
            display_df = df.copy()
            if period == "Torban Darbe":
                display_df = display_df[display_df['Date_Temp'] >= (datetime.now() - timedelta(days=7))]
            elif period == "Ji'aan":
                with f2:
                    sel_m = st.multiselect("Ji'a Filadhu:", MONTH_ORDER)
                    if sel_m: display_df = display_df[display_df['Ji\'a'].isin(sel_m)]
            elif period == "Kurmaanaan":
                with f3:
                    sel_q = st.multiselect("Kurmaana Filadhu:", ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dec)"])
                    if sel_q: display_df = display_df[display_df['Kurmaana'].isin(sel_q)]

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{display_df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(display_df)}</p></div>", unsafe_allow_html=True)
            with c3: 
                top_og = display_df['Maqaa_Ogeessa'].mode()[0] if not display_df.empty else "-"
                st.markdown(f"<div class='card'><p>🏆 Ogeessa Filatamaa</p><p class='metric-value' style='font-size:1.4rem;'>{top_og}</p></div>", unsafe_allow_html=True)
        else: st.info("Datiin galmaa'e hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Tajaajilaa":
        h_c1, h_c2 = st.columns([0.1, 0.9])
        with h_c1:
            if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=65)
        with h_c2: st.markdown("<h2 style='margin-top:10px;'>Galmee Haaraa Galchi</h2>", unsafe_allow_html=True)
        
        GATII_DICT = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"],
            "🏗 Pilaanii & Ijaarsa": ["Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
            "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],
            "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"]
        }
        
        sel_main = st.multiselect("🟢 Ramaddii Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        if sel_main:
            for g in sel_main:
                subs = st.multiselect(f"Filadhu ({g}):", GATII_DICT[g], key=f"s_{g}")
                if subs:
                    sub_cols = st.columns(len(subs))
                    for idx, s in enumerate(subs):
                        with sub_cols[idx]:
                            fee = st.number_input(f"Gatii {s}", min_value=0.0, key=f"v_{idx}_{s}")
                            details.append(s)
                            d_fees[f"{idx}_{s}"] = fee
                            if any(x in s for x in ["Jijjiirraa", "TOT"]): is_tot = True

        with st.form("main_form"):
            c1, c2 = st.columns(2)
            if is_tot:
                name_f = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
            else:
                name_f, ara_f = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")
            qax_f, ogeessa = c1.text_input("Qaxana"), c2.text_input("Maqaa Ogeessaa")
            total_sum = sum(d_fees.values())
            st.markdown(f"### 💰 Waliigala Kaffaltii: {total_sum:,.2f} ETB")
            if st.form_submit_button("💾 GALMEESSI"):
                if name_f and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y %H:%M'), name_f, ara_f, qax_f, ", ".join(details), ogeessa, total_sum]
                    df = load_data()
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                    receipt = create_receipt_pdf(new_row)
                    st.download_button("📥 Nagahee Buufadhu", receipt, f"Nagahee_{name_f}.pdf", "application/pdf")
                else: st.warning("Maaloo odeeffannoo guuti!")

    # --- SEARCH & REPORT ---
    elif menu == "📈 Gabaasa Galii":
        h_c1, h_c2 = st.columns([0.1, 0.9])
        with h_c1:
            if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=65)
        with h_c2: st.markdown("<h2 style='margin-top:10px;'>Gabaasa & Telegram Send</h2>", unsafe_allow_html=True)
        
        search_query = st.text_input("🔍 Barbaadi (Maqaa, Araddaa...):")
        if not df.empty:
            mask = df[COL_NAMES].apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            f_df = df[mask].copy()
            f_df.insert(0, 'No.', range(1, 1 + len(f_df))) # Lakkofsa (No.) dabalame
            
            st.dataframe(f_df, use_container_width=True)

            # Excel bifa bareedaan qopheessuu
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                f_df.to_excel(wr, index=False, sheet_name='Gabaasa')
                workbook, worksheet = wr.book, wr.sheets['Gabaasa']
                header_fmt = workbook.add_format({'bold': True, 'bg_color': '#10b981', 'border': 1, 'font_color': 'white'})
                for col_num, value in enumerate(f_df.columns.values):
                    worksheet.write(0, col_num, value, header_fmt)
            
            excel_out = buf.getvalue()
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel Buufadhu", excel_out, "Gabaasa_Dadar.xlsx")
            if c2.button("✈️ Gabaasa Telegram-itti Ergi"):
                with st.spinner("Ergamaa jira..."):
                    res = send_telegram_report(excel_out, "Gabaasa_Dadar_Final.xlsx")
                    if isinstance(res, dict) and res.get("ok"): st.success("✅ Gabaasni ergameera!")
                    else: st.error("❌ Erguun hin danda'amne!")
        else: st.info("Datiin hin jiru.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

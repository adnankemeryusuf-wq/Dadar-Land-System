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

# Order of months for the chart
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
    div[data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: #34d399 !important;
        transform: scale(1.02);
    }
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #10b981;
    }
    .metric-label { font-size: 1.1rem; color: #666; font-weight: bold; }
    .metric-val { font-size: 2rem; color: #10b981; font-weight: 900; }
    
    /* Card for Dashboard metrics */
    .card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1b5e20;
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
    
    # Dashboard-iif guyyaa irraa ji'a baasuuf
    try:
        df['Date_Temp'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y %H:%M', errors='coerce')
        df['Ji\'a'] = df['Date_Temp'].dt.month_name()
    except:
        df['Ji\'a'] = "Unknown"
        
    return df

def save_data(df):
    # Data save gochuu dura column dabalataa Dashboard-iif itti daballe hir'isna
    final_df = df[COL_NAMES]
    final_df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

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
        st.markdown("<br><br>", unsafe_allow_html=True)
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
        st.markdown("<h2 style='color: #1b5e20;'>📊 Dashboard Waliigalaa</h2>", unsafe_allow_html=True)
        if not df.empty:
            # Calallii Dashboard irratti
            sel_month = st.multiselect("Ji'aan Calali (Filter by Month):", options=MONTH_ORDER)
            
            display_df = df.copy()
            if sel_month:
                display_df = display_df[display_df['Ji\'a'].isin(sel_month)]

            c1, c2, c3 = st.columns(3)
            with c1:
                rev = float(display_df['Kafaltii_Taj'].sum())
                st.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{rev:,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(display_df)}</p></div>", unsafe_allow_html=True)
            with c3:
                top_og = display_df['Maqaa_Ogeessa'].mode()[0] if not display_df['Maqaa_Ogeessa'].empty else "-"
                st.markdown(f"<div class='card'><p>🏆 Ogeessa Filatamaa</p><p class='metric-value'>{top_og}</p></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("📈 Trendii Galii Ji'aan")
            trend_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.area_chart(trend_data)
        else:
            st.info("Data'n galmeeffame hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Tajaajilaa":
        st.markdown("<h2 style='color: #1a2a29;'>📝 Galmee Haaraa Galchi</h2>", unsafe_allow_html=True)
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
                st.markdown(f"🔹 {g}")
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
            qax_f, ogeessa = c1.text_input("Qaxana"), c2.text_input("Maqaa Ogeessaa")
            total_sum = sum(d_fees.values())
            st.markdown(f"### 💰 Waliigala Kaffaltii: <span style='color:#00a86b;'>{total_sum:,.2f} ETB</span>", unsafe_allow_html=True)
            if st.form_submit_button("💾 GALMEESSI FI NAGAHEE UUMI"):
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
        head_col1, head_col2 = st.columns([0.1, 0.9])
        with head_col1:
            if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=65)
        with head_col2:
            st.markdown("<h2 style='margin-top: 10px;'>Barbaadi (Search) & Gabaasa</h2>", unsafe_allow_html=True)
        
        search_query = st.text_input("🔍 Maqaa, Araddaa ykn Gosa Tajaajilaa galchi...", placeholder="Fakkeenya: Kaartaa...")
        
        if not df.empty:
            if search_query:
                mask = df[COL_NAMES].apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
                filtered_df = df[mask]
            else:
                filtered_df = df
            
            st.dataframe(filtered_df[COL_NAMES].style.highlight_max(axis=0, color='#d1e7dd'), use_container_width=True)
            st.write(f"Maamiltoota {len(filtered_df)} argamaniiru.")
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                filtered_df[COL_NAMES].to_excel(wr, index=False)
            st.download_button("📥 Gabaasa kana (Excel) Buufadhu", buf.getvalue(), "Gabaasa_Dadar_Filtered.xlsx")
        else:
            st.info("Datiin gabaasaaf dhiyaatu hin jiru.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

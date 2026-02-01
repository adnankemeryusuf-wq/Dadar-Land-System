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

# CSS for better UI
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
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #10b981;
        margin-bottom: 10px;
    }
    .metric-label { font-size: 1.1rem; color: #666; font-weight: bold; }
    .metric-val { font-size: 2rem; color: #10b981; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    # Guyyaa irraa Ji'a baasuuf
    df['Date_Converted'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Ji\'a'] = df['Date_Converted'].dt.month_name()
    return df

def save_data(df):
    # Save gochuun dura column dabalataa ('Ji'a' fi 'Date_Converted') hir'isuu qabna
    temp_df = df[COL_NAMES]
    temp_df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding='utf-8')

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
        st.markdown("<h3 style='text-align:center;'>Dadar Land Admin</h3>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("Filannoo", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🚪 Logout"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #1b5e20;'>📊 Dashboard Waliigalaa</h2>", unsafe_allow_html=True)
        
        if not df.empty:
            # Calallii Dashboard irratti
            c_filter1, c_filter2 = st.columns(2)
            with c_filter1:
                sel_month = st.multiselect("Ji'aan Calali", options=MONTH_ORDER)
            
            display_df = df.copy()
            if sel_month:
                display_df = display_df[display_df['Ji\'a'].isin(sel_month)]

            c1, c2, c3 = st.columns(3)
            with c1:
                total_rev = display_df['Kafaltii_Taj'].sum()
                st.markdown(f"<div class='metric-card'><div class='metric-label'>💰 Galii Waliigalaa</div><div class='metric-val'>{total_rev:,.2f}</div><p>ETB</p></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>👥 Maamiltoota</div><div class='metric-val'>{len(display_df)}</div><p>Total</p></div>", unsafe_allow_html=True)
            with c3:
                top_staff = display_df['Maqaa_Ogeessa'].mode()[0] if not display_df.empty else "-"
                st.markdown(f"<div class='metric-card'><div class='metric-label'>🏆 Ogeessa Filatamaa</div><div class='metric-val' style='font-size:1.5rem;'>{top_staff}</div></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("📈 Trendii Galii Ji'aan")
            trend = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.area_chart(trend)
        else:
            st.info("Hanga ammaatti data'n galmaa'e hin jiru.")

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
                    df = load_data() # Refresh before save
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                    receipt = create_receipt_pdf(new_row)
                    st.download_button("📥 Nagahee Buufadhu", receipt, f"Nagahee_{name_f}.pdf", "application/pdf")
                else: st.warning("Maaloo odeeffannoo guuti!")

    # --- REPORT ---
    elif menu == "📈 Gabaasa Galii":
        st.header("📈 Barbaadi & Gabaasa")
        search_query = st.text_input("🔍 Maqaa, Araddaa ykn Gosa Tajaajilaa...")
        if not df.empty:
            mask = df[COL_NAMES].apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            filtered_df = df[mask][COL_NAMES]
            st.dataframe(filtered_df, use_container_width=True)
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                filtered_df.to_excel(wr, index=False)
            st.download_button("📥 Excel Buufadhu", buf.getvalue(), "Gabaasa.xlsx")
        else:
            st.info("Datiin hin jiru.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

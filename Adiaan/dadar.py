import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from ethiopian_date import EthiopianDateConverter

# ================= 1. CONFIGURATION & SETUP =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# Folder uumuuf
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Administration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

# Style bareedsuuf
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_clearance_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 15, "WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    body = f"Maqaa: {data['maqaa']}\nAraddaa: {data['araddaa']}\nLakk. Manaa: {data['mana']}\nLakk. Kaartaa: {data['kaartaa']}\n\nQabiyyeen kun dhorkaa irraa bilisa ta'uu ni mirkaneessina."
    pdf.multi_cell(0, 10, body)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP UI =================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    st.markdown("<h2 style='text-align:center;'>🏢 Dadar Land Administration Login</h2>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username ykn Password dogoggora!")

else:
    # --- MAIN SIDEBAR ---
    df = load_data()
    with st.sidebar:
        st.header("FILANNOO")
        menu = st.radio("Menu", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "📜 Clearance", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("📅 Ji'a Kana", len(df[df['Ji\'a'] == MONTH_MAP[datetime.now().month]]))
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    # --- 2. REGISTRATION (GALMEE) ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara"]
        }
        
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        d_fees = {}
        details = []
        is_tot = False

        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g])
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0)
                    if s == "TOT": is_tot = True

        with st.form("reg_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            if is_tot:
                maqaa = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                araddaa = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
            else:
                maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
                araddaa = c2.text_input("Araddaa")
            
            qaxana = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                    st.rerun()

   # ================= 3. PDF GENERATOR (FIXED) =================
def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    # Border and BG
    pdf.set_fill_color(245, 255, 245); pdf.rect(12, 12, 273, 186, 'F')
    pdf.set_line_width(4); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)

    # Logos - Using getvalue() for reliability
    if logo_left:
        with open("temp_logo_l.png", "wb") as f: f.write(logo_left.getvalue())
        pdf.image("temp_logo_l.png", x=20, y=15, w=35)
    if logo_right:
        with open("temp_logo_r.png", "wb") as f: f.write(logo_right.getvalue())
        pdf.image("temp_logo_r.png", x=240, y=15, w=35)

    pdf.set_y(45); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 25, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_text_color(30, 70, 30); pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(15); pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    
    pdf.ln(5); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 32)
    pdf.cell(0, 20, f"{name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_text_color(40, 40, 40); pdf.set_font('Arial', '', 15)
    msg = (f"Waggaa 2026 keessatti tajaajila saffisaa fi amannamaa ta'een\n"
           f"Abbootii Dhimmaa {count} tajaajiluun beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    
    pdf.ln(20); curr_y = pdf.get_y()
    pdf.line(40, curr_y, 110, curr_y); pdf.set_xy(40, curr_y + 2); pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
    pdf.line(180, curr_y, 250, curr_y); pdf.set_xy(180, curr_y + 2); pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
            else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    
    with st.sidebar:
        st.title("Dadar Admin")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h4>💰 Galii Waliigalaa</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Tajaajilamtoota</h4><h2>{len(df)}</h2><p>Walitti qabaa</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Hojii irra jiran</p></div>", unsafe_allow_html=True)
            st.divider()
            st.subheader("📈 Raawwii Galii Ji'aan")
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else:
            st.info("Data'n galmeeffame hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Haaromsuu"],
            "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
            "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
            "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
        }
        
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")
                    if s == "TOT": is_tot = True

        with st.form("entry_form", clear_on_submit=True):
            st.markdown("### 📋 Odeeffannoo Abbaa Dhimmaa")
            if is_tot:
                col1, col2 = st.columns(2)
                maqaa_f = f"G: {col1.text_input('Maqaa Gurguraa')} / B: {col2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {col1.text_input('Araddaa G')} / B: {col2.text_input('Araddaa B')}"
                qax_f = f"G: {col1.text_input('Qaxana G')} / B: {col2.text_input('Qaxana B')}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f = c1.text_input("Maqaa Abbaa Dhimmaa")
                ara_f = c2.text_input("Araddaa")
                qax_f = c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                else: st.error("⚠️ Odeeffannoo guuti!")

    # --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Bal'aa")
        if not df.empty:
            f_type = st.sidebar.radio("Calali:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa Murtaa'aa"])
            filtered = df.copy()
            if f_type == "Guyyaa Murtaa'aa":
                sel_date = st.sidebar.date_input("Guyyaa:", datetime.now())
                filtered = df[df['Guyyaa'] == sel_date.strftime('%d/%m/%Y')]
            else:
                sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
                filtered = filtered[filtered['Waggaa'] == sel_y]
                if f_type == "Kurmaana":
                    filtered = filtered[filtered['Kurmaana'] == st.sidebar.selectbox("Kurmaana", [1,2,3,4])]
                elif f_type == "Ji'a":
                    filtered = filtered[filtered['Ji\'a'] == st.sidebar.selectbox("Ji'a", MONTH_ORDER)]
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            total = filtered['Kafaltii_Taj'].sum()
            st.metric("Galii", f"{total:,.2f} ETB")
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel", buf.getvalue(), "Gabaasa.xlsx")
            if c2.button("✈️ Telegram"):
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa Galii: {total} ETB"): st.success("✅ Ergame!")
        else: st.warning("Data'n hin jiru.")

    # --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa & Sartiifiikeeta")
        cl, cr = st.columns(2)
        logo_l = cl.file_uploader("Logo Bitaa Filadhu", type=['png', 'jpg'], key="l_up")
        logo_r = cr.file_uploader("Logo Mirgaa Filadhu", type=['png', 'jpg'], key="r_up")
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h2 style='color:green;'>{i}FFAA</h2><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    try:
                        # Passing uploaded files directly
                        pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                        st.download_button(f"📥 PDF {i}ffaa", pdf_bytes, f"Cert_{name}.pdf", "application/pdf", key=f"btn_{i}")
                    except Exception as e: 
                        st.error(f"PDF Error: {e}")
        else: st.info("Data'n hin jiru.")

    # --- SEARCH/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not results.empty:
                for idx, row in results.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                        new_name = st.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                        new_fee = st.number_input("Kafaltii Sirreessi", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                        c1, c2 = st.columns(2)
                        if c1.button("💾 Update", key=f"u_{idx}"):
                            df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_name
                            df.at[idx, 'Kafaltii_Taj'] = new_fee
                            save_data(df); st.success("Sirreeffameera!"); st.rerun()
                        if c2.button("🗑 Haqi", key=f"d_{idx}"):
                            df = df.drop(idx); save_data(df); st.warning("Haqumeera!"); st.rerun()
            else: st.error("Maqaan kun hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURATION TELEGRAM ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try: return requests.post(url, files=files, data=data).status_code == 200
    except: return False

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



import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from ethiopian_date import EthiopianDateConverter


# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Administration", 
    page_icon="🏢", 
    layout="wide"
)

# CSS Styling
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. SERVICE STRUCTURE =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Kaartaa Lafa Qoonnaa"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa",
        "Kaffaltii Seeressuu (Regularization)",
        "Adabbii Faallaa Pilaanii"
    ],
}

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 4. LOGIN SYSTEM =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Maqaa ykn Koodiin dogoggora!")

# ================= 5. MAIN APP =================
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa"])

    # ================= REGISTRATION =================
    if menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")

        # Service selection
        selected_cats = st.multiselect("🟢 Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        final_services = []
        fees_dict = {}

        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    st.write(f"📂 {cat}")
                    subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat], key=f"sub_{cat}")
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s} (ETB):", min_value=0.0, key=f"fee_{s}")
                        final_services.append(s)
                        fees_dict[s] = fee

        total_fee = sum(fees_dict.values())
        st.markdown(f"**💰 Waliigala Kafaltii: {total_fee:.2f} ETB**")
        st.divider()
        st.subheader("📝 Odeeffannoo Maamilaa")

        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])

            if st.form_submit_button("💾 Galmeessi"):
                errors = []

                # VALIDATION
                if not name.strip(): errors.append("❌ Maqaa dirqamaa guutuu galchi!")
                if not final_services: errors.append("❌ Maaloo tajaajila tokko filadhu!")
                if qax and (not qax.isdigit() or int(qax) < 1): errors.append("❌ Qaxana lakkoofsa sirrii galchi (1-1000)")
                if total_fee < 0: errors.append("❌ Kafaltii sirrii galchi (≥ 0)")
                if nagahee and nagahee.size > 5*1024*1024: errors.append("❌ Fayilii Nagahee ol-kaayame (max 5MB)")

                if errors:
                    for e in errors: st.error(e)
                else:
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())

                    new_row = [
                        datetime.now().strftime('%d/%m/%Y'),
                        name.strip(), ara.strip(), qax.strip(),
                        ", ".join(final_services), ogeessa.strip(), total_fee
                    ]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Waliigala: {total_fee:.2f} ETB")
                    st.balloons()

    # ================= DASHBOARD =================
    elif menu == "📊 Dashboard":
        st.header("📊 Dashboard")

        if not df.empty:
            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Maamiltootaa", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.divider()

            # Fees by Officer
            st.subheader("👷 Fees by Officer")
            fees_by_officer = df.groupby('Maqaa_Ogeessa')['Kafaltii_Taj'].sum().reset_index()
            fig_officer = px.bar(fees_by_officer, x='Maqaa_Ogeessa', y='Kafaltii_Taj',
                                 text='Kafaltii_Taj', color='Maqaa_Ogeessa', labels={'Kafaltii_Taj':'ETB'})
            st.plotly_chart(fig_officer, use_container_width=True)
            st.divider()

            # Fees by Service
            st.subheader("🏷 Fees by Service")
            df_services = df.assign(Service=df['Gosa_Tajajjilaa'].str.split(', ')).explode('Service')
            fees_by_service = df_services.groupby('Service')['Kafaltii_Taj'].sum().reset_index()
            fig_service = px.bar(fees_by_service, x='Service', y='Kafaltii_Taj',
                                 text='Kafaltii_Taj', color='Service')
            fig_service.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_service, use_container_width=True)
            st.divider()

            # Payment trend
            st.subheader("📈 Payment Trend")
            df['Guyyaa'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
            trend_fig = px.line(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa',
                                labels={'Kafaltii_Taj':'Fee (ETB)', 'Guyyaa':'Date'})
            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    # ================= BADHAASA =================
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        if not df.empty:
            top_officers = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_officers.items()):
                with cols[i]:
                    st.markdown(f"### {name}\n**Hojii: {count}**")
        else:
            st.info("Ragaan ogeeyyii hin jiru.")import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# ================= CONFIG =================
st.set_page_config(page_title="Dadar Land System", layout="wide")

DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID_MANAGER = "YOUR_CHAT_ID"

COL_NAMES = [
    'Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa',
    'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj'
]

# ================= SESSION =================
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

# ================= HELPERS =================
def get_ethiopian_date():
    now = datetime.now()
    ec = EthiopianDateConverter.to_ethiopian(now.year, now.month, now.day)
    return f"{ec.day:02d}/{ec.month:02d}/{ec.year}"

# ================= CLEARANCE PDF =================
def create_clearance_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)

    pdf.cell(0,10,"MOOTUMMAA NAANNOO OROMIYAA",ln=True,align="C")
    pdf.cell(0,10,"WAAJJIRA LAFAA - BULCHIINSA MAGAALAA DADAR",ln=True,align="C")
    pdf.ln(10)

    pdf.multi_cell(0,8,
        f"Waraqaan ragaa kun Obbo/Adde {data['maqaa']} "
        f"Araddaa {data['araddaa']} Qaxana {data['qaxana']} "
        f"Lakk. Kaartaa {data['kaartaa']} irratti kennama.\n\n"
        f"Bara Gibiraa: {data['bara']}\n"
        f"Dhimma: {data['dhimma']}\n\n"
        f"Itti Gaafatamaa: {data['head']}\n"
        f"Guyyaa: {get_ethiopian_date()}"
    )

    return pdf.output(dest="S").encode("latin-1")

# ================= DATA =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)

# ================= TELEGRAM =================
def send_excel_to_telegram(file_bytes, filename, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {"document": (filename, file_bytes)}
    data = {"chat_id": CHAT_ID_MANAGER, "caption": caption}
    requests.post(url, files=files, data=data)

# ================= EXCEL =================
def create_excel_report(df, mode):
    df['Date'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')

    if mode == "daily":
        df = df[df['Date'].dt.date == datetime.now().date()]
        fname = "Daily_Report.xlsx"
    else:
        df = df[
            (df['Date'].dt.month == datetime.now().month) &
            (df['Date'].dt.year == datetime.now().year)
        ]
        fname = "Monthly_Report.xlsx"

    if df.empty:
        return None

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df[COL_NAMES].to_excel(writer, index=False)
    out.seek(0)
    return out, fname

# ================= UI =================
st.title("🏛 Dadar Land Administration System")

tab1, tab2 = st.tabs(["📝 Clearance PDF", "📊 Reports"])

# -------- TAB 1 --------
with tab1:
    with st.form("clearance_form"):
        m1, m2 = st.columns(2)
        maqaa = m1.text_input("Maqaa Maamilaa *")
        araddaa = m2.text_input("Araddaa *")
        qaxana = m1.text_input("Qaxana *")
        kaartaa = m2.text_input("Lakk. Kaartaa *")
        bara = m1.text_input("Bara Gibiraa")
        dhimma = m2.selectbox("Dhimma", ["Gurgurtaa","Liqii","Kennaa"])
        head = st.text_input("Maqaa Itti Gaafatamaa *")

        if st.form_submit_button("📄 PDF UUMI"):
            if maqaa and kaartaa and head:
                st.session_state.pdf_bytes = create_clearance_pdf({
                    "maqaa": maqaa,
                    "araddaa": araddaa,
                    "qaxana": qaxana,
                    "kaartaa": kaartaa,
                    "bara": bara,
                    "dhimma": dhimma,
                    "head": head
                })
                st.session_state.pdf_name = f"Clearance_{maqaa}.pdf"
                st.success("PDF qophaa'eera")

    if st.session_state.pdf_bytes:
        st.download_button(
            "⬇️ PDF Buusi",
            st.session_state.pdf_bytes,
            file_name=st.session_state.pdf_name,
            mime="application/pdf"
        )

# -------- TAB 2 --------
with tab2:
    df = load_data()

    if st.button("📊 Daily Excel → Telegram"):
        res = create_excel_report(df,"daily")
        if res:
            send_excel_to_telegram(*res,"📊 Gabaasa Guyyaa")
            st.success("Ergameera")
        else:
            st.warning("Ragaan hin jiru")

    if st.button("📈 Monthly Excel → Telegram"):
        res = create_excel_report(df,"monthly")
        if res:
            send_excel_to_telegram(*res,"📈 Gabaasa Ji'aa")
            st.success("Ergameera")
        else:
            st.warning("Ragaan hin jiru")

    st.dataframe(df)



import streamlit as st
import pandas as pd
import sqlite3
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
import plotly.express as px

# ================= CONFIG =================
st.set_page_config("Dadar Land Admin", "🏢", layout="wide")
DB_FILE = "dadar_land.db"
NAGAHEE_DIR = "nagahee_scan"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii", "Gibira Qonnaa", "Kaffaltii Liizii Waggaa"],
    "📂 Tajaajila Biroo": ["Clearance PDF", "Deebii Iyyannoo"]
}

COL_NAMES = ['id','guyyaa','maqaa','araddaa','qaxana','gosa_taj','ogeessa','kafaltii','nagahee_path']

# ================= HELPERS =================
def get_ec_date(g=None):
    if g is None: g=datetime.now()
    ec = EthiopianDateConverter.to_ethiopian(g.year,g.month,g.day)
    return f"{ec.day:02d}/{ec.month:02d}/{ec.year}"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS galmee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guyyaa TEXT, maqaa TEXT, araddaa TEXT, qaxana TEXT,
            gosa_taj TEXT, ogeessa TEXT, kafaltii REAL, nagahee_path TEXT
        )
    """)
    conn.commit()
    return conn

def load_data():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM galmee", conn)
    conn.close()
    return df

def save_row(row):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO galmee
        (guyyaa, maqaa, araddaa, qaxana, gosa_taj, ogeessa, kafaltii, nagahee_path)
        VALUES (?,?,?,?,?,?,?,?)
    """, row)
    conn.commit(); conn.close()

def create_clearance_pdf(data):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Times", size=12)
    pdf.cell(0,10,"MOOTUMMAA NAANNOO OROMIYAA",ln=True,align="C")
    pdf.cell(0,10,"BULCHIINSA MAGAALAA DADAR - WAAJJIRA LAFAA",ln=True,align="C")
    pdf.ln(10)
    pdf.multi_cell(0,8,
        f"Maqaa: {data['maqaa']}\n"
        f"Araddaa: {data['araddaa']}  Qaxana: {data['qaxana']}\n"
        f"Dhimma: {data['dhimma']}\n"
        f"Itti Gaafatamaa: {data['head']}\n"
        f"Guyyaa: {get_ec_date()}"
    )
    return pdf.output(dest="S").encode("latin-1")

def create_excel_report(df, mode):
    df['Date'] = pd.to_datetime(df['guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['EC_Date'] = df['Date'].apply(get_ec_date)
    if mode=="daily":
        df=df[df['Date'].dt.date==datetime.now().date()]; fname="Daily_Report.xlsx"
    else:
        df=df[(df['Date'].dt.month==datetime.now().month)&(df['Date'].dt.year==datetime.now().year)]; fname="Monthly_Report.xlsx"
    if df.empty: return None
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer: df.to_excel(writer, index=False)
    out.seek(0); return out,fname

def send_excel_to_telegram(file_bytes, filename, caption):
    url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    requests.post(url, files={"document":(filename,file_bytes)}, data={"chat_id":CHAT_ID_MANAGER,"caption":caption})

# ================= SESSION =================
if 'logged' not in st.session_state: st.session_state.logged=False
if 'pdf_bytes' not in st.session_state: st.session_state.pdf_bytes=None
if 'pdf_name' not in st.session_state: st.session_state.pdf_name=""

# ================= LOGIN =================
if not st.session_state.logged:
    st.title("🔐 Login")
    u = st.text_input("Username"); p=st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u=="admin" and p=="2026": st.session_state.logged=True; st.rerun()
        elif u=="staff" and p=="2026": st.session_state.logged=True; st.session_state.staff=True; st.rerun()
        else: st.error("Dogoggora login")

# ================= MAIN =================
else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard","📝 Galmee Haaraa","📄 Clearance","📤 Telegram Report"])

    # ---------- DASHBOARD ----------
    if menu=="📊 Dashboard":
        st.header("📊 Dashboard")
        if df.empty: st.info("Ragaan hin jiru")
        else:
            c1,c2,c3=st.columns(3)
            c1.metric("💰 Galii",f"{df['kafaltii'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota",len(df))
            c3.metric("👷 Ogeeyyii",df['ogeessa'].nunique())
            fig=px.bar(df.groupby("ogeessa")['kafaltii'].sum().reset_index(),x="ogeessa",y="kafaltii")
            st.plotly_chart(fig,use_container_width=True)

    # ---------- GALMEE HAARAA ----------
    elif menu=="📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        with st.form("reg_form"):
            c1,c2=st.columns(2)
            maqaa=c1.text_input("Maqaa"); araddaa=c2.text_input("Araddaa")
            qaxana=c1.text_input("Qaxana"); ogeessa=c2.text_input("Ogeessa Raawwate")
            services=st.multiselect("Tajaajila", sum(SERVICE_STRUCTURE.values(),[]))
            kafaltii=st.number_input("Kafaltii (ETB)", min_value=0.0)
            nagahee=st.file_uploader("Nagahee Scan (JPG/PNG)",type=["jpg","png"])
            if st.form_submit_button("💾 Galmeessi"):
                path=""; 
                if nagahee: path=os.path.join(NAGAHEE_DIR,f"{maqaa}_{datetime.now().strftime('%H%M%S')}.jpg"); open(path,"wb").write(nagahee.getbuffer())
                save_row([datetime.now().strftime('%d/%m/%Y'),maqaa,araddaa,qaxana,",".join(services),ogeessa,kafaltii,path])
                st.success("✅ Galmeeffameera!"); st.balloons()

    # ---------- CLEARANCE ----------
    elif menu=="📄 Clearance":
        st.header("📄 Clearance PDF")
        with st.form("clr_form"):
            maqaa=st.text_input("Maqaa Maamilaa"); araddaa=st.text_input("Araddaa"); qaxana=st.text_input("Qaxana")
            dhimma=st.text_input("Dhimma"); head=st.text_input("Itti Gaafatamaa")
            if st.form_submit_button("PDF UUMI"):
                st.session_state.pdf_bytes=create_clearance_pdf({"maqaa":maqaa,"araddaa":araddaa,"qaxana":qaxana,"dhimma":dhimma,"head":head})
                st.session_state.pdf_name=f"Clearance_{maqaa}.pdf"
                st.success("PDF qophaa'eera")
        if st.session_state.pdf_bytes:
            st.download_button("⬇️ PDF Buusi", st.session_state.pdf_bytes, st.session_state.pdf_name, mime="application/pdf")

    # ---------- TELEGRAM ----------
    elif menu=="📤 Telegram Report":
        st.header("📤 Telegram Reports")
        if st.button("📊 Daily Excel → Telegram"):
            res=create_excel_report(df,"daily")
            if res: send_excel_to_telegram(*res,"Daily Report"); st.success("Ergameera")
            else: st.warning("Ragaan hin jiru")
        if st.button("📈 Monthly Excel → Telegram"):
            res=create_excel_report(df,"monthly")
            if res: send_excel_to_telegram(*res,"Monthly Report"); st.success("Ergameera")
            else: st.warning("Ragaan hin jiru")









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

# ================= 2. DATA & CONSTANTS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

# GOSA TAJAAJILAA & GATII (Hubachiisa: Gatii asitti sirreessi)
GATII_DICT = {
      "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"
    ]
}
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

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = rank_colors.get(rank, (27, 94, 32))
    pdf.set_fill_color(245, 255, 245); pdf.rect(12, 12, 273, 186, 'F')
    pdf.set_line_width(4); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)
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
    msg = f"Waggaa 2026 keessatti tajaajila saffisaa fi amannamaa ta'een\nAbbootii Dhimmaa {count} tajaajiluun beekamtii kanaan badhaafamaniiru."
    pdf.multi_cell(0, 10, msg, align='C')
    pdf.ln(20); curr_y = pdf.get_y()
    pdf.line(40, curr_y, 110, curr_y); pdf.set_xy(40, curr_y + 2); pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
    pdf.line(180, curr_y, 250, curr_y); pdf.set_xy(180, curr_y + 2); pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN LOGIC =================
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123": 
                st.session_state.logged_in = True
                st.rerun()
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
            c1.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Maamila</h4><h2>{len(df)}</h2><p>Walitti qabaa</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Hojii irra jiran</p></div>", unsafe_allow_html=True)
            st.divider()
            st.subheader("📈 Raawwii Galii Ji'aan")
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n galmeeffame hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        
        details, d_fees = [], {}
        is_tot = False
        
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
                with col1:
                    gurg_m = st.text_input("Maqaa Gurguraa")
                    gurg_a = st.text_input("Araddaa Gurguraa")
                    gurg_q = st.text_input("Qaxana Gurguraa")
                with col2:
                    bit_m = st.text_input("Maqaa Bitataa")
                    bit_a = st.text_input("Araddaa Bitataa")
                    bit_q = st.text_input("Qaxana Bitataa")
                maqaa_f, ara_f, qax_f = f"G: {gurg_m} / B: {bit_m}", f"G: {gurg_a} / B: {bit_a}", f"G: {gurg_q} / B: {bit_q}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f, ara_f, qax_f = c1.text_input("Maqaa Abbaa Dhimmaa"), c2.text_input("Araddaa"), c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success(f"✅ Galmeeffameera!"); st.balloons()
                else: st.error("⚠️ Odeeffannoo guutuu galchi!")

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
                sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True) if not df['Waggaa'].isnull().all() else [2026])
                filtered = filtered[filtered['Waggaa'] == sel_y]
                if f_type == "Kurmaana": filtered = filtered[filtered['Kurmaana'] == st.sidebar.selectbox("Kurmaana", [1,2,3,4])]
                elif f_type == "Ji'a": filtered = filtered[filtered['Ji\'a'] == st.sidebar.selectbox("Ji'a", MONTH_ORDER)]
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            total = filtered['Kafaltii_Taj'].sum()
            st.metric("Galii Waliigalaa", f"{total:,.2f} ETB")
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel Buufadhu", buf.getvalue(), "Gabaasa.xlsx")
            if c2.button("✈️ Telegram-itti Ergi"):
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa Galii: {total} ETB"): st.success("✅ Ergame!")
        else: st.warning("Data'n hin jiru.")

    # --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa & Sartiifiikeeta")
        cl, cr = st.columns(2)
        logo_l = cl.file_uploader("Logo Bitaa", type=['png', 'jpg'], key="l_up")
        logo_r = cr.file_uploader("Logo Mirgaa", type=['png', 'jpg'], key="r_up")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h2 style='color:green;'>{i}FFAA</h2><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                    st.download_button(f"📥 Sartiifiikeeta {i}", pdf_bytes, f"Cert_{name}.pdf", "application/pdf", key=f"btn_{i}")
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
                        new_name = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                        new_fee = st.number_input("Kafaltii", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                        if st.button("💾 Update", key=f"u_{idx}"):
                            df.at[idx, 'Maqaa_Abbaa_Dhimmaa'], df.at[idx, 'Kafaltii_Taj'] = new_name, new_fee
                            save_data(df); st.success("Sirreeffameera!"); st.rerun()
                        if st.button("🗑 Haqi", key=f"d_{idx}"):
                            df = df.drop(idx); save_data(df); st.warning("Haqumeera!"); st.rerun()
            else: st.error("Maqaan kun hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF
# Library kana 'pip install ethiopian-date' godhii fe'adhu
from ethiopian_date import EthiopianDateConverter

# ================= 1. SETUP =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide", page_icon="🏢")

if 'pdf_to_download' not in st.session_state:
    st.session_state.pdf_to_download = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

# ================= 2. FUNCTIONS =================

def get_ethiopian_date_str():
    """Guyyaa har'aa gara Itoophiyaatti jijjiiruuf"""
    now = datetime.now()
    # Tooftaa sirrii library ethiopian-date itti fayyadaman
    e_date = EthiopianDateConverter.to_ethiopian(now.year, now.month, now.day)
    return f"{e_date[2]:02d}/{e_date[1]:02d}/{e_date[0]}"

def create_clearance_pdf(data):
    # 'latin-1' bakka 'Arial' ykn 'Times' itti fayyadamnuuf 'FPDF' qofaan gahaa dha
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Double line)
    pdf.set_line_width(0.8); pdf.rect(10, 10, 190, 277)
    pdf.set_line_width(0.2); pdf.rect(12, 12, 186, 273)

    # Logos (Checking if they exist before drawing)
    if os.path.exists("logo_bitta.jpg"): 
        pdf.image("logo_bitta.jpg", 15, 18, 23)
    if os.path.exists("logo_mirga.jpg"): 
        pdf.image("logo_mirga.jpg", 172, 18, 23)

    # --- Header Section ---
    pdf.set_y(22)
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, "MOOTUMMAA NAANNOO OROMIYAA", ln=True, align='C')
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, "WAAJJIRA LAFAA", ln=True, align='C')
    pdf.cell(0, 8, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    
    # Header Underline
    pdf.ln(3); pdf.set_line_width(0.5); pdf.line(20, 50, 190, 50)

    # Date and Ref No
    pdf.ln(12); pdf.set_font('Arial', '', 12)
    guyyaa_ec = get_ethiopian_date_str()
    
    # Lakk Galmee (Year calculation in EC)
    now = datetime.now()
    e_year = EthiopianDateConverter.to_ethiopian(now.year, now.month, now.day)[0]

    pdf.set_x(20)
    pdf.write(5, "Lakk. Galmee: ")
    pdf.set_font('Arial', 'B', 12) 
    pdf.write(5, f"DAD/WL/{e_year}/____")
    
    pdf.set_font('Arial', '', 12)
    pdf.set_x(140)
    pdf.write(5, f"Guyyaa: {guyyaa_ec}")
    pdf.ln(18)

    # Subject
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "DHIMMA: WARAQAA RAGAA QULQULLINAA (CLEARANCE)", ln=True, align='C')
    pdf.ln(8)

    # Body
    pdf.set_font('Arial', '', 12)
    pdf.set_x(20)
    
    # Multi-cell or writing for better flow
    body_text = (
        f"Waraqaan ragaa kun Obbo/Adde/Dhaabbata {data['maqaa'].upper()} "
        f"Araddaa {data['araddaa']} Qaxana {data['qaxana']} keessatti mana/lafa Lakk. Kaartaa "
        f"{data['kaartaa']} qabaniif kan kennameedha.\n\n"
        f"Maamilli kun hanga guyyaa har'aatti tajaajiloota waajjira keenya irraa argachaa turaniif:\n\n"
    )
    pdf.set_x(20)
    pdf.multi_cell(170, 8, body_text)

    # Items
    pdf.set_x(20)
    pdf.write(8, "1. Kaffaltii Gibira waggaa hanga bara ")
    pdf.set_font('Arial', 'B', 12); pdf.write(8, f"{data['bara_gibiraa']} E.C"); pdf.set_font('Arial', '', 12)
    pdf.write(8, " guutummaatti kaffalaniiru.\n")

    pdf.set_x(20)
    if data.get('gosa_qabiyyee') == "Liizii":
        pdf.write(8, "2. Kaffaltii ")
        pdf.set_font('Arial', 'B', 12); pdf.write(8, "Liizii"); pdf.set_font('Arial', '', 12)
        pdf.write(8, " waggaa/duraa kan kaffalamuu qabu hunda kaffalanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")
    else:
        pdf.write(8, "2. Kaffaltii tajaajilaa fi kaffaltiiwwan adda addaa qabiyyee durii kanaan wal qabatan hunda raawwatanii kan xumuran ta'uu isaanii ni mirkaneessina.\n")

    pdf.set_x(20)
    pdf.write(8, "3. Lafni/Manni kun ")
    pdf.set_font('Arial', 'B', 12); pdf.write(8, "DHORKAA MANA MURTII"); pdf.set_font('Arial', '', 12)
    pdf.write(8, " ykn dhimma seeraa biroo kamirrayyuu bilisa ta'uu isaa qulqulleessinee mirkaneessineera.\n\n")

    pdf.set_x(20)
    pdf.multi_cell(170, 8, f"Kanaafuu, maamilli kun dhimma {data['dhimma']} raawwachuuf ragaa qulqullinaa kana akka dhiyeeffatan beekamee, waajjirri keenyas dhimma kana irratti mormii kan hin qabne ta'uu ni mirkaneessina.")

    # --- SIGNATURE SECTION ---
    pdf.set_y(235); pdf.set_x(20)
    pdf.set_font('Arial', '', 12); pdf.write(8, "Maqaa Itti Gaafatamaa: ")
    pdf.set_font('Arial', 'B', 12); pdf.write(8, f"{data['head_name']}")
    
    pdf.ln(8); pdf.set_x(20)
    pdf.set_font('Arial', '', 12); pdf.write(8, "Mallattoo: _________________")
    
    # Stamp (Right)
    pdf.set_y(243); pdf.set_x(120)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(70, 8, "(Chaappaa Waajjiraa)", ln=True, align='R')

    return pdf.output(dest='S').encode('latin-1')

# ================= 3. STREAMLIT UI =================
st.header("📝 Sirna Qophii Waraqaa Qulqullinaa (Clearance)")

# To show download button if PDF is ready
if st.session_state.pdf_to_download:
    st.success(f"✅ PDF'n {st.session_state.pdf_name} qophaa'eera!")
    st.download_button(
        label="📥 PDF Buufadhu",
        data=st.session_state.pdf_to_download,
        file_name=st.session_state.pdf_name,
        mime="application/pdf"
    )
    if st.button("🔄 Haaraa Jalqabi"):
        st.session_state.pdf_to_download = None
        st.rerun()

with st.form("clearance_form", clear_on_submit=False):
    st.info("Odeeffannoo maamilaa guuti")
    c1, c2 = st.columns(2)
    m_maqaa = c1.text_input("Maqaa Maamilaa *")
    m_araddaa = c2.text_input("Araddaa *")
    m_qaxana = c1.text_input("Lakk. Qaxana *")
    m_kaartaa = c2.text_input("Lakk. Kaartaa *")
    m_gosa = c1.selectbox("Gosa Qabiyyee", ["Liizii", "Qabiyyee Durii (Permit)"])
    m_bara = c2.text_input("Bara Gibiraa Xumurame (E.C)")
    m_dhimma = c1.selectbox("Dhimma Maaliif?", ["Gurgurtaa", "Liqii Bankii", "Kennaa", "Waliigaltee"])
    
    st.markdown("---")
    m_head = st.text_input("Maqaa Itti Gaafatamaa *")
    m_dhorkaa_bilisa = st.checkbox("Qabiyyeen kun dhorkaa irraa bilisa ta'uu nan mirkaneessa.")

    submit = st.form_submit_button("💾 PDF UUMI")
    
    if submit:
        if m_maqaa and m_kaartaa and m_head and m_dhorkaa_bilisa:
            data_map = {
                'maqaa': m_maqaa, 'araddaa': m_araddaa, 'qaxana': m_qaxana, 
                'kaartaa': m_kaartaa, 'bara_gibiraa': m_bara, 'dhimma': m_dhimma, 
                'gosa_qabiyyee': m_gosa, 'head_name': m_head
            }
            try:
                st.session_state.pdf_to_download = create_clearance_pdf(data_map)
                st.session_state.pdf_name = f"Clearance_{m_maqaa.replace(' ', '_')}.pdf"
                st.rerun()
            except Exception as e:
                st.error(f"Dogoggora: {e}")
        else:
            st.warning("Maaloo, dirree '*' qaban hunda guuti, akkasumas mirkaneessi.")

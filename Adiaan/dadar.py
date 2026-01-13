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
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
    "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonna Magaalaa", "Kaartaa Haaromsuu"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
}

MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
WEEKDAY_MAP = {0: "Wixata", 1: "Filatama", 2: "Roobii", 3: "Kamisa", 4: "Jimmata", 5: "Sanbata", 6: "Dilbata"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
    df['Guyyaa_Torbee'] = df['Date_Obj'].dt.dayofweek.map(WEEKDAY_MAP)
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

# ================= 3. PDF CERTIFICATE ENGINE =================
def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Logos on PDF
    if os.path.exists("logo_bitaa.png"): pdf.image("logo_bitaa.png", 15, 15, 25)
    if os.path.exists("logo_mirgaa.png"): pdf.image("logo_mirgaa.png", 255, 15, 25)

    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    rank_text = {1: "1FFAA (GOLD)", 2: "2FFAA (SILVER)", 3: "3FFAA (BRONZE)"}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    pdf.set_line_width(5); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)
    pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 45, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_text_color(40, 40, 40); pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(20); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 15)
    msg = (f"Waggaa 2026 keessatti tajaajila saffisaa fi amannamaa ta'een Abbootii Dhimmaa {count}\n"
           f"tajaajiluun beekamtii {rank_text[rank]} kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    return pdf.output(dest='S').encode('latin-1')

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
    
    # HEADER LOGOS
    head1, head2, head3 = st.columns([1, 4, 1])
    with head1:
        if os.path.exists("logo_bitaa.png"): st.image("logo_bitaa.png", width=100)
        else: st.title("🏛️")
    with head2:
        st.markdown("<h1 style='text-align: center; color: #1b5e20;'>WAAJJIRA LAFAA MAGAALAA DADAR</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-weight: bold;'>SIRNA BULCHIINSA TAJAAJILAA PRO</p>", unsafe_allow_html=True)
    with head3:
        if os.path.exists("logo_mirgaa.png"): st.image("logo_mirgaa.png", width=100)
        else: st.title("⚖️")
    
    st.divider()

    with st.sidebar:
        st.markdown("### 🏢 MENU")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Tajaajilamtoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.subheader("📈 Galii Ji'aan")
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Filannoo {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")
        
        with st.form("entry", clear_on_submit=True):
            c1, c2 = st.columns(2)
            maqaa_f, ara_f = c1.text_input("Maqaa Abbaa Dhimmaa"), c2.text_input("Araddaa")
            qax_f, ogeessa = c1.text_input("Qaxana"), c2.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details and ogeessa:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!")
                else: st.error("Maaloo odeeffannoo guutuu guuti!")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Calalame")
        if not df.empty:
            f_type = st.sidebar.radio("Calali:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee"])
            sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].unique(), reverse=True))
            filtered = df[df['Waggaa'] == sel_y]
            
            if f_type == "Kurmaana": filtered = filtered[filtered['Kurmaana'] == st.sidebar.selectbox("Kurmaana", [1,2,3,4])]
            elif f_type == "Ji'a": filtered = filtered[filtered['Ji\'a'] == st.sidebar.selectbox("Ji'a", MONTH_ORDER)]
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            total = filtered['Kafaltii_Taj'].sum()
            st.metric(f"Galii ({f_type})", f"{total:,.2f} ETB")
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel Buufadhu", buf.getvalue(), f"Gabaasa_{f_type}.xlsx")
            if c2.button("✈️ Telegram-itti Ergi"):
                caption = f"📊 Gabaasa Galii\n💰 Waliigala: {total:,.2f} ETB\n📅 {datetime.now().strftime('%d/%m/%Y')}"
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", caption): st.success("✅ Ergameera!")
                else: st.error("❌ Hin ergamne!")

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sartiifiikeeta Ogeeyyii Cimaa")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            medals = ["🥇 1FFAA", "🥈 2FFAA", "🥉 3FFAA"]
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2>{medals[i]}</h2><h3>{name}</h3><p>Tajaajilamtoota: {count}</p></div>", unsafe_allow_html=True)
                    pdf_data = create_pdf_cert(name, count, i+1)
                    st.download_button(f"📥 Download PDF", pdf_data, f"Cert_{name}.pdf", "application/pdf")
        else: st.warning("Data'n hin jiru.")

    # --- SEARCH/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi ykn Haqi")
        q = st.text_input("Maqaa Abbaa Dhimmaa barreessi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                    if st.button("🗑 Galmee Kana Haqi", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

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
    try:
        return requests.post(url, files=files, data=data).status_code == 200
    except: return False

# ================= 3. PDF CERTIFICATE ENGINE =================
def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    rank_text = {1: "1FFAA (GOLD)", 2: "2FFAA (SILVER)", 3: "3FFAA (BRONZE)"}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    pdf.set_line_width(5); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)
    pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 40, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
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
        st.markdown("## 🏢 Admin Login")
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.title("🏢 DADAR LAND")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("Tajaajilamtoota", len(df))
            st.bar_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        selected_main = st.multiselect("Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Filannoo {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}")
        
        with st.form("entry"):
            c1, c2 = st.columns(2)
            maqaa_f, ara_f = c1.text_input("Maqaa"), c2.text_input("Araddaa")
            qax_f, ogeessa = c1.text_input("Qaxana"), c2.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("Galmeeffameera!")

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa & Calaltuu")
        if not df.empty:
            f_type = st.sidebar.radio("Filtarii:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee"])
            sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].unique(), reverse=True))
            filtered = df[df['Waggaa'] == sel_y]
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            total = filtered['Kafaltii_Taj'].sum()
            st.metric("Galii Filtarii", f"{total:,.2f} ETB")
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            if st.button("✈️ Telegram-itti Ergi"):
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa: {total} ETB"): st.success("Ergameera!")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Ogeeyyii Cimaa")
        top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        cols = st.columns(3)
        for i, (name, count) in enumerate(top_3.items()):
            with cols[i]:
                st.markdown(f"<div class='card'><h3>{i+1}FFAA</h3><p>{name}</p></div>", unsafe_allow_html=True)
                pdf_data = create_pdf_cert(name, count, i+1)
                st.download_button(f"📥 PDF {i+1}", pdf_data, f"Cert_{name}.pdf")

    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from PIL import Image
from fpdf import FPDF

# --- CONFIGURATION TELEGRAM ---
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

# ================= 1. SETTINGS & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; text-align: center; border-top: 5px solid #2e7d32; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
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
    "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Haaromsuu"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
}
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji_Lakk'] = df['Date_Obj'].dt.month
    df['Ji_Maqaa'] = df['Ji_Lakk'].map({9:"Fulbaana", 10:"Onkololeessa", 11:"Sadaasa", 12:"Muddee", 1:"Amajjii", 2:"Guraandhala", 3:"Bitootessa", 4:"Eebila", 5:"Caamsaa", 6:"Waxabajjii", 7:"Adooleessa", 8:"Hagayya"})
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
    df['Kurmaana'] = df['Ji_Lakk'].apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption, 'parse_mode': 'Markdown'}
    try:
        return requests.post(url, files=files, data=data).status_code == 200
    except: return False

# ================= 3. PDF CERTIFICATE =================
def create_pdf(name, count, rank, l_logo=None, r_logo=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # Design logic hamma kanaa gabaabseera (previous logic fits here)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 40, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 20, f"Obbo/Adde: {name}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.header("🏢 Admin Login")
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
else:
    df = load_data()
    with st.sidebar:
        st.title("🏢 DADAR LAND")
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Telegram", "🏆 Badhaasa", "🔍 Edit/Haqi", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Tajaajilamtoota", len(df))
            st.bar_chart(df.groupby('Ji_Maqaa')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("galmee_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            araddaa = col1.text_input("Araddaa")
            qaxana = col2.text_input("Qaxana")
            tajaajila = st.selectbox("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa", "Ittii Fayyaddam"])
            kafaltii = st.number_input("Kafaltii (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, tajaajila, ogeessa, kafaltii]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success("Galmeeffameera!")

    elif menu == "📈 Gabaasa Telegram":
        st.header("📈 Gabaasa Telegram-itti Erguu")
        f_type = st.radio("Gosa Gabaasaa:", ["Guyyaa", "Torbee", "Ji'a", "Kurmaana", "Waggaa"], horizontal=True)
        
        now = datetime.now()
        filtered = df.copy()
        if f_type == "Guyyaa": filtered = df[df['Guyyaa'] == now.strftime('%d/%m/%Y')]
        elif f_type == "Torbee": filtered = df[(df['Ji_Lakk'] == now.month) & (df['Torbee'] == (now.day-1)//7+1)]
        elif f_type == "Ji'a": filtered = df[df['Ji_Lakk'] == now.month]
        elif f_type == "Kurmaana":
            q = 1 if now.month in [9,10,11,12] else (2 if now.month in [1,2,3] else (3 if now.month in [4,5,6] else 4))
            filtered = df[df['Kurmaana'] == q]
        elif f_type == "Waggaa": filtered = df[df['Waggaa'] == now.year]

        st.dataframe(filtered[COL_NAMES], use_container_width=True)
        total = filtered['Kafaltii_Taj'].sum()
        
        if st.button(f"✈️ Gabaasa {f_type} Ergi"):
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            caption = f"📢 *GABAASA {f_type.upper()}*\n💰 Galii: {total:,.2f} ETB\n👥 Baay'ina: {len(filtered)}"
            if send_to_telegram(buf.getvalue(), f"Gabaasa_{f_type}.xlsx", caption):
                st.success("✅ Ergameera!")

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeeyyii")
        if not df.empty:
            top = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (name, count) in enumerate(top.items(), 1):
                st.write(f"{i}. {name} ({count} Hojii)")
                # Download PDF button as per previous logic

    elif menu == "🔍 Edit/Haqi":
        q = st.text_input("Maqaa Barbaadi")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)
            # Add delete button logic here

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

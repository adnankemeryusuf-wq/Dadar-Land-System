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

MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    # Guyyaa gara bifa Date-ittii jijjiiruuf
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

# ================= 3. MAIN APP =================
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
    with head3:
        if os.path.exists("logo_mirgaa.png"): st.image("logo_mirgaa.png", width=100)
        else: st.title("⚖️")
    
    st.divider()

    with st.sidebar:
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🔍 Barbaadi/Edit", "Ba'i"])

    # --- GABAASA BAL'AA (WITH DATE FILTER) ---
    if menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Calalame")
        if not df.empty:
            # Calaltuu Guyyaa dabalatee
            f_type = st.sidebar.radio("Gosa Calalii:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa Murtaa'aa"])
            
            filtered = df.copy()
            
            if f_type == "Guyyaa Murtaa'aa":
                # User-ichi guyyaa kalandara irraa akka filatu gochuuf
                sel_date = st.sidebar.date_input("Guyyaa Filadhu:", datetime.now())
                formatted_date = sel_date.strftime('%d/%m/%Y')
                filtered = df[df['Guyyaa'] == formatted_date]
            else:
                sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
                filtered = filtered[filtered['Waggaa'] == sel_y]
                
                if f_type == "Kurmaana":
                    sel_q = st.sidebar.selectbox("Kurmaana (Q1-Q4)", [1,2,3,4])
                    filtered = filtered[filtered['Kurmaana'] == sel_q]
                elif f_type == "Ji'a":
                    sel_m = st.sidebar.selectbox("Ji'a", MONTH_ORDER)
                    filtered = filtered[filtered['Ji\'a'] == sel_m]
                elif f_type == "Torbee":
                    sel_m = st.sidebar.selectbox("Ji'a", MONTH_ORDER)
                    sel_w = st.sidebar.selectbox("Torbee (1-4)", [1,2,3,4])
                    filtered = filtered[(filtered['Ji\'a'] == sel_m) & (filtered['Torbee'] == sel_w)]

            # Gabaasa Agarsiisuu
            st.markdown(f"### Bu'aa Calalii: {f_type}")
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            
            total = filtered['Kafaltii_Taj'].sum()
            st.metric(f"Waliigala Galii", f"{total:,.2f} ETB")
            
            # Download & Telegram
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: 
                filtered[COL_NAMES].to_excel(wr, index=False, sheet_name='Gabaasa')
            
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel Buufadhu", buf.getvalue(), f"Gabaasa_{f_type}.xlsx")
            if c2.button("✈️ Telegram-itti Ergi"):
                caption = f"📊 Gabaasa Galii ({f_type})\n💰 Waliigala: {total:,.2f} ETB\n📅 {datetime.now().strftime('%d/%m/%Y')}"
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", caption): st.success("✅ Ergameera!")
                else: st.error("❌ Hin ergamne!")
        else:
            st.warning("Data'n galmeeffame hin jiru.")

    # ... [Kutaaleen hafan (Dashboard, Galmee Haaraa, etc.) akkuma koodii kee isa duraatti itti fufu] ...
    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()

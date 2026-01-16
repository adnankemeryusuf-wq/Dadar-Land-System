# ================== IMPORTS ==================
import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF

# ================== CONFIGURATION ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN")
CHAT_ID_MANAGER = os.getenv("CHAT_ID_MANAGER", "YOUR_CHAT_ID")
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "Adiaan/logo.png"

COL_NAMES = ['Guyyaa','Maqaa_Abbaa_Dhimmaa','Araddaa','Qaxana',
             'Gosa_Tajajjilaa','Maqaa_Ogeessa','Kafaltii_Taj','Biometric_ID']
MONTH_ORDER = ["Fulbaana","Onkololeessa","Sadaasa","Muddee","Amajjii","Guraandhala",
               "Bitootessa","Eebila","Caamsaa","Waxabajjii","Adooleessa","Hagayya"]
MONTH_MAP = {9:"Fulbaana",10:"Onkololeessa",11:"Sadaasa",12:"Muddee",1:"Amajjii",2:"Guraandhala",
             3:"Bitootessa",4:"Eebila",5:"Caamsaa",6:"Waxabajjii",7:"Adooleessa",8:"Hagayya"}

st.set_page_config(
    page_title="Dadar Land Customer Registration System",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢",
    layout="wide"
)

# ================== STYLE ==================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
[data-testid="stSidebar"] { background-color: #1b5e20 !important; }
[data-testid="stSidebar"] * { color: #ffffff !important; }
div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; }
.card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
.stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; border: none; }
</style>
""", unsafe_allow_html=True)

# ================== FUNCTIONS ==================
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

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try: return requests.post(url, files=files, data=data).status_code == 200
    except: return False

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # ... certificate design code ...
    return pdf.output(dest='S').encode('latin-1')

# ================== LOGIN ==================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1,1.2,1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center; color:#1b5e20;'>Dadar Land Administration Customer Registration System</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username", placeholder="admin")
            p = st.text_input("Password", type="password", placeholder="••••••••")
            if st.form_submit_button("Seeni"):
                if u=="DAD" and p=="2026":
                    st.session_state.logged_in=True; st.rerun()
                else: st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard","📝 Galmee Haaraa","📈 Gabaasa Bal'aa","🏆 Badhaasa Ogeeyyii","🔍 Barbaadi/Edit"])
        if st.button("Log Out"): st.session_state.logged_in=False; st.rerun()

    # --- DASHBOARD ---
    if menu=="📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1,c2,c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)
        else: st.info("Data'n galmeeffame hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu=="📝 Galmee Haaraa":
        # registration form code (maqaa, araddaa, qaxana, ogeessa, gosa tajaajilaa, fees, TOT case)
        # save_data(df) call

    # --- GABAASA BAL'AA ---
    elif menu=="📈 Gabaasa Bal'aa":
        # report table, Excel export, Telegram send

    # --- BADHAASA OGEEYYII ---
    elif menu=="🏆 Badhaasa Ogeeyyii":
        # top 3 performers, certificate PDF

    # --- BARBAADI/EDIT ---
    elif menu=="🔍 Barbaadi/Edit":
        # search by name/ID, update, delete

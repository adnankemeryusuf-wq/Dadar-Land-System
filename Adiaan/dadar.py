import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
CHAT_ID_MANAGER = os.getenv("CHAT_ID_MANAGER", "YOUR_CHAT_ID")

DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa','Maqaa_Abbaa_Dhimmaa','Araddaa','Qaxana','Gosa_Tajajjilaa','Maqaa_Ogeessa','Kafaltii_Taj','Biometric_ID']

GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo","Gibira Lafa Qonnaa","Gibira Manaa"],
    "Liizii": ["Liizii Waggaa","Jijjiirraa Maqaa","Kafaltii Liizii Duraa","TOT"],
    "Kaartaa": ["Kaartaa Manaa","Kaartaa Kadastaara","Kaartaa Haaromsuu"],
    "Biometric": ["Mirkaneessaa Quubaa"]
}

MONTH_ORDER = ["Fulbaana","Onkololeessa","Sadaasa","Muddee","Amajjii","Guraandhala","Bitootessa","Eebila","Caamsaa","Waxabajjii","Adooleessa","Hagayya"]
MONTH_MAP = {9:"Fulbaana",10:"Onkololeessa",11:"Sadaasa",12:"Muddee",1:"Amajjii",2:"Guraandhala",3:"Bitootessa",4:"Eebila",5:"Caamsaa",6:"Waxabajjii",7:"Adooleessa",8:"Hagayya"}

# --- PAGE CONFIG & STYLE ---
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg,#f1f8e9 0%,#ffffff 100%); font-family:'Segoe UI',sans-serif; }
[data-testid="stSidebar"] { background-color:#1b5e20 !important; }
[data-testid="stSidebar"] * { color:#ffffff !important; }
div.stForm { background:#fff; border-radius:15px; padding:25px; border:2px solid #2e7d32; box-shadow:0px 4px 15px rgba(0,0,0,0.1); }
.card { background:#fff; padding:20px; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.1); text-align:center; border-top:5px solid #2e7d32; transition:transform 0.2s ease; }
.card:hover { transform:scale(1.05); }
.metric-container { display:flex; justify-content:space-between; gap:10px; margin-bottom:25px; }
h2 { color:#1b5e20; }
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding="utf-8")
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

# --- LOGIN SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1,1.2,1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;color:#1b5e20;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username (admin / user)")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u=="admin" and p=="2026":
                st.session_state.logged_in=True; st.session_state.role="admin"; st.rerun()
            elif u=="user" and p=="1234":
                st.session_state.logged_in=True; st.session_state.role="user"; st.rerun()
            else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    menu_options = ["📊 Dashboard","📝 Galmee Haaraa","📈 Gabaasa Bal'aa","🔍 Barbaadi/Edit","Ba'i"] if st.session_state.role=="admin" else ["📝 Galmee Haaraa","🔍 Barbaadi/Edit","Ba'i"]
    menu = st.sidebar.radio("FILANNOO", menu_options)

    # --- DASHBOARD ---
    if menu=="📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            t_income = df['Kafaltii_Taj'].sum()
            t_clients = len(df)
            st.markdown(f"""
            <div class="metric-container">
                <div class="card">💰 WALIIGALA GALII<br><h2>{t_income:,.2f} ETB</h2></div>
                <div class="card">👥 TAJAAJILAMTOOTA<br><h2>{t_clients}</h2></div>
            </div>
            """, unsafe_allow_html=True)
            monthly_income = df.groupby("Ji'a")["Kafaltii_Taj"].sum().reindex(MONTH_ORDER, fill_value=0)
            st.area_chart(monthly_income)
        else: st.info("Data'n hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu=="📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Filannoo {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}", format="%.2f")
        with st.form("entry", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa", placeholder="Abdi Mahammad Yusuuf")
            ara = c2.text_input("Araddaa", placeholder="01 ykn 02")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            st.markdown("### 🔐 Mirkaneessaa Biometric")
            bio_check = st.checkbox("Mallattoo Quubaa Mirkaneessi")
            if st.form_submit_button("💾 Galmeessi"):
                if name and ara and bio_check:
                    bio_id = f"BIO-{datetime.now().strftime('%M%S')}-{name[:2].upper()}"
                    new = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(details), ogeessa, sum(d_fees.values()), bio_id]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success(f"✅ Galmeeffameera! ID: {bio_id}")
                else: st.error("Maaloo kutaalee hunda guuti ykn Biometric mirkaneessi!")

    #

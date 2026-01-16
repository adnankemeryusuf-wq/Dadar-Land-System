import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF

# ================== CONFIGURATION ==================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "Adiaan/logo.png"

COL_NAMES = ['Guyyaa','Maqaa_Abbaa_Dhimmaa','Araddaa','Qaxana',
             'Gosa_Tajajjilaa','Maqaa_Ogeessa','Kafaltii_Taj','Biometric_ID']
MONTH_ORDER = ["Fulbaana","Onkololeessa","Sadaasa","Muddee","Amajjii","Guraandhala",
               "Bitootessa","Eebila","Caamsaa","Waxabajjii","Adooleessa","Hagayya"]
MONTH_MAP = {9:"Fulbaana",10:"Onkololeessa",11:"Sadaasa",12:"Muddee",1:"Amajjii",2:"Guraandhala",
             3:"Bitootessa",4:"Eebila",5:"Caamsaa",6:"Waxabajjii",7:"Adooleessa",8:"Hagayya"}

st.set_page_config(page_title="Dadar Land System", page_icon="🏢", layout="wide")

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
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}
    data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try: return requests.post(url, files=files, data=data).status_code == 200
    except: return False

# ================== MAIN APP ==================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1,1.2,1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center; color:#1b5e20;'>🏢 Dadar Land System</h2>", unsafe_allow_html=True)
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
        menu = st.radio("FILANNOO", ["📊 Dashboard","📝 Galmee Haaraa","📈 Gabaasa Bal'aa","🏆 Badhaasa Ogeeyyii","🔍 Barbaadi/Edit"])
        if st.sidebar.button("Log Out"): st.session_state.logged_in=False; st.rerun()

    # --- DASHBOARD ---
    if menu=="📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1,c2,c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER))
        else: st.info("Data'n galmeeffame hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu=="📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "TOT"],
            "Kaartaa": ["Kaartaa Haaromsuu", "Kaartaa Kadastaara"]
        }
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"sub_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")
                    if s == "TOT": is_tot = True

        with st.form("entry_form", clear_on_submit=True):
            if is_tot:
                col1, col2 = st.columns(2)
                maqaa_f = f"G: {col1.text_input('Maqaa Gurguraa')} / B: {col2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {col1.text_input('Araddaa G')} / B: {col2.text_input('Araddaa B')}"
                qax_f = f"G: {col1.text_input('Qaxana G')} / B: {col2.text_input('Qaxana B')}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f, ara_f = c1.text_input("Maqaa Abbaa Dhimmaa"), c2.text_input("Araddaa")
                qax_f = c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            bio_check = st.checkbox("Mirkaneessaa Biometric (Fingerprint Scan)")

            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details and bio_check:
                    bio_id = f"BIO-{datetime.now().strftime('%M%S')}"
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values()), bio_id]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success(f"✅ Galmeeffameera! ID: {bio_id}"); st.rerun()
                else: st.error("Maaloo kutaalee hunda guuti!")

    # --- GABAASA BAL'AA ---
    elif menu=="📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Filtarii")
        if not df.empty:
            sel_m = st.selectbox("Ji'a Filadhu", MONTH_ORDER)
            filtered = df[df['Ji\'a'] == sel_m]
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                filtered[COL_NAMES].to_excel(writer, index=False)
            
            c1, c2 = st.columns([1, 4])
            c1.download_button("📥 Excel Download", buf.getvalue(), f"Gabaasa_{sel_m}.xlsx")
            if c2.button("✈️ Telegram-itti Ergi"):
                if send_to_telegram(buf.getvalue(), f"Gabaasa_{sel_m}.xlsx", f"Gabaasa Ji'a {sel_m}"):
                    st.success("Gabaasni gara Telegramitti ergameera!")
        else: st.info("Data'n hin jiru.")

    # --- SEARCH & EDIT ---
    elif menu=="🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi ykn Fooyyessi")
        q = st.text_input("Maqaa ykn Biometric ID barreessi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False) | df['Biometric_ID'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} ({row['Guyyaa']})"):
                    new_fee = st.number_input("Kafaltii Sirreessi", value=float(row['Kafaltii_Taj']), key=f"edit_{idx}")
                    if st.button("💾 Save Changes", key=f"save_{idx}"):
                        df.at[idx, 'Kafaltii_Taj'] = new_fee
                        save_data(df); st.success("Sirreeffameera!"); st.rerun()
                    if st.button("🗑 Haqi", key=f"del_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

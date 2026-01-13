import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from fpdf import FPDF
import io

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom right, #f0f2f6, #e0e5ec); }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    div[data-testid="metric-container"] {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); border-top: 4px solid #3b82f6;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
# Telegram API - Token fi ID kee asitti galchi
TELEGRAM_TOKEN = "7864321234:AAH_F_XXXXXXXXXXXXX" 
TELEGRAM_CHAT_ID = "123456789"

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira Bara Kanaa": 100.0,
    "Ittii Fayyaddam": 50.0,
    "Kartaa": 150.0,
    "Jijjirra Maqaa": {
        "Jijjirraa": 200.0,
        "Lizii Duraa": 500.0,
        "TOT": 100.0
    },
    "Dhimma Dangaa": 100.0,
    "Dhimma Mana Murtii": 0.0,
    "Ugura Mana Murtii": 50.0,
    "Uguraa Mana Murtii Kasuu": 50.0,
    "Dorkka Liqii Bankii": 100.0,
    "Dorkkaa Liqii Bankii Kasuu": 100.0
}
elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            
            # Gosa Tajaajilaa Filachuu
            gosa = col2.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            
            # Kaffaltii ofumaan herregu
            if gosa == "Jijjirra Maqaa":
                # Kaffaltii sadii walitti ida'a
                k_jijjirra = GATII_DICT["Jijjirra Maqaa"]["Kafaltii Jijjirraa Maqaa"]
                k_lizii = GATII_DICT["Jijjirra Maqaa"]["Kafaltii Lizii Duraa"]
                k_tot = GATII_DICT["Jijjirra Maqaa"]["Kafaltii TOT"]
                base_fee = k_jijjirra + k_lizii + k_tot
                st.warning(f"Jijjirra Maqaa: Jijjirra({k_jijjirra}) + Lizii({k_lizii}) + TOT({k_tot})")
            else:
                base_fee = GATII_DICT[gosa]

            # Kaffaltii dabalataa yoo jiraate
            add_fee = st.number_input("Kafaltii Dabalataa (Penalty/Other)", min_value=0.0, value=0.0)
            
            total_fee = base_fee + add_fee
            st.info(f"💰 Kafaltii Waliigalaa: **{total_fee} ETB**")
            
            if st.form_submit_button("💾 Galmeessi", use_container_width=True):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, total_fee]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                else:
                    st.error("Maqaa fi Ogeessa guuti!")
# ================= 3. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    try:
        return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    except:
        return pd.DataFrame(columns=COL_NAMES)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"document": file})
            return True
    except:
        return False

def generate_certificate_pro(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(3); pdf.set_draw_color(184, 134, 11); pdf.rect(10, 10, 277, 190) 
    pdf.ln(30); pdf.set_font('Arial', 'B', 45); pdf.set_text_color(20, 50, 100)
    pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", ln=True, align='C')
    pdf.ln(15); pdf.set_font('Arial', 'B', 35); pdf.set_text_color(150, 0, 0)
    pdf.cell(0, 20, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 18); pdf.set_text_color(0, 0, 0)
    msg = "Tajaajila qulqulluu fi saffisaa tajaajilamtootaaf kennaa turaniif beekamtii kana kennineefirra."
    pdf.multi_cell(0, 10, msg, align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align: center;'>🏢 Dadar Land</h1>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Username ykn Password dogoggora!")
else:
    with st.sidebar:
        st.header(f"👤 {st.session_state.user}")
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Sirreessi", "📤 Gabaasa Ergi", "🏆 Sartiifiketa", "Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Gabaasaa")
        c1, c2, c3 = st.columns(3)
        c1.metric("Baay'ina Tajaajilaa", len(df))
        # Kafaltii herreguuf string gara float tti jijjiiru
        if not df.empty:
            total = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').sum()
        else:
            total = 0
        c2.metric("Kafaltii Waliigalaa", f"{total} ETB")
        c3.metric("Araddaawwan", len(df['Araddaa'].unique()) if not df.empty else 0)
        st.divider()
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Galmeessi")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            gosa = col2.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            
            # Kafaltii Herreguu
            if gosa == "Jijjirra Maqaa":
                d = GATII_DICT["Jijjirra Maqaa"]
                base_fee = d["Jijjirraa"] + d["Lizii Duraa"] + d["TOT"]
                st.warning(f"💡 Breakdown: Jijjirraa({d['Jijjirraa']}) + Lizii({d['Lizii Duraa']}) + TOT({d['TOT']})")
            else:
                base_fee = GATII_DICT[gosa]

            extra = st.number_input("Kafaltii Dabalataa (Penalty/Kkf)", min_value=0.0, step=10.0)
            total_fee = base_fee + extra
            st.info(f"💰 Kafaltii Waliigalaa: **{total_fee} ETB**")
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, total_fee]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success(f"✅ Tajaajilli {maqaa} galmeeffameera!")
                else:
                    st.error("Maqaa fi Ogeessa guutuun dirqama!")

    elif menu == "🔍 Barbaadi & Sirreessi":
        st.header("🔍 Barbaadi ykn Sirreessi")
        q = st.text_input("Maqaa abbaa dhimmaa barreessi...")
        if not df.empty:
            search = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            for idx, row in search.iterrows():
                with st.expander(f"👤 {row['Maqaa']} - {row['Gosa']}"):
                    col_a, col_b = st.columns(2)
                    edit_maqaa = col_a.text_input("Maqaa Sirreessi", row['Maqaa'], key=f"n_{idx}")
                    edit_araddaa = col_b.text_input("Araddaa Sirreessi", row['Araddaa'], key=f"a_{idx}")
                    
                    if st.button("💾 Ol-kaayi", key=f"s_{idx}"):
                        df.at[idx, 'Maqaa'] = edit_maqaa
                        df.at[idx, 'Araddaa'] = edit_araddaa
                        save_data(df)
                        st.success("Sirreeffameera!")
                        st.rerun()
                    
                    if st.button("🗑 Haqi", key=f"d_{idx}"):
                        df = df.drop(idx)
                        save_data(df)
                        st.warning("Haqameera!")
                        st.rerun()

    elif menu == "📤 Gabaasa Ergi":
        st.header("📤 Gabaasa Telegram-itti Ergi")
        if not df.empty:
            if st.button("📤 Gabaasa Excel Ergi"):
                file_name = "Gabaasa_Dadar.xlsx"
                df.to_excel(file_name, index=False)
                if send_to_telegram(file_name, f"Gabaasa Guyyaa: {datetime.now().strftime('%d/%m/%Y')}"):
                    st.success("Gabaasni Excel Telegram-itti ergameera!")
                else:
                    st.error("Error: Telegram-itti erguu hin danda'amne. Bot Token ilaali.")
        else:
            st.info("Gabaasni erguuf data'n hin jiru.")

    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Sartiifiketa Beekamtii Ogeessaa")
        if not df.empty:
            og_list = df['Ogeessa'].unique()
            og = st.selectbox("Ogeessa Filadhu", og_list)
            if st.button("📜 PDF Qopheessi"):
                pdf_bytes = generate_certificate_pro(og)
                st.download_button(
                    label="📥 Sartiifiketa Buufadhu",
                    data=pdf_bytes,
                    file_name=f"Sartii_{og}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Ogeessi galmaa'e hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()


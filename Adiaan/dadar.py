import streamlit as st
import pandas as pd
import os
import hashlib
import requests
from datetime import datetime
from fpdf import FPDF
from PIL import Image

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
    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
TELEGRAM_TOKEN = "7864321234:AAH_F_XXXXXXXXXXXXX" 
TELEGRAM_CHAT_ID = "123456789"

COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

# Gosa Tajaajilaa fi Gatii (Structure haaraa)
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

# ================= 3. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"document": file})
            return True
    except: return False

def generate_certificate_pro(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(3); pdf.set_draw_color(184, 134, 11); pdf.rect(10, 10, 277, 190) 
    pdf.ln(30); pdf.set_font('Arial', 'B', 45); pdf.set_text_color(20, 50, 100)
    pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", ln=True, align='C')
    pdf.ln(15); pdf.set_font('Arial', 'B', 35); pdf.set_text_color(150, 0, 0)
    pdf.cell(0, 20, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', '', 18); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, "Tajaajila qulqulluu fi saffisaa tajaajilamtootaaf kennaa turaniif beekamtii kana kennineefirra.", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align: center;'>🏢 Dadar Land</h1>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
else:
    with st.sidebar:
        st.header(f"👤 {st.session_state.get('user', 'Admin')}")
        menu = st.radio("MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi & Sirreessi", "📤 Gabaasa Ergi", "🏆 Sartiifiketa", "Ba'i"])

    df = load_data()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("Baay'ina", len(df))
        total = df['Kafaltii_Taj'].astype(float).sum() if not df.empty else 0
        c2.metric("Kafaltii (ETB)", f"{total}")
        st.divider()
        st.dataframe(df, use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col1.text_input("Maqaa Ogeessaa")
            gosa = col2.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            
            # Herrega Kafaltii
            if gosa == "Jijjirra Maqaa":
                d = GATII_DICT["Jijjirra Maqaa"]
                base_fee = d["Jijjirraa"] + d["Lizii Duraa"] + d["TOT"]
                st.warning(f"💡 Breakdown: Jijjirraa({d['Jijjirraa']}) + Lizii({d['Lizii Duraa']}) + TOT({d['TOT']})")
            else:
                base_fee = GATII_DICT[gosa]

            total_fee = base_fee + st.number_input("Kafaltii Dabalataa", min_value=0.0)
            st.info(f"💰 Kafaltii Waliigalaa: {total_fee} ETB")
            
            if st.form_submit_button("💾 Galmeessi"):
                new = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, total_fee]
                df.loc[len(df)] = new
                save_data(df); st.success("Galmeeffameera!")

    elif menu == "🔍 Barbaadi & Sirreessi":
        st.header("🔍 Barbaadi & Sirreessi")
        q = st.text_input("Maqaa barbaadi...")
        if not df.empty:
            search = df[df['Maqaa'].str.contains(q, case=False, na=False)]
            for idx, row in search.iterrows():
                with st.expander(f"👤 {row['Maqaa']}"):
                    n_maqaa = st.text_input("Maqaa", row['Maqaa'], key=f"n_{idx}")
                    if st.button("Save", key=f"s_{idx}"):
                        df.at[idx, 'Maqaa'] = n_maqaa
                        save_data(df); st.rerun()
                    if st.button("Delete", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    elif menu == "📤 Gabaasa Ergi":
        st.header("📤 Telegram-itti Ergi")
        if st.button("📤 Excel Ergi"):
            df.to_excel("Gabaasa.xlsx", index=False)
            send_to_telegram("Gabaasa.xlsx", "Gabaasa Dadar"); st.success("Ergameera!")

    elif menu == "🏆 Sartiifiketa":
        st.header("🏆 Sartiifiketa Beekamtii")
        if not df.empty:
            og = st.selectbox("Ogeessa Filadhu", df['Ogeessa'].unique())
            if st.button("📜 PDF Qopheessi"):
                pdf = generate_certificate_pro(og)
                st.download_button("📥 Buufadhu", pdf, f"Sartii_{og}.pdf")

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()            st.dataframe(res, use_container_width=True)
            
            if st.session_state.role == "Admin" and not res.empty:
                st.divider()
                st.subheader("🗑 Galmee Haquu (Admin Only)")
                idx_to_del = st.number_input("ID Galmee haquu barbaaddu galchi:", step=1, min_value=0)
                if st.button("Haquu Mirkaneessi"):
                    conn = sqlite3.connect("dadar_land.db")
                    conn.cursor().execute("DELETE FROM records WHERE id=?", (idx_to_del,))
                    conn.commit()
                    conn.close()
                    st.warning(f"Galmeen ID {idx_to_del} haqameera!")
                    st.rerun()

    elif menu == "⚙️ Bulchiinsa":
        if st.session_state.role == "Admin":
            st.header("⚙️ Bulchiinsa Fayyadamtootaa")
            with st.expander("Nama Haaraa Galmeessi"):
                new_u = st.text_input("Username Haaraa")
                new_p = st.text_input("Password Haaraa", type="password")
                new_r = st.selectbox("Gahee (Role)", ["Ogeessa", "Admin"])
                if st.button("Fayyadamaa Uumi"):
                    if new_u and new_p:
                        conn = sqlite3.connect("dadar_land.db")
                        try:
                            conn.cursor().execute("INSERT INTO users VALUES (?,?,?)", (new_u, hash_password(new_p), new_r))
                            conn.commit()
                            st.success(f"Fayyadamaa '{new_u}' uumameera!")
                        except:
                            st.error("Maqaan kun duraan jira!")
                        finally:
                            conn.close()
            
            st.subheader("Tarree Hojjettootaa")
            conn = sqlite3.connect("dadar_land.db")
            st.table(pd.read_sql_query("SELECT username, role FROM users", conn))
            conn.close()
        else:
            st.error("Kutaa kana arguuf mirga Admin qabaachuu qabda!")


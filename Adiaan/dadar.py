import streamlit as st
import pandas as pd
import os
import requests
import io
from datetime import datetime, timedelta
from fpdf import FPDF

# ================= 1. CONFIGURATION & TELEGRAM =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID = "7329587700"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def send_telegram_report(title, total_money, total_people, details_text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = (
        f"📊 {title}\n"
        f"📅 Guyyaa: {datetime.now().strftime('%d/%m/%Y')}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👥 Maamiltoota: {total_people}\n"
        f"💰 Galii: {total_money:,.2f} ETB\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📝 TARREEFFAMA:\n{details_text}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏢 Wajjira Lafa Dadar"
    )
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except:
        st.error("Gabaasa Telegram irratti erguun hin danda'amne!")

# ================= 2. CORE DATA FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Guyyaa'] = pd.to_datetime(df['Guyyaa'], dayfirst=True)
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save.to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_clearance_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "BULCHIINSA MAGAALAA DADAR", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "WAJJIRA LAFA FI MANAA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "WARAQAA RAGAA QULQULLUMMAA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    text = (f"Maamilli Maqaan isaanii Obbo/Adde {row['Maqaa_Abbaa_Dhimmaa']} ta'an, "
            f"Araddaa {row['Araddaa']} keessatti tajaajila {row['Gosa_Tajajjilaa']} "
            f"kaffaltii Birrii {row['Kafaltii_Taj']:,} kaffalanii waan xumuraniif "
            f"waraqaan ragaa qulqullummaa kun kennameefii jira.")
    pdf.multi_cell(0, 10, text)
    pdf.ln(20)
    pdf.cell(200, 10, "Mallattoo Itti Gaafatamaa: ___________________", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. APP INTERFACE =================
st.set_page_config(page_title="Dadar Land Admin", layout="wide")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.header("🏢 DADAR ADMIN")
        menu = st.radio("FILANNOO:", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "📄 Clearance", "📤 Gabaasa Telegram", "🚪 Logout"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        c1, c2 = st.columns(2)
        c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Baay'ina Galmee", len(df))
        st.dataframe(df.sort_values(by='Guyyaa', ascending=False), use_container_width=True)

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Haaraa")
        with st.form("reg"):
            name = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            gosa = st.selectbox("Gosa Tajaajilaa", ["Jijjiirraa Maqaa", "Kaartaa Haaraa", "Waraqaa Qulqullummaa", "Adabbii"])
            fee = st.number_input("Kaffaltii", min_value=0.0)
            ogeessa = st.text_input("Ogeessa")
            if st.form_submit_button("Galmeessi"):
                if name and ogeessa:
                    new_val = [[datetime.now().strftime('%d/%m/%Y'), name, ara, gosa, ogeessa, fee]]
                    new_df = pd.DataFrame(new_val, columns=COL_NAMES)
                    df = pd.concat([df, new_df], ignore_index=True)
                    save_data(df)
                    st.success("Milkaa'inaan Galmeeffameera!")
                else: st.error("Maaloo odeeffannoo guutuu galchi!")

    # --- BARBAADI ---
    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi")
        q = st.text_input("Maqaa galchi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

    # --- CLEARANCE ---
    elif menu == "📄 Clearance":
        st.title("📄 Waraqaa Qulqullummaa")
        q = st.text_input("Maqaa Maamilaa barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                col1, col2 = st.columns([3, 1])
                col1.write(f"✅ **{row['Maqaa_Abbaa_Dhimmaa']}** | {row['Gosa_Tajajjilaa']} | {row['Kafaltii_Taj']} ETB")
                pdf_bytes = create_clearance_pdf(row)
                col2.download_button("📥 PDF Buufadhu", pdf_bytes, f"Clearance_{idx}.pdf", "application/pdf", key=f"btn_{idx}")

    # --- TELEGRAM REPORT ---
    elif menu == "📤 Gabaasa Telegram":
        st.title("📤 Gabaasa Telegram")
        g_type = st.selectbox("Gosa Gabaasaa:", ["Guyyaa", "Torbee", "Ji'a", "Kurmaana", "Waggaa"])
        if st.button("🚀 Gabaasa Ergi"):
            now = datetime.now()
            if g_type == "Guyyaa": filtered = df[df['Guyyaa'].dt.date == now.date()]
            elif g_type == "Torbee": filtered = df[df['Guyyaa'] > (now - timedelta(days=7))]
            elif g_type == "Ji'a": filtered = df[df['Guyyaa'].dt.month == now.month]
            elif g_type == "Kurmaana":
                q_num = (now.month - 1) // 3 + 1
                filtered = df[(df['Guyyaa'].dt.month - 1) // 3 + 1 == q_num]
            else: filtered = df[df['Guyyaa'].dt.year == now.year]

            if not filtered.empty:
                total_money = filtered['Kafaltii_Taj'].sum()
                details = "".join([f"• {r['Maqaa_Abbaa_Dhimmaa']}: {r['Kafaltii_Taj']} ETB\n" for i, r in filtered.iterrows()])
                send_telegram_report(f"GABAASA {g_type.upper()}", total_money, len(filtered), details)
                st.success(f"Gabaasni {g_type} ergameera!")
            else: st.warning("Data'n hin argamne.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

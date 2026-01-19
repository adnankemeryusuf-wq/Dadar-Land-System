import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(
    page_title="Dadar Land Administration",
    page_icon="🏢",
    layout="wide"
)

DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID_MANAGER = "YOUR_CHAT_ID"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

COL_NAMES = [
    'Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa',
    'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj'
]

SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa",
        "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa",
        "Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"
    ]
}

# ================= HELPERS =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False)

def get_ec_date():
    now = datetime.now()
    ec = EthiopianDateConverter.to_ethiopian(now.year, now.month, now.day)
    return f"{ec.day:02d}/{ec.month:02d}/{ec.year}"

# ================= TELEGRAM =================
def send_excel_to_telegram(file_bytes, filename, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {"document": (filename, file_bytes)}
    data = {"chat_id": CHAT_ID_MANAGER, "caption": caption}
    requests.post(url, files=files, data=data)

# ================= EXCEL =================
def create_excel_report(df, mode):
    df['Date'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')

    if mode == "daily":
        df = df[df['Date'].dt.date == datetime.now().date()]
        fname = "Daily_Report.xlsx"
    else:
        df = df[(df['Date'].dt.month == datetime.now().month) &
                (df['Date'].dt.year == datetime.now().year)]
        fname = "Monthly_Report.xlsx"

    if df.empty:
        return None

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df[COL_NAMES].to_excel(writer, index=False)
    out.seek(0)
    return out, fname

# ================= PDF =================
def create_clearance_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.cell(0,10,"MOOTUMMAA NAANNOO OROMIYAA",ln=True,align="C")
    pdf.cell(0,10,"BULCHIINSA MAGAALAA DADAR - WAAJJIRA LAFAA",ln=True,align="C")
    pdf.ln(10)

    pdf.multi_cell(
        0,8,
        f"Maqaa: {data['maqaa']}\n"
        f"Araddaa: {data['araddaa']}  Qaxana: {data['qaxana']}\n"
        f"Kaartaa: {data['kaartaa']}\n"
        f"Dhimma: {data['dhimma']}\n"
        f"Itti Gaafatamaa: {data['head']}\n"
        f"Guyyaa: {get_ec_date()}"
    )
    return pdf.output(dest="S").encode("latin-1")

# ================= LOGIN =================
if 'logged' not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026":
            st.session_state.logged = True
            st.rerun()
        else:
            st.error("Dogoggora login")

# ================= MAIN APP =================
else:
    df = load_data()
    menu = st.sidebar.radio(
        "MENU",
        ["📊 Dashboard", "📝 Galmee Haaraa", "📄 Clearance", "📤 Telegram Report"]
    )

    # ---------- DASHBOARD ----------
    if menu == "📊 Dashboard":
        if df.empty:
            st.info("Ragaan hin jiru")
        else:
            c1,c2,c3 = st.columns(3)
            c1.metric("💰 Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())

            fig = px.bar(
                df.groupby("Maqaa_Ogeessa")["Kafaltii_Taj"].sum().reset_index(),
                x="Maqaa_Ogeessa", y="Kafaltii_Taj"
            )
            st.plotly_chart(fig, use_container_width=True)

    # ---------- REGISTRATION ----------
    elif menu == "📝 Galmee Haaraa":
        with st.form("reg"):
            name = st.text_input("Maqaa")
            ogeessa = st.text_input("Ogeessa")
            services = st.multiselect("Tajaajila", sum(SERVICE_STRUCTURE.values(), []))
            fee = st.number_input("Kafaltii", min_value=0.0)
            if st.form_submit_button("Galmeessi"):
                df.loc[len(df)] = [
                    datetime.now().strftime('%d/%m/%Y'),
                    name,"","",", ".join(services),ogeessa,fee
                ]
                save_data(df)
                st.success("Galmeeffameera")

    # ---------- CLEARANCE ----------
    elif menu == "📄 Clearance":
        with st.form("clr"):
            maqaa = st.text_input("Maqaa")
            araddaa = st.text_input("Araddaa")
            qaxana = st.text_input("Qaxana")
            kaartaa = st.text_input("Kaartaa")
            dhimma = st.text_input("Dhimma")
            head = st.text_input("Itti Gaafatamaa")
            if st.form_submit_button("PDF UUMI"):
                pdf = create_clearance_pdf(
                    {"maqaa":maqaa,"araddaa":araddaa,"qaxana":qaxana,
                     "kaartaa":kaartaa,"dhimma":dhimma,"head":head}
                )
                st.download_button("⬇️ PDF Buusi", pdf, "Clearance.pdf")

    # ---------- TELEGRAM ----------
    elif menu == "📤 Telegram Report":
        if st.button("📊 Daily Excel → Telegram"):
            res = create_excel_report(df,"daily")
            if res:
                send_excel_to_telegram(*res,"Daily Report")
                st.success("Ergameera")
        if st.button("📈 Monthly Excel → Telegram"):
            res = create_excel_report(df,"monthly")
            if res:
                send_excel_to_telegram(*res,"Monthly Report")
                st.success("Ergameera")

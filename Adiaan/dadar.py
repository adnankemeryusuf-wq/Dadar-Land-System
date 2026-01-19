import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import requests
import matplotlib.pyplot as plt
from io import BytesIO

# ================= CONFIG =================
st.set_page_config("Dadar Land Admin Pro", layout="wide", page_icon="🏢")

DATA_FILE = "dadar_data.txt"

BOT_TOKEN = "BOT_TOKEN_KEE_ASI"
CHAT_ID = "CHAT_ID_KEE_ASI"

COLS = [
    "Guyyaa",
    "Maqaa_Abbaa_Dhimmaa",
    "Araddaa",
    "Qaxana",
    "Gosa_Tajaajilaa",
    "Maqaa_Ogeessa",
    "Kafaltii"
]

SERVICE_STRUCTURE = {
    "Gibira": ["Gibira Baaxii", "Gibira Qonnaa", "TOT"],
    "Kaartaa": ["Kaartaa Haaraa", "Jijjiirraa Maqaa"],
    "Ijaarsaa": ["Hayyama Ijaarsaa"],
    "Seeraa": ["Ugura Mana Murtii"]
}

# ================= STYLE =================
st.markdown("""
<style>
.stApp {background:#f4f7f6;}
.card {background:white;padding:20px;border-radius:12px;
box-shadow:0 2px 6px rgba(0,0,0,.1);text-align:center;}
[data-testid="stSidebar"] {background:#1b5e20;}
[data-testid="stSidebar"] * {color:white;}
</style>
""", unsafe_allow_html=True)

# ================= DATA =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COLS)
    return pd.read_csv(DATA_FILE, sep="|", names=COLS)

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, header=False)

# ================= TELEGRAM =================
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass

def send_telegram_file(file_bytes, filename, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": caption},
            files={"document": (filename, file_bytes)}
        )
    except:
        pass

# ================= EXCEL & CHART =================
def generate_excel(df):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Gabaasa")
    buf.seek(0)
    return buf.getvalue()

def generate_chart(df):
    fig, ax = plt.subplots()
    df.groupby("Maqaa_Ogeessa")["Kafaltii"].sum().plot(kind="bar", ax=ax)
    ax.set_title("Galii Ogeeyyii")
    ax.set_ylabel("ETB")

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

# ================= PDF =================
def generate_pdf(name, count, rank):
    pdf = FPDF("L","mm","A4")
    pdf.add_page()
    pdf.set_line_width(3)
    pdf.rect(10,10,277,190)
    pdf.set_font("Arial","B",30)
    pdf.cell(0,30,"SARTIIFIKETA BEEKAMTII",ln=True,align="C")
    pdf.ln(10)
    pdf.set_font("Arial","B",22)
    pdf.cell(0,20,name.upper(),ln=True,align="C")
    pdf.set_font("Arial","",16)
    pdf.multi_cell(
        0,10,
        f"Waggaa 2026 tajaajila {count} kennuun sadarkaa {rank}ffaa argateera.",
        align="C"
    )
    return pdf.output(dest="S").encode("latin-1","replace")

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "admin" and p == "123":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Dogoggora!")
    st.stop()

# ================= MAIN =================
df = load_data()

with st.sidebar:
    st.title("🏢 Dadar Admin")
    menu = st.radio("MENU", [
        "📊 Dashboard",
        "📝 Galmee Haaraa",
        "📈 Gabaasa",
        "🏆 Badhaasa",
        "🚪 Ba'i"
    ])

# -------- DASHBOARD --------
if menu == "📊 Dashboard":
    if df.empty:
        st.info("Data hin jiru")
    else:
        c1,c2,c3 = st.columns(3)
        c1.markdown(f"<div class='card'><h3>💰 Galii</h3><h2>{df['Kafaltii'].sum():,.2f}</h2></div>",unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>👥 Tajaajilamtoota</h3><h2>{len(df)}</h2></div>",unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>👷 Ogeeyyii</h3><h2>{df['Maqaa_Ogeessa'].nunique()}</h2></div>",unsafe_allow_html=True)

# -------- GALMEE --------
elif menu == "📝 Galmee Haaraa":
    selected = st.multiselect("Gosa Tajaajilaa", SERVICE_STRUCTURE.keys())
    services = []
    total_fee = 0

    for cat in selected:
        subs = st.multiselect(cat, SERVICE_STRUCTURE[cat])
        for s in subs:
            fee = st.number_input(f"Kaffaltii {s}", min_value=0.0)
            services.append(s)
            total_fee += fee

    with st.form("reg"):
        name = st.text_input("Maqaa Abbaa Dhimmaa")
        ara = st.text_input("Araddaa")
        qax = st.text_input("Qaxana")
        ogeessa = st.text_input("Maqaa Ogeessa")

        if st.form_submit_button("💾 Galmeessi"):
            if name and services and ogeessa:
                row = [
                    datetime.now().strftime("%d/%m/%Y"),
                    name, ara, qax,
                    ", ".join(services),
                    ogeessa,
                    total_fee
                ]
                df = pd.concat([df, pd.DataFrame([row], columns=COLS)])
                save_data(df)

                send_telegram_message(
                    f"📥 Galmee Haaraa\n👤 {name}\n🛠 {services}\n💰 {total_fee} ETB\n👷 {ogeessa}"
                )

                st.success("Galmeeffameera!")
            else:
                st.error("Odeeffannoo guuti!")

# -------- GABAASA --------
elif menu == "📈 Gabaasa":
    st.dataframe(df, use_container_width=True)

    excel_bytes = generate_excel(df)
    chart_bytes = generate_chart(df)

    if st.button("✈️ Excel + Chart Telegramtti Ergi"):
        send_telegram_file(excel_bytes, "Gabaasa.xlsx", "📊 Gabaasa Excel")
        send_telegram_file(chart_bytes, "Chart.png", "📈 Chart Galii")
        st.success("Telegramtti ergameera!")

# -------- BADHAASA --------
elif menu == "🏆 Badhaasa":
    if not df.empty:
        top = df["Maqaa_Ogeessa"].value_counts().head(3)
        for i,(name,count) in enumerate(top.items(),1):
            pdf = generate_pdf(name,count,i)
            st.download_button(
                f"📥 PDF {i}ffaa - {name}",
                pdf,
                f"Cert_{name}.pdf",
                "application/pdf"
            )

# -------- LOGOUT --------
elif menu == "🚪 Ba'i":
    st.session_state.login = False
    st.rerun()

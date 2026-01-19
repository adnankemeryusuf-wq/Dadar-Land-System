import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px
from ethiopian_date import EthiopianDateConverter

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


# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(
    page_title="Dadar Land Administration", 
    page_icon="🏢", 
    layout="wide"
)

# CSS Styling
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd; }
    .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. SERVICE STRUCTURE =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Kaartaa Lafa Qoonnaa"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa",
        "Kaffaltii Seeressuu (Regularization)",
        "Adabbii Faallaa Pilaanii"
    ],
}

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 4. LOGIN SYSTEM =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Admin Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Maqaa ykn Koodiin dogoggora!")

# ================= 5. MAIN APP =================
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa"])

    # ================= REGISTRATION =================
    if menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")

        # Service selection
        selected_cats = st.multiselect("🟢 Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        final_services = []
        fees_dict = {}

        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    st.write(f"📂 {cat}")
                    subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat], key=f"sub_{cat}")
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s} (ETB):", min_value=0.0, key=f"fee_{s}")
                        final_services.append(s)
                        fees_dict[s] = fee

        total_fee = sum(fees_dict.values())
        st.markdown(f"**💰 Waliigala Kafaltii: {total_fee:.2f} ETB**")
        st.divider()
        st.subheader("📝 Odeeffannoo Maamilaa")

        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee Scan (JPG/PNG)", type=['jpg','png','jpeg'])

            if st.form_submit_button("💾 Galmeessi"):
                errors = []

                # VALIDATION
                if not name.strip(): errors.append("❌ Maqaa dirqamaa guutuu galchi!")
                if not final_services: errors.append("❌ Maaloo tajaajila tokko filadhu!")
                if qax and (not qax.isdigit() or int(qax) < 1): errors.append("❌ Qaxana lakkoofsa sirrii galchi (1-1000)")
                if total_fee < 0: errors.append("❌ Kafaltii sirrii galchi (≥ 0)")
                if nagahee and nagahee.size > 5*1024*1024: errors.append("❌ Fayilii Nagahee ol-kaayame (max 5MB)")

                if errors:
                    for e in errors: st.error(e)
                else:
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())

                    new_row = [
                        datetime.now().strftime('%d/%m/%Y'),
                        name.strip(), ara.strip(), qax.strip(),
                        ", ".join(final_services), ogeessa.strip(), total_fee
                    ]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Waliigala: {total_fee:.2f} ETB")
                    st.balloons()

    # ================= DASHBOARD =================
    elif menu == "📊 Dashboard":
        st.header("📊 Dashboard")

        if not df.empty:
            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Maamiltootaa", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.divider()

            # Fees by Officer
            st.subheader("👷 Fees by Officer")
            fees_by_officer = df.groupby('Maqaa_Ogeessa')['Kafaltii_Taj'].sum().reset_index()
            fig_officer = px.bar(fees_by_officer, x='Maqaa_Ogeessa', y='Kafaltii_Taj',
                                 text='Kafaltii_Taj', color='Maqaa_Ogeessa', labels={'Kafaltii_Taj':'ETB'})
            st.plotly_chart(fig_officer, use_container_width=True)
            st.divider()

            # Fees by Service
            st.subheader("🏷 Fees by Service")
            df_services = df.assign(Service=df['Gosa_Tajajjilaa'].str.split(', ')).explode('Service')
            fees_by_service = df_services.groupby('Service')['Kafaltii_Taj'].sum().reset_index()
            fig_service = px.bar(fees_by_service, x='Service', y='Kafaltii_Taj',
                                 text='Kafaltii_Taj', color='Service')
            fig_service.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_service, use_container_width=True)
            st.divider()

            # Payment trend
            st.subheader("📈 Payment Trend")
            df['Guyyaa'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
            trend_fig = px.line(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa',
                                labels={'Kafaltii_Taj':'Fee (ETB)', 'Guyyaa':'Date'})
            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    # ================= BADHAASA =================
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        if not df.empty:
            top_officers = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_officers.items()):
                with cols[i]:
                    st.markdown(f"### {name}\n**Hojii: {count}**")
        else:
            st.info("Ragaan ogeeyyii hin jiru.")import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# ================= CONFIG =================
st.set_page_config(page_title="Dadar Land System", layout="wide")

DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID_MANAGER = "YOUR_CHAT_ID"

COL_NAMES = [
    'Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa',
    'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj'
]

# ================= SESSION =================
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""

# ================= HELPERS =================
def get_ethiopian_date():
    now = datetime.now()
    ec = EthiopianDateConverter.to_ethiopian(now.year, now.month, now.day)
    return f"{ec.day:02d}/{ec.month:02d}/{ec.year}"

# ================= CLEARANCE PDF =================
def create_clearance_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)

    pdf.cell(0,10,"MOOTUMMAA NAANNOO OROMIYAA",ln=True,align="C")
    pdf.cell(0,10,"WAAJJIRA LAFAA - BULCHIINSA MAGAALAA DADAR",ln=True,align="C")
    pdf.ln(10)

    pdf.multi_cell(0,8,
        f"Waraqaan ragaa kun Obbo/Adde {data['maqaa']} "
        f"Araddaa {data['araddaa']} Qaxana {data['qaxana']} "
        f"Lakk. Kaartaa {data['kaartaa']} irratti kennama.\n\n"
        f"Bara Gibiraa: {data['bara']}\n"
        f"Dhimma: {data['dhimma']}\n\n"
        f"Itti Gaafatamaa: {data['head']}\n"
        f"Guyyaa: {get_ethiopian_date()}"
    )

    return pdf.output(dest="S").encode("latin-1")

# ================= DATA =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None)

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
        df = df[
            (df['Date'].dt.month == datetime.now().month) &
            (df['Date'].dt.year == datetime.now().year)
        ]
        fname = "Monthly_Report.xlsx"

    if df.empty:
        return None

    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df[COL_NAMES].to_excel(writer, index=False)
    out.seek(0)
    return out, fname

# ================= UI =================
st.title("🏛 Dadar Land Administration System")

tab1, tab2 = st.tabs(["📝 Clearance PDF", "📊 Reports"])

# -------- TAB 1 --------
with tab1:
    with st.form("clearance_form"):
        m1, m2 = st.columns(2)
        maqaa = m1.text_input("Maqaa Maamilaa *")
        araddaa = m2.text_input("Araddaa *")
        qaxana = m1.text_input("Qaxana *")
        kaartaa = m2.text_input("Lakk. Kaartaa *")
        bara = m1.text_input("Bara Gibiraa")
        dhimma = m2.selectbox("Dhimma", ["Gurgurtaa","Liqii","Kennaa"])
        head = st.text_input("Maqaa Itti Gaafatamaa *")

        if st.form_submit_button("📄 PDF UUMI"):
            if maqaa and kaartaa and head:
                st.session_state.pdf_bytes = create_clearance_pdf({
                    "maqaa": maqaa,
                    "araddaa": araddaa,
                    "qaxana": qaxana,
                    "kaartaa": kaartaa,
                    "bara": bara,
                    "dhimma": dhimma,
                    "head": head
                })
                st.session_state.pdf_name = f"Clearance_{maqaa}.pdf"
                st.success("PDF qophaa'eera")

    if st.session_state.pdf_bytes:
        st.download_button(
            "⬇️ PDF Buusi",
            st.session_state.pdf_bytes,
            file_name=st.session_state.pdf_name,
            mime="application/pdf"
        )

# -------- TAB 2 --------
with tab2:
    df = load_data()

    if st.button("📊 Daily Excel → Telegram"):
        res = create_excel_report(df,"daily")
        if res:
            send_excel_to_telegram(*res,"📊 Gabaasa Guyyaa")
            st.success("Ergameera")
        else:
            st.warning("Ragaan hin jiru")

    if st.button("📈 Monthly Excel → Telegram"):
        res = create_excel_report(df,"monthly")
        if res:
            send_excel_to_telegram(*res,"📈 Gabaasa Ji'aa")
            st.success("Ergameera")
        else:
            st.warning("Ragaan hin jiru")

    st.dataframe(df)




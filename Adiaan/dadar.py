import streamlit as st
import pandas as pd
import sqlite3
import os, io, requests
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter
import plotly.express as px

# ================= CONFIG =================
st.set_page_config("Dadar Land Admin", "🏢", layout="wide")
DB_FILE = "dadar_land.db"
NAGAHEE_DIR = "nagahee_scan"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)


st.set_page_config(page_title="Dadar Land System", page_icon="🏢", layout="wide")

# CSS Styling
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {background-color: #f4f7f9;}
div.stForm {background: white; border-radius: 12px; padding: 20px; border: 1px solid #ddd;}
.card {background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center;}
</style>
""", unsafe_allow_html=True)

# ================== DATA & SERVICES ==================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"],
    "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa", "Kaartaa Lafa Qoonnaa"],
    "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandummaa"],
    "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"],
    "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"],
    "⚖️ Adabbii & Seeressuu": ["Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", "Adabbii Faallaa Pilaanii"]
}

# ================== FUNCTIONS ==================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    df['Guyyaa'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y')
    df['Waggaa'] = df['Guyyaa'].dt.year
    df['Ji_a'] = df['Guyyaa'].dt.month
    df['Torbee'] = df['Guyyaa'].dt.isocalendar().week
    return df

def save_data(df):
    df[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_certificate(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 100, 0)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)

    # Logos
    if logo_left: pdf.image(logo_left, 20, 15, 30)
    if logo_right: pdf.image(logo_right, 230, 15, 30)

    pdf.set_y(50)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 20, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", align='C')
    pdf.line(40, 180, 100, 180)
    pdf.set_xy(40, 182)
    pdf.cell(60, 10, "Itti Gaafatamaa", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================== SESSION ==================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = None

# ================== LOGIN ==================
if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()
        elif u == "ogeessa" and p == "1234":
            st.session_state.logged_in = True
            st.session_state.role = "user"
            st.rerun()
        else:
            st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    if st.session_state.role == "admin":
        menu_options = ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa", "🔍 Barbaadi/Edit"]
    else:
        menu_options = ["📝 Galmee Haaraa", "🔍 Barbaadi/Edit"]

    menu = st.sidebar.radio("FILANNOO", menu_options)
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    # ================== REGISTRATION ==================
    if menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Gurgurtaa & Tajaajila")
        selected_cats = st.multiselect("Ramaddii Tajaajilaa:", list(SERVICE_STRUCTURE.keys()))
        final_services = []
        total_fee = 0

        if selected_cats:
            cols = st.columns(len(selected_cats))
            for i, cat in enumerate(selected_cats):
                with cols[i]:
                    st.write(cat)
                    subs = st.multiselect(f"Tajaajiloota {cat}:", SERVICE_STRUCTURE[cat], key=cat)
                    for s in subs:
                        fee = st.number_input(f"Kaffaltii {s}:", min_value=0.0, key=f"fee_{s}")
                        final_services.append(s)
                        total_fee += fee

        st.divider()
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Ogeessa Raawwate")
            nagahee = st.file_uploader("Nagahee Scan (Image)", type=['jpg','png','jpeg'])

            if st.form_submit_button("💾 Galmeessi"):
                if name and final_services:
                    if nagahee:
                        f_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                        with open(f_path, "wb") as f: f.write(nagahee.getbuffer())
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_services), ogeessa, total_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Waliigala: {total_fee} ETB")
                else:
                    st.error("Maaloo odeeffannoo guutuu galchi!")

    # ================== DASHBOARD ==================
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Maamiltootaa", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            st.subheader("Trendii Kaffaltii")
            fig = px.bar(df, x='Guyyaa', y='Kafaltii_Taj', color='Maqaa_Ogeessa')
            st.plotly_chart(fig, use_container_width=True)

    # ================== CERTIFICATES ==================
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Sartiifiikeeta Ogeeyyii Cimaa")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            medals = ["🥇 1FFAA", "🥈 2FFAA", "🥉 3FFAA"]
            with st.form("logo_upload_form"):
                logo_bita = st.file_uploader("Upload Logo Bita (Left)", type=["png","jpg","jpeg"])
                logo_mirga = st.file_uploader("Upload Logo Mirga (Right)", type=["png","jpg","jpeg"])
                submit_logos = st.form_submit_button("✅ Upload Logos")
            if submit_logos:
                cols = st.columns(3)
                for i, (name, count) in enumerate(top_3.items()):
                    with cols[i]:
                        st.markdown(f"<div class='card'><h2>{medals[i]}</h2><h3>{name}</h3><p>Abbootii Dhimmaa: {count}</p></div>", unsafe_allow_html=True)
                        pdf_bytes = create_certificate(name, count, i+1, logo_bita, logo_mirga)
                        safe_name = name.replace(" ", "_")
                        st.download_button(f"📥 Download {name} PDF", pdf_bytes, f"Certificate_{safe_name}.pdf", mime="application/pdf")

    # ================== SEARCH/EDIT ==================
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi / Edit Galmee")
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if res.empty: st.info("Ragaan hin argamne.")
            else:
                for idx, row in res.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                        st.write(f"Araddaa: {row['Araddaa']}")
                        st.write(f"Qaxana: {row['Qaxana']}")
                        st.write(f"Tajaajila: {row['Gosa_Tajajjilaa']}")
                        st.write(f"Ogeessa: {row['Maqaa_Ogeessa']}")
                        st.write(f"Kafaltii: {row['Kafaltii_Taj']}")
                        if st.session_state.role == 'admin':
                            if st.button("🗑 Haqi", key=f"del_{idx}"):
                                df = df.drop(idx)
                                save_data(df)
                                st.success(f"{row['Maqaa_Abbaa_Dhimmaa']} haqameera")
                                st.experimental_rerun()


SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": ["Gibira Baaxii", "Gibira Qonnaa", "Kaffaltii Liizii Waggaa"],
    "📂 Tajaajila Biroo": ["Clearance PDF", "Deebii Iyyannoo"]
}

COL_NAMES = ['id','guyyaa','maqaa','araddaa','qaxana','gosa_taj','ogeessa','kafaltii','nagahee_path']

# ================= HELPERS =================
def get_ec_date(g=None):
    if g is None: g=datetime.now()
    ec = EthiopianDateConverter.to_ethiopian(g.year,g.month,g.day)
    return f"{ec.day:02d}/{ec.month:02d}/{ec.year}"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS galmee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guyyaa TEXT, maqaa TEXT, araddaa TEXT, qaxana TEXT,
            gosa_taj TEXT, ogeessa TEXT, kafaltii REAL, nagahee_path TEXT
        )
    """)
    conn.commit()
    return conn

def load_data():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM galmee", conn)
    conn.close()
    return df

def save_row(row):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO galmee
        (guyyaa, maqaa, araddaa, qaxana, gosa_taj, ogeessa, kafaltii, nagahee_path)
        VALUES (?,?,?,?,?,?,?,?)
    """, row)
    conn.commit(); conn.close()

def create_clearance_pdf(data):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Times", size=12)
    pdf.cell(0,10,"MOOTUMMAA NAANNOO OROMIYAA",ln=True,align="C")
    pdf.cell(0,10,"BULCHIINSA MAGAALAA DADAR - WAAJJIRA LAFAA",ln=True,align="C")
    pdf.ln(10)
    pdf.multi_cell(0,8,
        f"Maqaa: {data['maqaa']}\n"
        f"Araddaa: {data['araddaa']}  Qaxana: {data['qaxana']}\n"
        f"Dhimma: {data['dhimma']}\n"
        f"Itti Gaafatamaa: {data['head']}\n"
        f"Guyyaa: {get_ec_date()}"
    )
    return pdf.output(dest="S").encode("latin-1")

def create_excel_report(df, mode):
    df['Date'] = pd.to_datetime(df['guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['EC_Date'] = df['Date'].apply(get_ec_date)
    if mode=="daily":
        df=df[df['Date'].dt.date==datetime.now().date()]; fname="Daily_Report.xlsx"
    else:
        df=df[(df['Date'].dt.month==datetime.now().month)&(df['Date'].dt.year==datetime.now().year)]; fname="Monthly_Report.xlsx"
    if df.empty: return None
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer: df.to_excel(writer, index=False)
    out.seek(0); return out,fname

def send_excel_to_telegram(file_bytes, filename, caption):
    url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    requests.post(url, files={"document":(filename,file_bytes)}, data={"chat_id":CHAT_ID_MANAGER,"caption":caption})

# ================= SESSION =================
if 'logged' not in st.session_state: st.session_state.logged=False
if 'pdf_bytes' not in st.session_state: st.session_state.pdf_bytes=None
if 'pdf_name' not in st.session_state: st.session_state.pdf_name=""

# ================= LOGIN =================
if not st.session_state.logged:
    st.title("🔐 Login")
    u = st.text_input("Username"); p=st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u=="admin" and p=="2026": st.session_state.logged=True; st.rerun()
        elif u=="staff" and p=="2026": st.session_state.logged=True; st.session_state.staff=True; st.rerun()
        else: st.error("Dogoggora login")

# ================= MAIN =================
else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard","📝 Galmee Haaraa","📄 Clearance","📤 Telegram Report"])


# ---------- DASHBOARD ----------
    if menu=="📊 Dashboard":
        st.header("📊 Dashboard")
        if df.empty: st.info("Ragaan hin jiru")
        else:
            c1,c2,c3=st.columns(3)
            c1.metric("💰 Galii",f"{df['kafaltii'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota",len(df))
            c3.metric("👷 Ogeeyyii",df['ogeessa'].nunique())
            fig=px.bar(df.groupby("ogeessa")['kafaltii'].sum().reset_index(),x="ogeessa",y="kafaltii")
            st.plotly_chart(fig,use_container_width=True)

    # ---------- GALMEE HAARAA ----------
    elif menu=="📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        with st.form("reg_form"):
            c1,c2=st.columns(2)
            maqaa=c1.text_input("Maqaa"); araddaa=c2.text_input("Araddaa")
            qaxana=c1.text_input("Qaxana"); ogeessa=c2.text_input("Ogeessa Raawwate")
            services=st.multiselect("Tajaajila", sum(SERVICE_STRUCTURE.values(),[]))
            kafaltii=st.number_input("Kafaltii (ETB)", min_value=0.0)
            nagahee=st.file_uploader("Nagahee Scan (JPG/PNG)",type=["jpg","png"])
            if st.form_submit_button("💾 Galmeessi"):
                path=""; 
                if nagahee: path=os.path.join(NAGAHEE_DIR,f"{maqaa}_{datetime.now().strftime('%H%M%S')}.jpg"); open(path,"wb").write(nagahee.getbuffer())
                save_row([datetime.now().strftime('%d/%m/%Y'),maqaa,araddaa,qaxana,",".join(services),ogeessa,kafaltii,path])
                st.success("✅ Galmeeffameera!"); st.balloons()

    # ---------- CLEARANCE ----------
    elif menu=="📄 Clearance":
        st.header("📄 Clearance PDF")
        with st.form("clr_form"):
            maqaa=st.text_input("Maqaa Maamilaa"); araddaa=st.text_input("Araddaa"); qaxana=st.text_input("Qaxana")
            dhimma=st.text_input("Dhimma"); head=st.text_input("Itti Gaafatamaa")
            if st.form_submit_button("PDF UUMI"):
                st.session_state.pdf_bytes=create_clearance_pdf({"maqaa":maqaa,"araddaa":araddaa,"qaxana":qaxana,"dhimma":dhimma,"head":head})
                st.session_state.pdf_name=f"Clearance_{maqaa}.pdf"
                st.success("PDF qophaa'eera")
        if st.session_state.pdf_bytes:
            st.download_button("⬇️ PDF Buusi", st.session_state.pdf_bytes, st.session_state.pdf_name, mime="application/pdf")

    # ---------- TELEGRAM ----------
    elif menu=="📤 Telegram Report":
        st.header("📤 Telegram Reports")
        if st.button("📊 Daily Excel → Telegram"):
            res=create_excel_report(df,"daily")
            if res: send_excel_to_telegram(*res,"Daily Report"); st.success("Ergameera")
            else: st.warning("Ragaan hin jiru")
        if st.button("📈 Monthly Excel → Telegram"):
            res=create_excel_report(df,"monthly")
            if res: send_excel_to_telegram(*res,"Monthly Report"); st.success("Ergameera")
            else: st.warning("Ragaan hin jiru")

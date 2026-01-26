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
            else: st.warning("Ragaan hin jiru")    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
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

# ================= 3. PDF GENERATOR (GOLD METAL EDITION) =================
def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    # Orientation 'L' (Landscape), A4
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluuwwan Gold Metal fi Background Bareedaa
    gold_metal = (255, 215, 0)      # Bright Gold Metal
    deep_green = (0, 60, 0)        # Deep Magariisa
    bg_color = (255, 254, 245)     # Cream/Soft Gold Background

    # --- 1. Background fi Border (Double Design) ---
    pdf.set_fill_color(*bg_color)
    pdf.rect(10, 10, 277, 190, 'F')
    
    # Border alaa (Magariisa)
    pdf.set_draw_color(*deep_green) 
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    
    # Border keessaa (Gold Metal)
    pdf.set_draw_color(*gold_metal)
    pdf.set_line_width(1.5)
    pdf.rect(13, 13, 271, 184)

    # --- 2. Logo Management ---
    if logo_left:
        ext_l = logo_left.name.split('.')[-1].lower()
        temp_l = f"temp_l.{ext_l}"
        with open(temp_l, "wb") as f: f.write(logo_left.getbuffer())
        pdf.image(temp_l, x=22, y=18, w=40)

if logo_right:
        ext_r = logo_right.name.split('.')[-1].lower()
        temp_r = f"temp_r.{ext_r}"
        with open(temp_r, "wb") as f: f.write(logo_right.getbuffer())
        pdf.image(temp_r, x=235, y=18, w=40)

    # --- 3. Mata Duree Gurguddaa ---
    pdf.set_y(35)
    pdf.set_text_color(*gold_metal)
    pdf.set_font('Arial', 'B', 42) # Size baay'ee guddaa
    pdf.cell(0, 22, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 12, "CERTIFICATE OF RECOGNITION", ln=True, align='C')
    
    # Sarara Bareechituu Gidduu
    pdf.set_draw_color(*gold_metal)
    pdf.line(90, 72, 207, 72)

    pdf.set_y(78)
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.set_font('Arial', 'I', 13)
    pdf.cell(0, 7, "Dedar City Administration Land Office", ln=True, align='C')

    # --- 4. Maqaa Ogeessaa (GOLD METAL LOOK) ---
    pdf.set_y(105)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font('Arial', 'I', 15)
    pdf.cell(0, 10, "Sartiifiketiin kun kabajaan kan kennameef / Proudly presented to:", ln=True, align='C')
    
    # Maqaa (Size guddaa fi Halluu Magariisa calaqqisu)
    pdf.ln(5)
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 38) # Size 38 (Baay'ee ifa)
    pdf.cell(0, 25, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    # Jechoota Galataa
    pdf.ln(5)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font('Arial', '', 14)
    msg_oromoo = "Waggaa 2026 keessatti tajaajila saffisaa, qulqulluu fi amannamaa ta'een tajaajila hawaasaa irratti gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru."
    msg_english = "In deep appreciation for your outstanding dedication and exceptional service delivery throughout the year 2026."
    
    pdf.multi_cell(0, 8, msg_oromoo, align='C')
    pdf.set_font('Arial', 'I', 12)
    pdf.multi_cell(0, 7, msg_english, align='C')

    # --- 5. Bakka Mallattoo fi Guyyaa (Signature Section) ---
    pdf.set_y(172) # Gara jalaatti siqee jira
    curr_y = pdf.get_y()
    
    pdf.set_draw_color(*deep_green)
    pdf.set_line_width(0.7)
    
    # Bitaa: Mallattoo
    pdf.line(40, curr_y, 115, curr_y)
    pdf.set_xy(40, curr_y + 2)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(*deep_green)
    pdf.cell(75, 6, "Mallattoo Itti Gaafatamaa", ln=True, align='C')
    pdf.set_x(40)
    pdf.set_font('Arial', '', 10)
    pdf.cell(75, 5, "Authorized Signature & Seal", align='C')

    # Mirga: Guyyaa
    pdf.line(180, curr_y, 255, curr_y)
    pdf.set_xy(180, curr_y + 2)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(75, 6, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.set_x(180)
    pdf.set_font('Arial', '', 10)
    pdf.cell(75, 5, "Dedar, Oromia", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
            else: st.error("Username ykn Password dogoggora!")
else:
    df = load_data()
    
    with st.sidebar:
        st.title("Dadar Admin")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

# --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h4>💰 Galii Waliigalaa</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Tajaajilamtoota</h4><h2>{len(df)}</h2><p>Walitti qabaa</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Hojii irra jiran</p></div>", unsafe_allow_html=True)
            st.divider()
            st.subheader("📈 Raawwii Galii Ji'aan")
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else:
            st.info("Data'n galmeeffame hin jiru.")

    # --- GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Haaromsuu"],
            "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
            "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
            "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
        }
        
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")
                    if s == "TOT": is_tot = True

        with st.form("entry_form", clear_on_submit=True):
            st.markdown("### 📋 Odeeffannoo Abbaa Dhimmaa")
            if is_tot:
                col1, col2 = st.columns(2)
                maqaa_f = f"G: {col1.text_input('Maqaa Gurguraa')} / B: {col2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {col1.text_input('Araddaa G')} / B: {col2.text_input('Araddaa B')}"
                qax_f = f"G: {col1.text_input('Qaxana G')} / B: {col2.text_input('Qaxana B')}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f = c1.text_input("Maqaa Abbaa Dhimmaa")
                ara_f = c2.text_input("Araddaa")
                qax_f = c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                else: st.error("⚠️ Odeeffannoo guuti!")

# --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Bal'aa")
        if not df.empty:
            f_type = st.sidebar.radio("Calali:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa Murtaa'aa"])
            filtered = df.copy()
            if f_type == "Guyyaa Murtaa'aa":
                sel_date = st.sidebar.date_input("Guyyaa:", datetime.now())
                filtered = df[df['Guyyaa'] == sel_date.strftime('%d/%m/%Y')]
            else:
                sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
                filtered = filtered[filtered['Waggaa'] == sel_y]
                if f_type == "Kurmaana":
                    filtered = filtered[filtered['Kurmaana'] == st.sidebar.selectbox("Kurmaana", [1,2,3,4])]
                elif f_type == "Ji'a":
                    filtered = filtered[filtered['Ji\'a'] == st.sidebar.selectbox("Ji'a", MONTH_ORDER)]
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            total = filtered['Kafaltii_Taj'].sum()
            st.metric("Galii", f"{total:,.2f} ETB")
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel", buf.getvalue(), "Gabaasa.xlsx")
            if c2.button("✈️ Telegram"):
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa Galii: {total} ETB"): st.success("✅ Ergame!")
        else: st.warning("Data'n hin jiru.")

    # --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa & Sartiifiikeeta")
        cl, cr = st.columns(2)
        logo_l = cl.file_uploader("Logo Bitaa Filadhu", type=['png', 'jpg'], key="l_up")
        logo_r = cr.file_uploader("Logo Mirgaa Filadhu", type=['png', 'jpg'], key="r_up")
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h2 style='color:green;'>{i}FFAA</h2><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    try:
                        # Passing uploaded files directly
                        pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                        st.download_button(f"📥 PDF {i}ffaa", pdf_bytes, f"Cert_{name}.pdf", "application/pdf", key=f"btn_{i}")
                    except Exception as e: 
                        st.error(f"PDF Error: {e}")
        else: st.info("Data'n hin jiru.")

    # --- SEARCH/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not results.empty:
                for idx, row in results.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                        new_name = st.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                        new_fee = st.number_input("Kafaltii Sirreessi", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                        c1, c2 = st.columns(2)
                        if c1.button("💾 Update", key=f"u_{idx}"):
                            df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_name
                            df.at[idx, 'Kafaltii_Taj'] = new_fee
                            save_data(df); st.success("Sirreeffameera!"); st.rerun()
                        if c2.button("🗑 Haqi", key=f"d_{idx}"):
                            df = df.drop(idx); save_data(df); st.warning("Haqumeera!"); st.rerun()
            else: st.error("Maqaan kun hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun() = st.columns(2)
                maqaa_f = f"G: {col1.text_input('Maqaa Gurguraa')} / B: {col2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {col1.text_input('Araddaa G')} / B: {col2.text_input('Araddaa B')}"
                qax_f = f"G: {col1.text_input('Qaxana G')} / B: {col2.text_input('Qaxana B')}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f = c1.text_input("Maqaa Abbaa Dhimmaa")
                ara_f = c2.text_input("Araddaa")
                qax_f = c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                else: st.error("⚠️ Odeeffannoo guuti!")

# --- GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Bal'aa")
        if not df.empty:
            f_type = st.sidebar.radio("Calali:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa Murtaa'aa"])
            filtered = df.copy()
            if f_type == "Guyyaa Murtaa'aa":
                sel_date = st.sidebar.date_input("Guyyaa:", datetime.now())
                filtered = df[df['Guyyaa'] == sel_date.strftime('%d/%m/%Y')]
            else:
                sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
                filtered = filtered[filtered['Waggaa'] == sel_y]
                if f_type == "Kurmaana":
                    filtered = filtered[filtered['Kurmaana'] == st.sidebar.selectbox("Kurmaana", [1,2,3,4])]
                elif f_type == "Ji'a":
                    filtered = filtered[filtered['Ji\'a'] == st.sidebar.selectbox("Ji'a", MONTH_ORDER)]
            
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            total = filtered['Kafaltii_Taj'].sum()
            st.metric("Galii", f"{total:,.2f} ETB")
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel", buf.getvalue(), "Gabaasa.xlsx")
            if c2.button("✈️ Telegram"):
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa Galii: {total} ETB"): st.success("✅ Ergame!")
        else: st.warning("Data'n hin jiru.")

    # --- BADHAASA OGEEYYII ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa & Sartiifiikeeta")
        cl, cr = st.columns(2)
        logo_l = cl.file_uploader("Logo Bitaa Filadhu", type=['png', 'jpg'], key="l_up")
        logo_r = cr.file_uploader("Logo Mirgaa Filadhu", type=['png', 'jpg'], key="r_up")
        
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h2 style='color:green;'>{i}FFAA</h2><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    try:
                        # Passing uploaded files directly
                        pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                        st.download_button(f"📥 PDF {i}ffaa", pdf_bytes, f"Cert_{name}.pdf", "application/pdf", key=f"btn_{i}")
                    except Exception as e: 
                        st.error(f"PDF Error: {e}")
        else: st.info("Data'n hin jiru.")

    # --- SEARCH/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not results.empty:
                for idx, row in results.iterrows():
                    with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                        new_name = st.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                        new_fee = st.number_input("Kafaltii Sirreessi", float(row['Kafaltii_Taj']), key=f"f_{idx}")
                        c1, c2 = st.columns(2)
                        if c1.button("💾 Update", key=f"u_{idx}"):
                            df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_name
                            df.at[idx, 'Kafaltii_Taj'] = new_fee
                            save_data(df); st.success("Sirreeffameera!"); st.rerun()
                        if c2.button("🗑 Haqi", key=f"d_{idx}"):
                            df = df.drop(idx); save_data(df); st.warning("Haqumeera!"); st.rerun()
            else: st.error("Maqaan kun hin jiru.")

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()    r, g, b = rank_colors.get(rank, (27, 94, 32))

    # Background & Borders
    pdf.set_fill_color(245, 255, 245); pdf.rect(12, 12, 273, 186, 'F')
    pdf.set_line_width(4); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)

    # Dual Logos - Size Fixed at 35mm for balance
    logo_size = 35
    if logo_left:
        left_p = "left_temp.png"; Image.open(logo_left).save(left_p)
        pdf.image(left_p, x=22, y=20, w=logo_size)
    if logo_right:
        right_p = "right_temp.png"; Image.open(logo_right).save(right_p)
        pdf.image(right_p, x=240, y=20, w=logo_size)

    # Content
    pdf.set_y(45); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_text_color(30, 70, 30); pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(15); pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    pdf.ln(5); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 32)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    pdf.ln(10); pdf.set_text_color(40, 40, 40); pdf.set_font('Arial', '', 15)
    msg = (f"Waggaa 2026 keessatti tajaajila saffisaa fi amannamaa ta'een\n"
           f"Abbootii Dhimmaa {count} tajaajiluun beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    
    pdf.ln(20); curr_y = pdf.get_y()
    pdf.line(40, curr_y, 110, curr_y); pdf.set_xy(40, curr_y + 2); pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
    pdf.line(180, curr_y, 250, curr_y); pdf.set_xy(180, curr_y + 2); pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 3. DATA LOAD & TELEGRAM =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
    "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Haaromsuu"],
    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
}
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0: return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map({9:"Fulbaana", 10:"Onkololeessa", 11:"Sadaasa", 12:"Muddee", 1:"Amajjii", 2:"Guraandhala", 3:"Bitootessa", 4:"Eebila", 5:"Caamsaa", 6:"Waxabajjii", 7:"Adooleessa", 8:"Hagayya"})
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save): df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def send_to_telegram(file_data, file_name, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {'document': (file_name, file_data)}; data = {'chat_id': CHAT_ID_MANAGER, 'caption': caption}
    try: return requests.post(url, files=files, data=data).status_code == 200
    except: return False

# ================= 4. APP INTERFACE =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center; color:#1b5e20;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
            else: st.error("Dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        st.markdown("### 🏢 DADAR LAND")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Tajaajilamtoota", len(df))
            st.bar_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n hin jiru.")

elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}")
                    if s == "TOT": is_tot = True
        with st.form("entry", clear_on_submit=True):
            if is_tot:
                col1, col2 = st.columns(2)
                maqaa_f = f"G: {col1.text_input('M Gurguraa')} / B: {col2.text_input('M Bitataa')}"
                ara_f = f"G: {col1.text_input('Araddaa G')} / B: {col2.text_input('Araddaa B')}"
                qax_f = f"G: {col1.text_input('Qaxana G')} / B: {col2.text_input('Qaxana B')}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f, ara_f, qax_f = c1.text_input("Maqaa"), c2.text_input("Araddaa"), c1.text_input("Qaxana")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa & Sartiifiikeeta")
        cl, cr = st.columns(2)
        logo_l = cl.file_uploader("Logo Bitaa (Mootummaa)", type=['png', 'jpg'])
        logo_r = cr.file_uploader("Logo Mirgaa (Waajjira)", type=['png', 'jpg'])
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='card'><h3>{i}FFAA</h3><h4>{name}</h4><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                    st.download_button(f"📥 PDF {i}ffaa", pdf_bytes, f"Cert_{name}.pdf", "application/pdf")

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Calalame")
        if not df.empty:
            f_type = st.sidebar.radio("Calali:", ["Waggaa", "Kurmaana", "Ji'a"])
            sel_y = st.sidebar.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
            filtered = df[df['Waggaa'] == sel_y]
            if f_type == "Kurmaana": filtered = filtered[filtered['Kurmaana'] == st.sidebar.selectbox("Kurmaana", [1,2,3,4])]
            elif f_type == "Ji'a": filtered = filtered[filtered['Ji\'a'] == st.sidebar.selectbox("Ji'a", MONTH_ORDER)]
            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            t_f = filtered['Kafaltii_Taj'].sum()
            st.metric("Galii", f"{t_f:,.2f} ETB")
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: filtered[COL_NAMES].to_excel(wr, index=False)
            if st.button("✈️ Telegram-itti Ergi"):
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa {f_type}: {t_f} ETB"): st.success("✅ Ergameera!")

    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi ykn Haqi")
        q = st.text_input("Maqaa barreessi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    if st.button("🗑 Haqi", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    elif menu == "Ba'i": st.session_state.logged_in = False; st.rerun()    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF GENERATOR (DUAL LOGO) =================
class CertificatePDF(FPDF):
    def header(self): pass
    def footer(self): pass

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = CertificatePDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Colors based on rank
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    # 1. Background Light Green
    pdf.set_fill_color(245, 255, 245) 
    pdf.rect(12, 12, 273, 186, 'F')

    # 2. Borders
    pdf.set_line_width(4); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(1); pdf.rect(14, 14, 269, 182)

    # 3. Dual Logos (Size Fixed at 35mm)
    logo_size = 35
    if logo_left:
        left_p = "left_temp.png"
        Image.open(logo_left).save(left_p)
        pdf.image(left_p, x=22, y=20, w=logo_size)
    if logo_right:
        right_p = "right_temp.png"
        Image.open(logo_right).save(right_p)
        pdf.image(right_p, x=240, y=20, w=logo_size)

    # 4. Content
    pdf.set_y(40); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_text_color(30, 70, 30); pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(15); pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    
    pdf.ln(5); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 32)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_text_color(40, 40, 40); pdf.set_font('Arial', '', 15)
    msg = (f"Waggaa 2026 keessatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een\n"
           f"Abbootii Dhimmaa {count} tajaajiluun bu'aa qabeessa ta'anii waan argamaniif\n"
           f"beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')

    # 5. Signatures
    pdf.ln(25); curr_y = pdf.get_y()
    pdf.set_draw_color(0, 0, 0); pdf.line(40, curr_y, 110, curr_y)
    pdf.set_xy(40, curr_y + 2); pdf.cell(70, 10, "Itti Gaafatamaa Waajjiraa", align='C')
    pdf.line(180, curr_y, 250, curr_y)
    pdf.set_xy(180, curr_y + 2); pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN INTERFACE =================
df = load_data()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=100)
    st.title("DADAR LAND")
    menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])

if menu == "📊 Dashboard":
    st.header("📊 Dashboard Gabaasaa")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Tajaajilamtoota", len(df))
        c3.metric("Ogeeyyii", len(df['Maqaa_Ogeessa'].unique()))
        st.line_chart(df.groupby('Guyyaa')['Kafaltii_Taj'].sum())
    else: st.info("Data'n galmeeffame hin jiru.")

elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa Haaraa")
    with st.form("galmee_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_abbaa = c1.text_input("Maqaa Abbaa Dhimmaa")
        ogeessa = c2.text_input("Maqaa Ogeessaa")
        araddaa = c1.text_input("Araddaa")
        qaxana = c2.text_input("Qaxana")
        gosa = st.selectbox("Gosa Tajaajilaa", ["Kaartaa", "Gibira", "Liizii", "Ittii Fayyaddam"])
        kafaltii = st.number_input("Kafaltii (ETB)", min_value=0.0)
        if st.form_submit_button("💾 Galmeessi"):
            new_row = [datetime.now().strftime('%d/%m/%Y'), m_abbaa, araddaa, qaxana, gosa, ogeessa, kafaltii]
            df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
            save_data(df); st.success("Galmee Keessan Milkaa'inaan Ol-ka'eera!")

elif menu == "📈 Gabaasa Bal'aa":
    st.header("📈 Gabaasa Tajaajilaa")
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Gabaasa CSV Buufadhu", df.to_csv(index=False).encode('utf-8'), "gabaasa_dadar.csv", "text/csv")

elif menu == "🏆 Badhaasa Ogeeyyii":
    st.header("🏆 Badhaasa & Sartiifiikeeta")
    col_l, col_r = st.columns(2)
    logo_l = col_l.file_uploader("Logo Bitaa (Government)", type=['png', 'jpg'])
    logo_r = col_r.file_uploader("Logo Mirgaa (Office)", type=['png', 'jpg'])
    
    if not df.empty:
        top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        cols = st.columns(3)
        for i, (name, count) in enumerate(top_3.items(), 1):
            with cols[i-1]:
                st.markdown(f"<div class='card'><h3>{i}FFAA</h3><h4>{name}</h4><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                st.download_button(f"📥 Buufadhu PDF {i}", pdf_bytes, f"Sartifiketa_{name}.pdf", "application/pdf")

elif menu == "🔍 Barbaadi/Edit":
    st.header("🔍 Barbaadi ykn Edit Godhi")
    search_q = st.text_input("Maqaa Barbaadi...")
    if search_q:
        res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search_q, case=False, na=False)]
        st.dataframe(res)
        if not res.empty:
            if st.button("🗑 Haqama (Hunda Filtarii)"):
                df = df[~df['Maqaa_Abbaa_Dhimmaa'].str.contains(search_q, case=False, na=False)]
                save_data(df); st.rerun()    "Dhimma Dangaa": ["Kafaltii Humna Mandisaa"],
    "Dhimma Mana Murtii": ["Ugura Mana Murtii", "Uguraa Mana Murtii Kaasuu"],
    "Liqii Bankii": ["Dorkka Liqii Bankii", "Dorkkaa Liqii Bankii Kaasuu"]
}

MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
WEEKDAY_MAP = {0: "Wixata", 1: "Filatama", 2: "Roobii", 3: "Kamisa", 4: "Jimmata", 5: "Sanbata", 6: "Dilbata"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Torbee'] = (df['Date_Obj'].dt.day - 1) // 7 + 1
    df['Guyyaa_Torbee'] = df['Date_Obj'].dt.dayofweek.map(WEEKDAY_MAP)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF CERTIFICATE ENGINE =================
def create_pdf_cert(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluuwwan: 1st=Gold, 2nd=Silver, 3rd=Bronze
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    rank_text = {1: "1FFAA (GOLD)", 2: "2FFAA (SILVER)", 3: "3FFAA (BRONZE)"}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    # Border
    pdf.set_line_width(5); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(1); pdf.rect(15, 15, 267, 180)

# Content
    pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 40, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_text_color(40, 40, 40); pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(15); pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    
    pdf.ln(5); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_text_color(60, 60, 60); pdf.set_font('Arial', '', 15)
    msg = (f"Waggaa 2026 keessatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een\n"
           f"Abbootii Dhimmaa {count} tajaajiluun bu'aa qabeessa ta'anii waan argamaniif\n"
           f"beekamtii {rank_text[rank]} kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')

    pdf.ln(25); curr_y = pdf.get_y()
    pdf.set_draw_color(0, 0, 0); pdf.line(40, curr_y, 110, curr_y)
    pdf.set_xy(40, curr_y + 2); pdf.cell(70, 10, "Itti Gaafatamaa Waajjiraa", align='C')
    pdf.line(180, curr_y, 250, curr_y)
    pdf.set_xy(180, curr_y + 2); pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123": st.session_state.logged_in = True; st.rerun()
else:
    df = load_data()
    with st.sidebar:
        st.markdown("### 🏢 DADAR LAND")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "Ba'i"])

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("Tajaajilamtoota", len(df))
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))

    # --- 2. GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        selected_main = st.multiselect("Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Filannoo {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}")
        
        with st.form("entry", clear_on_submit=True):
            c1, c2 = st.columns(2)
            maqaa_f, ara_f = c1.text_input("Maqaa Abbaa Dhimmaa"), c2.text_input("Araddaa")
            qax_f, ogeessa = c1.text_input("Qaxana"), c2.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa_f and details:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("Galmeeffameera!")

# --- 3. GABAASA & CALALII ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa & Calaltuu")
        if not df.empty:
            with st.sidebar:
                st.markdown("---")
                f_type = st.radio("Filtarii:", ["Waggaa", "Kurmaana", "Ji'a", "Torbee", "Guyyaa"])
                sel_y = st.selectbox("Waggaa", sorted(df['Waggaa'].dropna().unique(), reverse=True))
                filtered = df[df['Waggaa'] == sel_y]
                if f_type == "Kurmaana": filtered = filtered[filtered['Kurmaana'] == st.selectbox("Q", [1,2,3,4])]
                elif f_type == "Ji'a": filtered = filtered[filtered['Ji\'a'] == st.selectbox("Ji'a", MONTH_ORDER)]
                elif f_type == "Torbee":
                    sel_m, sel_w = st.selectbox("Ji'a", MONTH_ORDER), st.selectbox("Torbee", [1,2,3,4])
                    filtered = filtered[(filtered['Ji\'a'] == sel_m) & (filtered['Torbee'] == sel_w)]
                elif f_type == "Guyyaa": filtered = filtered[filtered['Guyyaa_Torbee'] == st.selectbox("Guyyaa", list(WEEKDAY_MAP.values()))]

            st.dataframe(filtered[COL_NAMES], use_container_width=True)
            st.metric("Galii Filtarii", f"{filtered['Kafaltii_Taj'].sum():,.2f} ETB")

    # --- 4. BADHAASA OGEEYYII (PDF) ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sartiifiikeeta Ogeeyyii Cimaa")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            medals = ["🥇 1FFAA", "🥈 2FFAA", "🥉 3FFAA"]
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2>{medals[i]}</h2><h3>{name}</h3><p>Abbootii Dhimmaa: {count}</p></div>", unsafe_allow_html=True)
                    pdf_data = create_pdf_cert(name, count, i+1)
                    st.download_button(f"📥 Download PDF {i+1}", pdf_data, f"Cert_{name}.pdf", "application/pdf")
        else: st.warning("Data'n hin jiru.")

    # --- 5. SEARCH / EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    if st.button("🗑 Haqi", key=f"del_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    elif menu == "Ba'i": st.session_state.logged_in = False; st.rerun()






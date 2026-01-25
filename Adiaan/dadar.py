import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= 1. CONFIG & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

LOGO_PATH = "logo.png" 

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA & SETTINGS =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Yeroo', 'Maqaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii_Taj']

MONTHS_OR = {
    "01": "Fulbaana", "02": "Onkololeessa", "03": "Sadaasa", "04": "Muddee",
    "05": "Amajjii", "06": "Guraandhala", "07": "Bitootessa", "08": "Eebila",
    "09": "Caamsaa", "10": "Waxabajjii", "11": "Adooleessa", "12": "Hagayya", "13": "Qaammee"
}

# Gatiiwwan Ati Kennite
GATII_DICT = {
    "Ittii Fayyaddam": 50.0, 
    "Kaartaa mana": 150.0, 
    "kartaa Kadastaara": 150.0, 
    "Kaartaa lafa qonna magaalaa": 150.0, 
    "Jijjirra Maqaa": 200.0,
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

# ================= 4. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🔍 Barbaadi", "Ba'i"])

    df = load_data()

    if menu == "📝 Galmee Haaraa":
        st.markdown("<h2 style='color: #2e7d32;'>📝 Galmee Tajaajilaa</h2>", unsafe_allow_html=True)
        
        # Dabarsa Lafa fi Gibira dabalatee listii filannoo
        options = ["Dabarsa Lafa", "Gibira"] + list(GATII_DICT.keys()) + ["Kan Biroo"]
        gosa_main = st.selectbox("Gosa Tajaajilaa Filadhu fi Mata Duree Galii ", options)
        
        base_fee = 0.0
        gosa_galmeeffamu = gosa_main

        # --- LOGIC DABARSA LAFA ---
        if gosa_main == "Dabarsa Lafa":
            sub_gosa = st.radio("Dabarsa Lafa Keessaa:", ["Liizii waggaa", "Jijjirraa Maqaa", "Lizii Duraa", "TOT"])
            base_fee = 200.0 if sub_gosa == "Jijjirraa Maqaa" else (500.0 if sub_gosa == "Lizii Duraa" else 100.0)
            gosa_galmeeffamu = f"Dabarsa Lafa ({sub_gosa})"

        # --- LOGIC GIBIRA ---
        elif gosa_main == "Gibira":
            c1, c2, c3 = st.columns(3)
            guyyaa = c1.selectbox("Guyyaa", [f"{i:02d}" for i in range(1, 31)])
            ji_lakk = c2.selectbox("Ji'a", list(MONTHS_OR.keys()), format_func=lambda x: f"{x} - {MONTHS_OR[x]}")
            bara = c3.selectbox("Waggaa", [str(y) for y in range(2000, 2025)])
            yeroo_gibiraa = f"{guyyaa}/{ji_lakk}/{bara}"
            base_fee = 100.0
            gosa_galmeeffamu = f"Gibira ({yeroo_gibiraa})"

# --- LOGIC KAN BIROO (SABABAA BIROO) ---
        elif gosa_main == "Kan Biroo":
            sababa_biroo = st.text_input("Sababa tajaajilaa barreessi (Fkn: Kenniinsa Lafa Haaraa)")
            base_fee = st.number_input("Kafaltii tajaajila kanaa (ETB)", min_value=0.0, step=10.0)
            gosa_galmeeffamu = f"Biroo: {sababa_biroo}"

        else:
            base_fee = GATII_DICT.get(gosa_main, 0.0)

        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            maqaa = col1.text_input("Maqaa Abbaa Dhimmaa Fullatti")
            araddaa = col2.text_input("Araddaa")
            qaxana = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            extra = st.number_input("Kafaltii Dabalataa (Yoo jiraate)", min_value=0.0)
            
            total_fee = base_fee + extra
            st.markdown(f"<div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #4caf50;'><h2 style='color: #2e7d32; margin: 0;'>💰 {total_fee} ETB</h2></div>", unsafe_allow_html=True)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa and gosa_galmeeffamu:
                    yeroo_ammaa = datetime.now().strftime('%d/%m/%Y')
                    new_row = [yeroo_ammaa, maqaa, araddaa, qaxana, gosa_galmeeffamu, ogeessa, total_fee]
                    df.loc[len(df)] = new_row
                    save_data(df)
                    st.success(f"✅ Galmeeffameera!")
                else: st.error("Maaloo odeeffannoo guuti!")

    elif menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        st.dataframe(df, use_container_width=True)

    elif menu == "Ba'i":
        st.session_state.logged_in = False; st.rerun()        border-top: 5px solid #d4af37; /* Halluu Guldii (Gold) */
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-8px); }
    .metric-card h4 { color: #64748b; margin-bottom: 10px; font-size: 1.1rem; }
    .metric-card h2 { color: #1e3a8a; font-size: 2.2rem; font-weight: 800; }

    /* Login Card */
    .login-card { 
        max-width: 450px; margin: auto; padding: 60px; 
        background: white; border-radius: 30px; 
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15); 
        text-align: center; border: 1px solid #e2e8f0;
    }
    
    /* Buttons - Custom Style */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white; font-weight: bold; border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background: #22c55e; box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4); }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #f1f5f9; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKSHIINIIWWAN (HELPERS) ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except: return dt.strftime("%Y-%m-%d")

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # Border Miidhagaa (Navy & Gold)
    pdf.set_draw_color(30, 58, 138) 
    pdf.set_line_width(4)
    pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(212, 175, 55) # Gold
    pdf.set_line_width(1.5)
    pdf.rect(13, 13, 271, 184)

    if LOGO_PATH: pdf.image(LOGO_PATH, x=133, y=18, w=30)
    
    pdf.ln(45)
    pdf.set_font('Arial', 'B', 36)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 15, 'SARTIFIKETII KABAJAA', ln=True, align='C')
    
    pdf.ln(15)
    pdf.set_font('Arial', '', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Badhaasni kun ogeessa gahumsa qabuuf kenname:', ln=True, align='C')
    
    pdf.ln(8)
    pdf.set_font('Arial', 'B', 32)
    pdf.set_text_color(184, 134, 11) # Gold text
    pdf.cell(0, 20, name.upper(), ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 16)
    content = f"Waggaa {year} keessa tajaajila gaarii fi gahumsa qabuun hojjechuun badhaasa sadarkaa {rank}ffaa waan ta'aniif qophaa'e."
    pdf.multi_cell(0, 10, content, align='C')
    
    pdf.set_xy(180, 170)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(80, 7, "_______________________", ln=True, align='C')
    pdf.set_x(180)
    pdf.cell(80, 7, "Obbo Aqiil Abdujaliil", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SEENSA (AUTHENTICATION) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<br><br><br>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=120)
        st.markdown("<h2 style='color:#22c55e; margin-top:15px;'>Dadar Land Administration Customer Registration System</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#22c55e;'>Maaloo ragaa kee galchuun seeni</p>", unsafe_allow_html=True)
        u = st.text_input("Username", placeholder="Maqaa kee...")
        p = st.text_input("Password", type="password", placeholder="Fungulaa...")
        if st.button("SEENI / LOGIN"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. MAIN UI ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.markdown("<h3 style='text-align:center; color:#22c55e;'>Dadar Land Administration Customer Registration System</h3>", unsafe_allow_html=True)
        st.divider()
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Menu Filadhu", menu)
        st.info(f"📅 Hardha: {to_ethiopian(datetime.now())}")

    # Header section
    st.markdown(f"""
        <div class="header-box">
            <h1 style='margin:0; font-weight:800; font-size:2.8rem;'>Waajjira Lafaa Bulchiinsa Magaalaa Dadar</h1>
            <p style='font-size:1.4rem; opacity:0.9; font-weight:300;'>Sistama Bulchiinsa Ragaa fi Galmee Ammayyaa</p>
        </div>
        """, unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            
            # Metric Cards Miidhagaa
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h4>👥 Abbootii Dhimmaa</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2:
                rev = df.iloc[:, -1].astype(float).sum()
                st.markdown(f'<div class="metric-card"><h4>💰 Galii Waligalaa</h4><h2>{rev:,.0f} <small style="font-size:1rem;">ETB</small></h2></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h4>✅ Status</h4><h2>Active</h2></div>', unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.subheader("🕒 Galmeewwan Dhiyoo")
                st.dataframe(df.tail(10), use_container_width=True)
            with col_r:
                st.subheader("📊 Gosa Tajaajilaa")
                st.bar_chart(df[5].value_counts(), color="#1e3a8a")
        else:
            st.info("Ragaan galmaa'e hin jiru.")

elif choice == "📝 Galmee Haaraa":
        st.markdown("<div style='background:white; padding:40px; border-radius:25px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        st.subheader("📝 Ragaa Abbaa Dhimmaa Galmeessi")
        with st.form("MyForm", clear_on_submit=True):
            cl1, cl2 = st.columns(2)
            with cl1:
                ad = st.text_input("👤 Maqaa Abbaa Dhimmaa")
                ar = st.text_input("📍 Araddaa")
                wi = st.text_input("🏢 Wirtuu")
            with cl2:
                gs = st.selectbox("🛠 Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Gibira"])
                og = st.text_input("👨‍💼 Maqaa Ogeessaa")
                k_wal = st.number_input("💵 Kafaltii Waligalaa", 0.0)
            
            if st.form_submit_button("✅ GALMEE MIRKANEEESSI"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                line = f"{now}|{ad}|{ar}|{wi}|-|{gs}|{og}|-|Hardha|0|0|0|{k_wal}\n"
                with open(DATA_FILE, "a", encoding="utf-8") as f: f.write(line)
                st.success(f"Ragaan '{ad}' milkiin galmaa'eera!")
                st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📄 Gabaasa Gurguddaa", "🎓 Sartifiketii Badhaasaa"])
        
        with tab1:
            st.subheader("Gabaasa Excel Buufadhu")
            if os.path.exists(DATA_FILE):
                df_view = pd.read_csv(DATA_FILE, sep="|", header=None)
                st.dataframe(df_view)
                st.button("🚀 GABAASA TELEGRAM-ITTI ERGI")
        
        with tab2:
            st.subheader("Sartifiketii Miidhagaa Uumi")
            c_name = st.text_input("Maqaa Ogeessaa")
            c_rank = st.selectbox("Sadarkaa Argatan", ["1ffaa", "2ffaa", "3ffaa"])
            c_year = st.text_input("Waggaa (E.C)", "2017")
            if st.button("🎨 SARTIFIKETII GENERATE"):
                if c_name:
                    pdf_out = generate_certificate(c_name, c_rank, c_year)
                    st.download_button("📥 Buufadhu (PDF)", pdf_out, f"{c_name}_Award.pdf")
                    st.balloons()

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()        return f"{eth_day}/{eth_month}/{eth_year} E.C"
    except:
        return f"{day}/{month}/{year} G.C"

def send_sms(phone, message):
    """SMS Gateway kallaattiin akka erguuf (Device ID dabalatee)"""
    try:
        # Lakk bilbilaa sirreessuuf (+251...)
        if phone.startswith('0'):
            phone = "+251" + phone[1:]
        elif not phone.startswith('+'):
            phone = "+251" + phone
            
        payload = {
            'token': SMS_TOKEN,
            'device': DEVICE_ID, # Device ID amma asitti dabalameera
            'to': phone,
            'message': message
        }
        
        # Ergaa POST fayyadamnee ergina
        res = requests.post(SMS_URL, data=payload, timeout=10)
        
        if res.status_code == 200:
            print(f"[✓] SMS gara {phone} tti ergameera.")
            return True
        else:
            print(f"[!] Gateway Error: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"[!] Network Error: {e}")
        return False

def send_telegram_text(message):
    """Ergaa barreeffamaa qofa qondaalaaf erga"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'text': message, 'parse_mode': 'Markdown'}, timeout=20)
    except: pass

def send_telegram_file(file_path, caption=""):
    """Excel ykn PDF Telegram irratti erga"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            requests.post(url, data={'chat_id': CHAT_ID_MANAGER, 'caption': caption}, files={'document': f}, timeout=20)
    except: pass

# --- KUTAA DOOKUMANTIIWWANII ---

def uumi_sartifiketii(ogeessa, rank, waggaa):
    """Sartifiketii PDF ogeessaaf qopheessa"""
    try:
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_draw_color(31, 78, 120); pdf.set_line_width(1.5); pdf.rect(10, 10, 277, 190)
        
        if os.path.exists(LOGO_PATH):
            pdf.image(LOGO_PATH, x=128, y=15, w=40)
            pdf.ln(45)
        else: pdf.ln(25)

        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 10, 'BULCHIINSA MAGAALAA DADAR', ln=True, align='C')
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 8, 'Wajjiira Lafa Bulchiinsa Magaalaa', ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 30); pdf.set_text_color(31, 78, 120)
        pdf.cell(0, 20, 'SARTIFIKETII BADHAASA WAGGAA', ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 16)
        pdf.cell(0, 15, f"Sartifiketiin kun Ogeessa kabajamaa {ogeessa.upper()}f", ln=True, align='C')

txt = (f"tajaajila mamiilaa haala bareedaa fi quubsaa ta'een waggaa {waggaa} "
               f"kennaa turaniif badhaasa {rank} ta'uun qophaa'eef.")
        pdf.set_font('Arial', '', 14); pdf.multi_cell(0, 8, txt, align='C')
        pdf.ln(20)
        
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 8, f"{OFFICE_HEAD}", ln=True, align='C')
        pdf.cell(0, 8, "Itti Gaafatamaa Wajjiraa", ln=True, align='C')
        
        f_name = f"Sartifiketii_{ogeessa.replace(' ', '_')}.pdf"
        pdf.output(f_name)
        return f_name
    except: return None

def uumi_gabaasa_target(filter_type, value, label):
    """Excel uumee Telegram-itti erga"""
    if not os.path.exists(DATA_FILE): return
    
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Gabaasa"
    headers = ["Guyyaa", "Abbaa Dhimmaa", "Araddaa", "Wirtuu", "Gosa Tajaajilaa", "Ogeessa", "Beellama", "Waligala"]
    ws.append(headers)
    
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", start_color="1F4E78")
    
    total_rev, count, ogeessota = 0, 0, []
    with open(DATA_FILE, "r") as f:
        for line in f:
            p = line.strip().split("|")
            if len(p) < 11: continue
            dt = datetime.strptime(p[0], "%Y-%m-%d %H:%M")
            match = (filter_type == "guyyaa" and dt.strftime("%A") == value) or \
                    (filter_type == "jia" and dt.month == value) or \
                    (filter_type == "waggaa" and dt.year == value)
            if match:
                eth_d = guyyaa_itophiyaa(dt.year, dt.month, dt.day)
                ws.append([eth_d, p[1], p[2], p[3], p[5], p[6], p[8], p[10]])
                total_rev += float(p[10]); ogeessota.append(p[6]); count += 1

    if count > 0:
        f_name = f"Gabaasa_{label}.xlsx"
        wb.save(f_name)
        if filter_type == "waggaa":
            top_3 = Counter(ogeessota).most_common(3)
            ranks = ["1ffaa", "2ffaa", "3ffaa"]
            for i, (name, _) in enumerate(top_3):
                sf = uumi_sartifiketii(name, ranks[i], value)
                if sf: send_telegram_file(sf, f"📜 Badhaasa: {name}")
        
        caption = f"📊 {label}\n💰 Galii: {total_rev} ETB\n📑 Galmee: {count}"
        send_telegram_file(f_name, caption)
        print(f"[✓] Gabaasaan ergameera.")

# --- KUTAA HOJII ---

def galmeessi():
    print("\n" + "="*15 + " GALMEE HAARAA " + "="*15)
    ad = input("Maqaa Abbaa Dhimmaa: ")
    ar = input("Araddaa: ")
    wi = input("Wirtuu: ")
    bad = input("Bilbila AD: ")
    gs = input("Gosa Tajaajilaa: ")
    og = input("Maqaa Ogeessaa: ")
    bog = input("Bilbila Ogeessaa: ")
    gb = input("Guyyaa Beellamaa (YYYY-MM-DD): ") or "2026-01-01"
    sb = input("Sa'aatii Beellamaa: ") or "08:00"
    
    k_vals = []
    print("\n--- Kafaltiiwwan ---")
    for kt in ["Kartaa", "Itti Fayyadaama", "Jij_Maqaa", "Lizii_Dura", "TOT", "Gibira", "Kan_Biro"]:
        v = input(f"{kt}: ") or "0"
        try: k_vals.append(float(v))
        except: k_vals.append(0.0)
            
    waligala = sum(k_vals)
    now_s = datetime.now().strftime("%Y-%m-%d %H:%M")
    k_str = "|".join(map(str, k_vals))
    line = f"{now_s}|{ad}|{ar}|{wi}|{bad}|{gs}|{og}|{bog}|{gb} {sb}|{k_str}|{waligala}\n"
    
    with open(DATA_FILE, "a") as f: f.write(line)

    # 1. SMS Abbaa Dhimmaaf
    msg_ad = f"Kabajamaa {ad}, Araddaa {ar}-Wirtuu {wi} irratti tajaajila {gs}af galmeeffamtaniittu. Ogeessi: {og}. Beellama: {gb} {sb}. W/B/L/M/Dadar."
    send_sms(bad, msg_ad)

    # 2. SMS Ogeessaaf
    msg_og = f"Ogeessa {og}, tajaajilli {gs} kan mamiila {ad} (Araddaa: {ar}) isiniif kennameera. Beellama: {gb} {sb}."
    send_sms(bog, msg_og)

    # 3. Telegram Notification
    tel_msg = f"✅ *GALMEE HAARAA*\n👤 AD: {ad}\n📍 Bakka: {ar} | {wi}\n🛠 Tajaajila: {gs}\n💰 Waligala: {waligala} ETB\n🧑‍💼 Ogeessa: {og}\n📅 Beellama: {gb} {sb}"
    send_telegram_text(tel_msg)
    print("\n[✓] Galmeeffameera! SMS fi Notification ergameera.")

# --- NAVIGATION ---



import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import xlsxwriter

# ================= 1. CONFIGURATION & STYLE =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
LOGO_PATH = "Adiaan/logo.png" # Logoon waajjiraa asii dubbisama
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background: #f4f7f6; }
    [data-testid="stSidebar"] { background-color: #0e3020 !important; }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        border-bottom: 5px solid #2e7d32;
        text-align: center;
        transition: transform 0.3s;
    }
    .stat-card:hover { transform: translateY(-5px); }
    
    /* Login Box */
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover { opacity: 0.9; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

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

# ================= 3. PDF CERTIFICATE (PIROFEESHINAL) =================
def create_advanced_pdf(name, count, rank, logo_l=None, logo_r=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border & Background
    gold = (184, 134, 11); green = (0, 70, 0); cream = (255, 255, 245)
    pdf.set_fill_color(*cream); pdf.rect(5, 5, 287, 200, 'F')
    
    # Elegant Double Border
    pdf.set_draw_color(*green); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*gold); pdf.set_line_width(1); pdf.rect(13, 13, 271, 184)
    
    # Logo Placement (Professional)
    if logo_l:
        with open("temp_l.png", "wb") as f: f.write(logo_l.getbuffer())
        pdf.image("temp_l.png", 25, 20, 35)
    elif os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, 25, 20, 35)
        
    if logo_r:
        with open("temp_r.png", "wb") as f: f.write(logo_r.getbuffer())
        pdf.image("temp_r.png", 235, 20, 35)

    # Content
    pdf.set_y(55); pdf.set_font('Arial', 'B', 40); pdf.set_text_color(*green)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_font('Arial', 'B', 16); pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "Bulchiinsa Magaalaa Dadar | Waajjira Lafaa", ln=True, align='C')
    
    pdf.ln(15); pdf.set_font('Arial', 'I', 18); pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa kun kan kennameef:", ln=True, align='C')
    
    pdf.set_font('Arial', 'B', 32); pdf.set_text_color(*gold)
    pdf.cell(0, 25, name.upper(), ln=True, align='C')
    
    pdf.set_font('Arial', '', 15); pdf.set_text_color(0, 0, 0)
    msg = f"Waggaa 2026 keessatti tajaajila saffisaa, qulqulluu fi amanamummaa qabuun tajaajila hawaasaa irratti gumaacha guddaa waan gumaachaniif badhaasa {rank}ffaa kanaan galateeffamaniiru."
    pdf.set_x(30); pdf.multi_cell(237, 10, msg, align='C')
    
    # Footer Signatures
    pdf.set_y(175); pdf.set_font('Arial', 'B', 12)
    pdf.set_x(40); pdf.cell(60, 10, "Mallattoo Itti Gaafatamaa", border='T', align='C')
    pdf.set_x(195); pdf.cell(60, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", border='T', align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APPLICATION =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- LOGIN SECTION ---
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=150)
        st.markdown("<h2 style='text-align:center; color:#1b5e20;'>Admin Portal</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- APP CONTENT ---
else:
    df = load_data()
    
    # Sidebar with Logo
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("### Deder Land Admin")
        st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
        st.divider()
        menu = st.radio("MAIN MENU", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit", "🚪 Ba'i"])
    
    # 1. DASHBOARD
    if menu == "📊 Dashboard":
        st.markdown(f"## <img src='https://cdn-icons-png.flaticon.com/512/1828/1828743.png' width='30'> Dashboard Analysis", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='stat-card'><h3>💰 Galii</h3><h2 style='color:#2e7d32;'>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB Total</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='stat-card'><h3>👥 Maamiltoota</h3><h2 style='color:#2e7d32;'>{len(df)}</h2><p>Customers</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='stat-card'><h3>👷 Ogeeyyii</h3><h2 style='color:#2e7d32;'>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Staff Members</p></div>", unsafe_allow_html=True)
            
            st.markdown("### 📈 Guddina Galii Ji'aan")
            chart_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.area_chart(chart_data)
        else: st.info("Hanga ammaatti data'n galmeeffame hin jiru.")

    # 2. NEW REGISTRATION
    elif menu == "📝 Galmee Haaraa":
        st.markdown("## 📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)", "Jijjiirraa Maqaa"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa"],
            "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Dhimma Dhala (Inheritance)"]
        }
        
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"f_{g}_{s}")
                    if "TOT" in s: is_tot = True
        
        with st.form("entry_form"):
            st.markdown("### 👤 Odeeffannoo Maamilaa")
            if is_tot:
                c1, c2 = st.columns(2)
                maqaa_f = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
                qax_f = f"G: {c1.text_input('Qaxana G')} / B: {c2.text_input('Qaxana B')}"
            else:
                c1, c2 = st.columns(2)
                maqaa_f, ara_f = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")
                qax_f = c1.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessa Tajaajila Kennee")
            
            if st.form_submit_button("💾 GALMEESSI"):
                if maqaa_f and details and ogeessa:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!"); st.rerun()
                else: st.warning("⚠️ Maaloo odeeffannoo guutuu galchaa!")

    # 3. REPORTS
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Galii & Hojii")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                df[COL_NAMES].to_excel(wr, index=False)
            
            c1, c2 = st.columns(2)
            c1.download_button("📥 Excel Buufadhu", buf.getvalue(), "Gabaasa_Dadar_Land.xlsx")
            if c2.button("✈️ Telegram-itti Ergi"):
                if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa Galii: {df['Kafaltii_Taj'].sum():,.2f} ETB"):
                    st.success("✅ Telegram irratti ergameera!")
        else: st.info("Data'n hin jiru.")

    # 4. CERTIFICATES
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Badhaasa & Beekamtii Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='stat-card'><h2 style='color:#b8860b;'>#{i}</h2><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i)
                    st.download_button(f"📥 PDF Badhaasa {i}", pdf_bytes, f"Beekamtii_{name}.pdf", "application/pdf")
        else: st.info("Ogeeyyiin tajaajila kenne hin jiru.")

    # 5. SEARCH/EDIT
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Maamilaa galchi...")
        if q and not df.empty:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in results.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']} - {row['Guyyaa']}"):
                    u_name = st.text_input("Maqaa Sirreessi", row['Maqaa_Abbaa_Dhimmaa'], key=f"un_{idx}")
                    u_fee = st.number_input("Kaffaltii Sirreessi", value=float(row['Kafaltii_Taj']), key=f"uf_{idx}")
                    if st.button("💾 Update", key=f"up_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = u_name
                        df.at[idx, 'Kafaltii_Taj'] = u_fee
                        save_data(df); st.success("Sirreeffameera!"); st.rerun()
                    if st.button("🗑 Haqi", key=f"del_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False; st.rerun()

import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. STYLE & DESIGN (CSS) =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    /* Halluu Background guutuu */
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    
    /* Sidebar Design */
    [data-testid="stSidebar"] { 
        background-color: #1b5e20 !important; 
        border-right: 3px solid #2e7d32;
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; font-weight: 500; }
    
    /* Dashboard Metric Cards */
    .metric-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 6px solid #2e7d32;
        transition: 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
    .metric-card h4 { color: #666; margin-bottom: 5px; font-size: 16px; }
    .metric-card h2 { color: #1b5e20; margin: 0; font-size: 30px; }
    
    /* Buttons Styling */
    .stButton>button {
        background: linear-gradient(90deg, #4caf50, #2e7d32);
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 12px 20px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { opacity: 0.9; transform: scale(1.02); }
    
    /* Forms Design */
    div.stForm {
        background: white;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CONFIG & FUNCTIONS =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"
LOGO_PATH = "Adiaan/logo.png"
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

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    gold = (255, 215, 0); green = (0, 80, 0)
    pdf.set_draw_color(*green); pdf.set_line_width(2.5); pdf.rect(10, 10, 277, 190)
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.set_text_color(*green)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', 'B', 20); pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    pdf.set_font('Arial', '', 14); pdf.set_text_color(50,50,50)
    pdf.multi_cell(0, 10, "Waggaa 2026 keessatti tajaajila saffisaa fi qulqulluu tajaajila hawaasaa irratti gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru.", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI MAIN LOGIC =================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.write("")
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("<h2 style='text-align:center; color:#1b5e20;'>Dadar Land Admin Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogoogora!")

else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=80)
        st.title("Dedar Land System")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa", "🔍 Barbaadi/Edit", "Ba'i"])
        st.write("---")
        if st.button("🚪 Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 📊 DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color:#1b5e20;'>📊 Dashboard Raawwii Hojii</h2>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><h4>💰 Galii Waliigalaa</h4><h2>{df['Kafaltii_Taj'].sum():,.0f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Galmeeffaman</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)
        
        st.write("")
        if not df.empty and "Ji'a" in df.columns:
            st.subheader("📈 Raawwii Galii Ji'aan")
            chart_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.area_chart(chart_data)

    # --- 📝 GALMEE HAARAA ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        GATII_DICT = {"Gibira": ["Gibira Manaa", "Gibira Lafa Qonnaa"], "Liizii": ["Jijjiirraa Maqaa", "TOT", "Liizii Waggaa"], "Kaartaa": ["Kaartaa Haaromsuu", "Kaartaa Kadastaara"]}
        
        sel_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if sel_main:
            for g in sel_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g])
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0)

        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col2.text_input("Araddaa")
            qax = col1.text_input("Qaxana")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if name and ogeessa and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!"); st.rerun()

    # --- 📈 GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa fi Ergaa Telegram")
        st.dataframe(df[COL_NAMES], use_container_width=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df[COL_NAMES].to_excel(wr, index=False)
        c1, c2 = st.columns(2)
        c1.download_button("📥 Excel Download", buf.getvalue(), "Gabaasa.xlsx")
        if c2.button("✈️ Gabaasa Telegram-itti Ergi"):
            if send_to_telegram(buf.getvalue(), "Gabaasa.xlsx", f"Gabaasa Galii: {df['Kafaltii_Taj'].sum()} ETB"):
                st.success("✅ Gabaasaan Manager-itti Ergameera!")

    # --- 🏆 BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items(), 1):
                with cols[i-1]:
                    st.markdown(f"<div class='metric-card'><h2 style='color:gold;'>{i}FFAA</h2><h3>{name}</h3><p>Tajaajila: {count}</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_advanced_pdf(name, count, i)
                    st.download_button(f"📥 PDF Badhaasa {i}ffaa", pdf_bytes, f"Badhaasa_{name}.pdf")

    # --- 🔍 BARBAADI/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Barbaadi...")
        if q and not df.empty:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in results.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    new_fee = st.number_input("Kafaltii Sirreessi", value=float(row['Kafaltii_Taj']), key=f"f_{idx}")
                    if st.button("Update", key=f"u_{idx}"):
                        df.at[idx, 'Kafaltii_Taj'] = new_fee
                        save_data(df); st.success("Sirreeffameera!"); st.rerun()

    elif menu == "Ba'i":
        st.session_state.logged_in = False
        st.rerun()

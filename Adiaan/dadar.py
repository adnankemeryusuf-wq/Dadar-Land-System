import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE (STRICT ORDER) =================
LOGO_PATH = "Adiaan/logo.png"

# 1. Page config hunda dura dhufuu qaba
st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

# 2. CSS: FOOTER, HEADER FI MENU DHOKSUUF
st.markdown("""
    <style>
    /* Barreeffama 'Hosted with Streamlit' (Footer) dhoksuuf */
    footer {visibility: hidden !important;}
    
    /* Menu (sarara sadii) fi Header gubbaa jiru dhoksuuf */
    header {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    
    /* Toolbar (Manage app, Share, Deploy) dhoksuuf */
    .stAppToolbar {display: none !important;}
    
    /* Iddoo duwwaa gubbaa jiru guutummaatti dhabamsiisuuf */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: -3rem !important;
    }

    /* Bareedina UI */
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CONSTANTS & DATA HANDLING =================
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Waggaa'] = df['Date_Obj'].dt.year
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_advanced_pdf(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    rank_colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    r_color = rank_colors.get(rank, (0, 80, 0))
    rank_text = f"{rank}FFAA"
    pdf.set_fill_color(255, 255, 255); pdf.rect(10, 10, 277, 190, 'F')
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(3.0); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(*r_color); pdf.set_line_width(1.5); pdf.rect(13, 13, 271, 184)
    pdf.set_y(45); pdf.set_text_color(*r_color); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_y(100); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 25, name.upper(), ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center;'>Dadar Land Registration</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=80)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False; st.rerun()

    if menu == "📊 Dashboard":
        st.title("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)
            st.dataframe(df.tail(10), use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara", "Kaartaa Lafa Qonnaa"]
        }
        selected_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        if selected_main:
            for g in selected_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"m_{g}")
                for s in subs:
                    details.append(f"{g}({s})")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s} (ETB)", min_value=0.0, key=f"f_{g}_{s}")
        
        with st.form("entry_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
            ara = c2.text_input("Araddaa")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and details and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!"); st.rerun()

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa fi Xiinxala")
        if not df.empty:
            f_type = st.selectbox("Gosa Gabaasaa:", ["Waliigala", "Waggaa", "Ji'a"])
            st.dataframe(df[COL_NAMES], use_container_width=True)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                df[COL_NAMES].to_excel(writer, index=False)
            st.download_button("📥 Excel Buusi", buf.getvalue(), "Gabaasa.xlsx")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card' style='border-top: 5px solid {colors[i]};'><h2>{i+1}FFAA</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_file = create_advanced_pdf(name, count, i+1)
                    st.download_button(f"📥 Sartiifiketa {i+1}", pdf_file, f"Sadarkaa_{i+1}.pdf", "application/pdf")

    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    new_name = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"en_{idx}")
                    if st.button("Update", key=f"u_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_name
                        save_data(df); st.rerun()
                    if st.button("Haqi", key=f"d_{idx}"):
                        df = df.drop(idx); save_data(df); st.rerun()

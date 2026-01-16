import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & UI STYLE =================
LOGO_PATH = "Adiaan/logo.png"

st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

# --- CSS: MANAGE APP DHOKSUU FI BAREEDINA ---
st.markdown("""
    <style>
    /* 1. Header gubbaa (Manage app, Share, Deploy) guutummaatti dhoksuuf */
    header, .stAppToolbar, .stActionButton, .stDeployButton {
        visibility: hidden; 
        display: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 2. Style Sidebar fi Cards */
    .stApp { background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* 3. Card Style Badhaasaaf */
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 2px solid #2e7d32; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; margin-bottom: 10px; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 45px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CONSTANTS & DATA FUNCTIONS =================
DATA_FILE = "dadar_final_report.txt"
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
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: 1 if x in [9,10,11,12] else (2 if x in [1,2,3] else (3 if x in [4,5,6] else 4)))
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF GENERATION (LOGO BITA FI MIRGA) =================
def create_certificate_pdf(name, count, rank, logo_p):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    r_color = colors.get(rank, (0, 80, 0))
    r_text = "1FFAA" if rank==1 else ("2FFAA" if rank==2 else "3FFAA")

    # Borders
    pdf.set_draw_color(*r_color); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(1.2); pdf.rect(13, 13, 271, 184)

    # Logo bitaa fi mirgaa
    if logo_p and os.path.exists(logo_p):
        pdf.image(logo_p, x=20, y=18, w=25)
        pdf.image(logo_p, x=250, y=18, w=25)

    # Text content
    pdf.set_y(45); pdf.set_text_color(*r_color); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    pdf.set_y(62); pdf.set_text_color(0, 80, 0); pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 12, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    pdf.set_y(100); pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 25, name.upper(), ln=True, align='C')
    pdf.set_y(135); pdf.set_font('Arial', '', 16)
    msg = f"Sadarkaa {r_text} Waggaa 2026 tajaajilamtoota {count} saffisaan tajaajiluun\ngumaacha guddaa waan gumaachaniif sartiifikonni kun kennameef."
    pdf.multi_cell(0, 10, msg, align='C')
    pdf.set_y(175); pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}              Mallattoo: ________________", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- LOGIN PAGE ---
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("<h2 style='text-align:center; color: #1b5e20;'>Dadar Land Administration</h2>", unsafe_allow_html=True)
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
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False; st.rerun()

    # --- 1. DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><h4>💰 Galii</h4><h2>{df['Kafaltii_Taj'].sum():,.2f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><h4>👥 Maamiltoota</h4><h2>{len(df)}</h2><p>Waliigala</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='card'><h4>👷 Ogeeyyii</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Aktiiwii</p></div>", unsafe_allow_html=True)

    # --- 2. REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        with st.form("entry_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            m_name = c1.text_input("Maqaa Abbaa Dhimmaa")
            m_ara = c2.text_input("Araddaa")
            m_qax = c1.text_input("Qaxana")
            m_oge = c2.text_input("Maqaa Ogeessaa")
            m_service = st.text_area("Gosa Tajaajilaa")
            m_pay = st.number_input("Kafaltii (ETB)", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                if m_name and m_oge:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), m_name, m_ara, m_qax, m_service, m_oge, m_pay]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!"); st.rerun()

    # --- 3. GABAASA BAL'AA ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Waliigalaa")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Excel/CSV Buusi", csv, "Gabaasa_Dadar.csv", "text/csv")
        else: st.warning("Data'n hin jiru.")

    # --- 4. BADHAASA OGEEYYII (1FFAA-3FFAA) ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.markdown("<h3 style='text-align:center;'>🏆 Ogeeyyii Sadan Jalqabaa</h3>", unsafe_allow_html=True)
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
            labels = ["1FFAA", "2FFAA", "3FFAA"]
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card' style='border-top: 10px solid {colors[i]};'><h1>{labels[i]}</h1><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_file = create_certificate_pdf(name, count, i+1, LOGO_PATH)
                    st.download_button(f"📥 Sartiifiketa {labels[i]}", pdf_file, f"Cert_{name}.pdf", "application/pdf", key=f"dl_{i}")

    # --- 5. SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        st.header("🔍 Barbaadi fi Sirreessi")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            for idx, row in res.iterrows():
                with st.expander(f"📄 {row['Maqaa_Abbaa_Dhimmaa']}"):
                    new_n = st.text_input("Maqaa", row['Maqaa_Abbaa_Dhimmaa'], key=f"n_{idx}")
                    if st.button("Update", key=f"u_{idx}"):
                        df.at[idx, 'Maqaa_Abbaa_Dhimmaa'] = new_n
                        save_data(df); st.success("Sirreeffameera!"); st.rerun()

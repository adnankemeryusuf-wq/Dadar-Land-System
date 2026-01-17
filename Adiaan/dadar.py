import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION =================
LOGO_PATH = "Adiaan/logo.png"
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# CSS Style
st.markdown("""
    <style>
    .stApp { background-color: #f9fbf9; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_MAP = {1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 
             7: "Adooleessa", 8: "Hagayya", 9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee"}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_advanced_pdf(name, service_or_count, date_str, cert_type="CUSTOMER", rank=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border Logic
    border_color = (255, 215, 0) if rank == 1 else (27, 94, 32)
    pdf.set_draw_color(*border_color)
    pdf.set_line_width(2)
    pdf.rect(5, 5, 287, 200)
    pdf.rect(8, 8, 281, 194)

    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, 135, 12, 25)
    
    pdf.set_y(45)
    pdf.set_font('Arial', 'B', 30)
    pdf.set_text_color(*border_color)
    title = "SARTIIFIKETA BEEKAMTII" if cert_type == "STAFF" else "WARAQAA RAGAA TAJAAJILAA"
    pdf.cell(0, 15, title, ln=True, align='C')
    
    pdf.set_font('Arial', '', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    
    if cert_type == "STAFF":
        msg = f"Obbo/Adde {name.upper()}\n\nTajaajilamtoota {service_or_count} saffisaan tajaajiluun sadarkaa {rank}ffaa\nwaggaa 2026 waan qabataniif beekamtiin kun kennameef."
    else:
        msg = f"Obbo/Adde {name.upper()}\n\nTajaajila '{service_or_count}' argachuu keessaniif\nguyyaa {date_str} ragaan kun kennameera."
        
    pdf.multi_cell(0, 12, msg, align='C')
    pdf.set_y(170)
    pdf.line(110, 175, 187, 175)
    pdf.set_xy(110, 177); pdf.set_font('Arial', 'I', 12)
    pdf.cell(77, 8, "Itti Gaafatamaa Waajjiraa", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. UI LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.header("Login")
        with st.form("login"):
            u, p = st.text_input("Username"), st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Dogoggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'><p>💰 Galii</p><h4>{df['Kafaltii_Taj'].sum():,.2f} ETB</h4></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'><p>👥 Maamiltoota</p><h4>{len(df)}</h4></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><h4>{df['Maqaa_Ogeessa'].nunique()}</h4></div>", unsafe_allow_html=True)
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum())

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {"Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"], "Liizii": ["Liizii Waggaa", "TOT"], "Kaartaa": ["Kaartaa Lafa"]}
        sel_main = st.multiselect("Gosa Tajaajilaa", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        for g in sel_main:
            subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g])
            for s in subs:
                details.append(f"{g}({s})")
                d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0)

        with st.form("reg_form"):
            maqaa, ara, qax = st.text_input("Maqaa Maamilaa"), st.text_input("Araddaa"), st.text_input("Qaxana")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            nagahee = st.file_uploader("Nagahee Scan", type=['jpg','png'])
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and details:
                    if nagahee:
                        with open(os.path.join(NAGAHEE_DIR, f"{maqaa}.jpg"), "wb") as f: f.write(nagahee.getbuffer())
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("Galmeeffameera!"); st.rerun()

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Excel")
        st.dataframe(df[COL_NAMES])
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df[COL_NAMES].to_excel(writer, index=False)
        st.download_button("📥 Excel Buusi", buf.getvalue(), "Gabaasa.xlsx")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h2>{i+1}ffaa</h2><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf_b = create_advanced_pdf(name, count, "", "STAFF", i+1)
                    st.download_button(f"📥 Sartiifiketa {i+1}", pdf_b, f"Badhaasa_{name}.pdf")

    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False)]
            for idx, row in res.iterrows():
                with st.expander(f"{row['Maqaa_Abbaa_Dhimmaa']}"):
                    st.write(f"Tajaajila: {row['Gosa_Tajajjilaa']}")
                    if st.button("📜 Sartifiikeetii Maamilaa", key=f"c_{idx}"):
                        pdf_m = create_advanced_pdf(row['Maqaa_Abbaa_Dhimmaa'], row['Gosa_Tajajjilaa'], row['Guyyaa'], "CUSTOMER")
                        st.download_button("📥 PDF Buusi", pdf_m, f"Ragaa_{idx}.pdf")

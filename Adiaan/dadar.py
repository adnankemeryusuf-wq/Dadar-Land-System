import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# Library guyyaa Itiyoophiyaaf
try:
    from ethiopian_date import EthiopianDateConverter
except ImportError:
    st.error("Maaloo 'pip install ethiopian-date' godhi!")

# ================= 1. CONFIGURATION =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
MONTH_ORDER = list(MONTH_MAP.values())

GATII_DICT = {
    "🏷️ Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa", "Gibira Daldalaa"],
    "📜 Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT (Turnover Tax)"],
    "🏗️ Pilaanii": ["Hayyama Ijaarsaa", "Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa", "Pilaanii Jijjiiruu"],
    "🗺️ Kaartaa": ["Kaartaa Haaraa", "Kaartaa Kadastaara", "Kaartaa Bakka Bu'aa", "Sirreeffama Daangaa"],
    "⚖️ Seera": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu"],
    "📂 Biroo": ["Waraqaa Clearance", "Ragaa Qulqullinaa", "Adabbii Ijaarsaa"]
}

# Streamlit Setup
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 1px solid #e0e0e0; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
    .metric-value { font-size: 24px; font-weight: bold; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def get_ethiopian_date():
    now = datetime.now()
    conv = EthiopianDateConverter()
    e = conv.to_ethiopian(now.year, now.month, now.day)
    return f"{e[2]:02d}/{e[1]:02d}/{e[0]}"

def create_pdf(name, count, rank, sig=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    color = (255, 215, 0) if rank == 1 else (192, 192, 192) if rank == 2 else (205, 127, 50)
    pdf.set_draw_color(*color); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_y(50); pdf.set_font('Arial', 'B', 35); pdf.cell(0, 20, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 15, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 16)
    msg = f"Waajjira Lafaa Magaalaa Dadar keessatti tajaajilamtoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru."
    pdf.multi_cell(0, 10, msg, align='C')
    if sig:
        with open("sig_temp.png", "wb") as f: f.write(sig.getbuffer())
        pdf.image("sig_temp.png", 120, 155, 40)
    pdf.set_y(175); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, f"Guyyaa: {get_ethiopian_date()}", 0, 0, 'L')
    pdf.cell(0, 10, "Mallattoo Itti Gaafatamaa", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. UI LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.header("🏢 Login")
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.button("Seeni"):
            if u == "DAD" and p == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Dogooggora!")
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa", "🔍 Edit"])

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Overview")
        
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='card'>💰 Galii<br><span class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</span></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'>👥 Maamila<br><span class='metric-value'>{len(df)}</span></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card'>👷 Ogeeyyii<br><span class='metric-value'>{df['Maqaa_Ogeessa'].nunique()}</span></div>", unsafe_allow_html=True)
            trend = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0).reset_index()
            st.plotly_chart(px.line(trend, x='Ji\'a', y='Kafaltii_Taj', title="Guddina Galii"), use_container_width=True)

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            araddaa = col1.text_input("Araddaa")
            qaxana = col2.text_input("Qaxana")
            # Gosa tajaajilaa qindaawaa
            cat = st.selectbox("Gosa Tajaajilaa", list(GATII_DICT.keys()))
            sub_cat = st.multiselect("Tajaajila Gadi Fageenyaa", GATII_DICT[cat])
            kaffaltii = st.number_input("Kaffaltii (ETB)", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                new_data = [datetime.now().strftime('%d/%m/%Y'), name, araddaa, qaxana, ", ".join(sub_cat), ogeessa, kaffaltii]
                df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                save_data(df)
                st.success("Milkaa'inaan Galmeeffameera!")

    elif menu == "🏆 Badhaasa":
        st.header("🏆 Badhaasa Ogeeyyii")
        sig_file = st.file_uploader("Mallattoo Itti Gaafatamaa (PNG)", type=['png'])
        if not df.empty:
            rank_df = df['Maqaa_Ogeessa'].value_counts().reset_index()
            rank_df.columns = ['Ogeessa', 'Count']
            top_3 = rank_df.head(3)
            cols = st.columns(3)
            for i, row in top_3.iterrows():
                with cols[i]:
                    st.markdown(f"<div class='card'><h1>{['🥇','🥈','🥉'][i]}</h1><h3>{row['Ogeessa']}</h3><p>{row['Count']} Tajaajile</p></div>", unsafe_allow_html=True)
                    pdf_bytes = create_pdf(row['Ogeessa'], row['Count'], i+1, sig=sig_file)
                    st.download_button(f"📥 Sartiifiikeeta {i+1}", pdf_bytes, f"Badhaasa_{row['Ogeessa']}.pdf")

    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa Waliigalaa")
        st.dataframe(df[COL_NAMES])
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        st.download_button("📥 Gabaasa Excel Buufadhu", buf.getvalue(), "Gabaasa_Dadar.xlsx")

import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(
    page_title="Dadar Land Admin Pro", 
    page_icon="🏢", 
    layout="wide"
)

# Gosa Tajaajilaa Guutuu
GATII_DICT = {
    "🏷️ Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa", "Gibira Daldalaa"],
    "📜 Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT (Turnover Tax)"],
    "🏗️ Pilaanii": ["Hayyama Ijaarsaa", "Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa", "Pilaanii Jijjiiruu"],
    "🗺️ Kaartaa": ["Kaartaa Haaraa", "Kaartaa Kadastaara", "Kaartaa Bakka Bu'aa", "Sirreeffama Daangaa"],
    "⚖️ Seera": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Waliigaltee Hiikuu"],
    "📂 Biroo": ["Waraqaa Clearance", "Ragaa Qulqullinaa", "Adabbii Ijaarsaa"]
}

MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}
MONTH_ORDER = list(MONTH_MAP.values())
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    div.stForm { background: white; border-radius: 15px; padding: 25px; border: 1px solid #e0e0e0; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map(MONTH_MAP)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf(name, count, rank, logo_l=None, logo_r=None, sig=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    rank_color = (255, 215, 0) if rank == 1 else (192, 192, 192)
    pdf.set_draw_color(*rank_color); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    
    if logo_l: 
        with open("l_temp.png", "wb") as f: f.write(logo_l.getbuffer())
        pdf.image("l_temp.png", 20, 15, 25)
    
    pdf.set_y(50); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 15, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 15, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 14); pdf.cell(0, 10, f"Tajaajilamtoota {count} tajaajiluun sadarkaa {rank}ffaa argataniiru.", 0, 1, 'C')
    
    if sig:
        with open("s_temp.png", "wb") as f: f.write(sig.getbuffer())
        pdf.image("s_temp.png", 45, 160, 30)
    
    pdf.line(40, 180, 100, 180); pdf.set_xy(40, 182); pdf.cell(60, 10, "Itti Gaafatamaa")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Dadar Land Admin Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026": 
            st.session_state.logged_in = True
            st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Edit"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Xiinxala Hojii")
        if not df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='card' style='border-top: 5px solid green;'><h4>GALII</h4><h2>{df['Kafaltii_Taj'].sum():,.0f}</h2><p>ETB</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card' style='border-top: 5px solid blue;'><h4>MAAMILA</h4><h2>{len(df)}</h2><p>Hundi</p></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='card' style='border-top: 5px solid orange;'><h4>OGEESSA</h4><h2>{df['Maqaa_Ogeessa'].nunique()}</h2><p>Active</p></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='card' style='border-top: 5px solid red;'><h4>AVERAGE</h4><h2>{df['Kafaltii_Taj'].mean():,.0f}</h2><p>ETB</p></div>", unsafe_allow_html=True)

            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.subheader("Trendii Galii Ji'aan")
                fig_trend = px.line(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).reset_index(), x='Ji\'a', y='Kafaltii_Taj', markers=True)
                st.plotly_chart(fig_trend, use_container_width=True)
            with col_b:
                st.subheader("Gosa Tajaajilaa")
                fig_pie = px.pie(df, names='Maqaa_Ogeessa', hole=0.3)
                st.plotly_chart(fig_pie, use_container_width=True)
        else: st.info("Data'n hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa Haaraa")
        cats = st.multiselect("Filannoo Tajaajilaa", list(GATII_DICT.keys()))
        final_subs, d_fees, is_tot = [], {}, False
        if cats:
            for c in cats:
                subs = st.multiselect(f"Tajaajila {c}:", GATII_DICT[c])
                for s in subs:
                    final_subs.append(f"{c}-{s}")
                    d_fees[s] = st.number_input(f"Kaffaltii {s}", min_value=0.0)
                    if "TOT" in s: is_tot = True
        
        with st.form("reg"):
            if is_tot:
                cl1, cl2 = st.columns(2)
                name = f"G: {cl1.text_input('Maqaa Gurguraa')} / B: {cl2.text_input('Maqaa Bitataa')}"
                ara, qax = cl1.text_input("Araddaa"), cl1.text_input("Qaxana")
            else:
                name, ara, qax = st.text_input("Maqaa Maamilaa"), st.text_input("Araddaa"), st.text_input("Qaxana")
            
            ogeessa = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, ", ".join(final_subs), ogeessa, sum(d_fees.values())]
                df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                save_data(df); st.success("Galmeeffameera!")

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeeyyii")
        sig = st.file_uploader("Mallattoo Itti Gaafatamaa", type=['png', 'jpg'])
        if not df.empty:
            top = df['Maqaa_Ogeessa'].value_counts().head(3)
            for i, (n, c) in enumerate(top.items(), 1):
                st.write(f"**{i}. {n}** ({c} Hojii)")
                pdf = create_pdf(n, c, i, None, None, sig)
                st.download_button(f"📥 Sartiifikeeta {n}", pdf, f"{n}.pdf")

    # --- REPORT & EDIT ---
    elif menu == "📈 Gabaasa":
        st.dataframe(df[COL_NAMES], use_container_width=True)
        st.download_button("Excel Buusi", df.to_csv(index=False).encode('utf-8'), "Gabaasa.csv")

    elif menu == "🔍 Edit":
        q = st.text_input("Maqaa Barbaadi")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False)]
            st.dataframe(res)

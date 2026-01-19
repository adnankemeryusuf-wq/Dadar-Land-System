import streamlit as st
import pandas as pd
import os
import io
import requests
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"

st.set_page_config(
    page_title="Dadar Land Customer Registration System", 
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🏢", 
    layout="wide"
)

BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
DATA_FILE = "dadar_final_report.txt"

COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]
MONTH_MAP = {9: "Fulbaana", 10: "Onkololeessa", 11: "Sadaasa", 12: "Muddee", 1: "Amajjii", 2: "Guraandhala", 3: "Bitootessa", 4: "Eebila", 5: "Caamsaa", 6: "Waxabajjii", 7: "Adooleessa", 8: "Hagayya"}

# --- STYLE CSS (HALLUU #1b5e20) ---
st.markdown(f"""
    <style>
    /* Background guutuu */
    .stApp {{
        background-color: #f4f7f6;
    }}
    
    /* Header fi Mata Duree */
    .stHeader, h1, h2, h3 {{
        color: #1b5e20 !important;
    }}
    
    /* Sidebar (Bitaa) */
    [data-testid="stSidebar"] {{
        background-color: #1b5e20 !important;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* Buttooniwwan */
    .stButton>button {{
        background-color: #1b5e20;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #2e7d32;
        color: #ffd700;
    }}
    
    /* Card Style Dashboard-iif */
    .card {{
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-top: 5px solid #1b5e20;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
        text-align: center;
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: bold;
        color: #1b5e20;
    }}
    
    /* Formii keessa */
    div.stForm {{
        border: 2px solid #1b5e20;
        border-radius: 15px;
        background-color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
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
    
    pdf.set_draw_color(27, 94, 32) # #1b5e20
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    
    pdf.set_y(50)
    pdf.set_text_color(*r_color)
    pdf.set_font('Arial', 'B', 35) 
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_text_color(27, 94, 32)
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.set_y(110)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 15, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Maqaan ykn Koodiin dogoggora!")
else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=100)
        st.markdown("### Deder Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii Waliigalaa</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3:
                top = df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else "-"
                st.markdown(f"<div class='card'><p>🏆 Ogeessa Filatamaa</p><p class='metric-value'>{top}</p></div>", unsafe_allow_html=True)
            st.markdown("---")
            st.subheader("Trendii Galii Ji'aan")
            st.area_chart(df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0))
        else: st.info("Data'n hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        with st.form("entry_form"):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            gosa = st.selectbox("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa", "Dhimma Mana Murtii"])
            og = st.text_input("Maqaa Ogeessaa")
            kaf = st.number_input("Kafaltii (ETB)", min_value=0.0)
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and og:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, gosa, og, kaf]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("Galmeeffameera!"); st.rerun()

    # --- REPORT ---
    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Galii")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                df[COL_NAMES].to_excel(writer, index=False)
            st.download_button("📥 Excel Buufadhu", buf.getvalue(), "Gabaasa.xlsx")

    # --- AWARDS ---
    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf = create_advanced_pdf(name, count, i+1)
                    st.download_button(f"📥 PDF {i+1}", data=pdf, file_name=f"Badhaasa_{name}.pdf")

    # --- SEARCH/EDIT ---
    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)

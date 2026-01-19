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

import streamlit as st

# CSS Style Halluu #1b5e20 irratti hundaa'e
st.markdown("""
    <style>
    /* 1. Background appii guutuu */
    .stApp {
        background-color: #f4f7f6;
    }

    /* 2. Sidebar (Bitaa) - Halluu #1b5e20 guutuu */
    [data-testid="stSidebar"] {
        background-color: #1b5e20 !important;
    }
    
    /* Barreeffama Sidebar adii gochuuf */
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* 3. Mata duree (Headers) */
    h1, h2, h3 {
        color: #1b5e20 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 4. Buttoonii (Buttons) */
    .stButton>button {
        background-color: #1b5e20;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #2e7d32; /* Yeroo tuqamu xiqqoo ifa */
        color: #ffd700; /* Halluu Warqee (Gold) */
        border: 1px solid #ffd700;
    }

    /* 5. Kaardiiwwan Gabaasaa (Metric Cards) */
    [data-testid="stMetricValue"] {
        color: #1b5e20 !important;
        font-weight: bold;
    }

    /* 6. Formiiwwan (Input Fields) */
    div.stForm {
        border: 2px solid #1b5e20;
        border-radius: 15px;
        padding: 20px;
        background-color: white;
    }
    
    /* 7. Progress Bar fi Checkbox */
    .stProgress > div > div > div > div {
        background-color: #1b5e20;
    }
    </style>
    """, unsafe_allow_html=True)

# Fakkeenya itti fayyadamaa
st.title("🏢 Bulchiinsa Lafa Magaalaa")
st.sidebar.header("Dadar Admin")
st.sidebar.button("Galmee Haaraa")

col1, col2 = st.columns(2)
col1.metric("Waliigala Galii", "500,000 ETB")
col2.metric("Maamiltoota", "1,240")

with st.form("my_form"):
    st.write("Odeeffannoo asitti galchi")
    st.text_input("Maqaa")
    st.form_submit_button("💾 Save")

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

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    rank_colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}
    rank_labels = {1: "1FFAA", 2: "2FFAA", 3: "3FFAA"}
    
    r_color = rank_colors.get(rank, (0, 80, 0))
    r_label = rank_labels.get(rank, "BEEKAMTII")

    # Border
    pdf.set_draw_color(0, 80, 0)
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    
    # Header
    pdf.set_y(45)
    pdf.set_text_color(*r_color)
    pdf.set_font('Arial', 'B', 35) 
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_text_color(0, 80, 0)
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 12, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    pdf.set_y(90)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font('Arial', 'I', 18)
    pdf.cell(0, 10, f"Badhaasa Sadarkaa {r_label} Waggaa 2026", ln=True, align='C')

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 30) 
    pdf.cell(0, 25, f"Obbo/Adde: {name.upper()}", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Admin Login</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
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
        st.success("Deder City Land Office")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "📊 Dashboard":
        st.header("📊 Dashboard Waliigalaa")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
            with c3:
                top = df['Maqaa_Ogeessa'].mode()[0] if not df['Maqaa_Ogeessa'].empty else "-"
                st.markdown(f"<div class='card'><p>🏆 Ogeessa</p><p class='metric-value'>{top}</p></div>", unsafe_allow_html=True)
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "TOT"],
            "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa"],
            "Kaartaa": ["Kaartaa Lafa", "Kaartaa Kadastaara"]
        }
        selected = st.multiselect("Gosa Tajaajilaa:", list(GATII_DICT.keys()))
        details, fees = [], {}
        if selected:
            for g in selected:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=g)
                for s in subs:
                    details.append(f"{g}({s})")
                    fees[s] = st.number_input(f"Kafaltii {s}", min_value=0.0)

        with st.form("reg_form"):
            maqaa = st.text_input("Maqaa Abbaa Dhimmaa")
            ara = st.text_input("Araddaa")
            qax = st.text_input("Qaxana")
            og = st.text_input("Maqaa Ogeessaa")
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and og:
                    new = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(details), og, sum(fees.values())]
                    df = pd.concat([df, pd.DataFrame([new], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("Galmeeffameera!"); st.rerun()

    elif menu == "📈 Gabaasa Bal'aa":
        st.header("📈 Gabaasa Galii")
        if not df.empty:
            st.dataframe(df[COL_NAMES], use_container_width=True)
            st.metric("Waliigala", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        else: st.warning("Data'n hin jiru.")

    elif menu == "🏆 Badhaasa Ogeeyyii":
        st.header("🏆 Sadarkaa Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(3)
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>{name}</h3><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    pdf = create_advanced_pdf(name, count, i+1)
                    st.download_button(f"📥 Sartiifiketa {i+1}", data=pdf, file_name=f"Badhaasa_{name}.pdf", mime="application/pdf")
    
    elif menu == "🔍 Barbaadi/Edit":
        q = st.text_input("Maqaa Barbaadi")
        if q and not df.empty:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.dataframe(res)


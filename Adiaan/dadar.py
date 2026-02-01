import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import xlsxwriter

# ================= 1. THEME & ATTRACTIVE UI =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    /* Background fuula guutuu */
    .stApp {
        background: linear-gradient(135deg, #f3f9f1 0%, #e8f5e9 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #062c1a !important;
        box-shadow: 5px 0 15px rgba(0,0,0,0.2);
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Dashboard Cards - Attractive Gold & Green Border */
    .premium-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-top: 6px solid #b8860b;
        transition: 0.4s;
    }
    .premium-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    .stat-title { color: #555; font-size: 18px; font-weight: 500; }
    .stat-value { color: #1b5e20; font-size: 32px; font-weight: 800; margin-top: 10px; }

    /* Custom Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #1b5e20, #2e7d32);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 25px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #b8860b, #966f08);
        color: white;
        box-shadow: 0 5px 15px rgba(184, 134, 11, 0.4);
    }
    
    /* Form Background */
    div.stForm {
        background: white;
        border-radius: 25px;
        padding: 40px;
        border: none;
        box-shadow: 0 15px 40px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']
MONTH_ORDER = ["Fulbaana", "Onkololeessa", "Sadaasa", "Muddee", "Amajjii", "Guraandhala", "Bitootessa", "Eebila", "Caamsaa", "Waxabajjii", "Adooleessa", "Hagayya"]

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month.map({9:"Fulbaana", 10:"Onkololeessa", 11:"Sadaasa", 12:"Muddee", 1:"Amajjii", 2:"Guraandhala", 3:"Bitootessa", 4:"Eebila", 5:"Caamsaa", 6:"Waxabajjii", 7:"Adooleessa", 8:"Hagayya"})
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. MAIN LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.write("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<div style='background: white; padding: 40px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #1b5e20;'>🏢 Dadar Land</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Admin Management System</p>", unsafe_allow_html=True)
        u = st.text_input("Username", placeholder="admin")
        p = st.text_input("Password", type="password", placeholder="123")
        if st.button("SEENI"):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Maaloo galmee kee sirreessi!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- APP CONTENT ---
else:
    df = load_data()
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>ADMIN PANEL</h2>", unsafe_allow_html=True)
        st.divider()
        menu = st.radio("FILANNOO", ["📊 DASHBOARD", "📝 GALMEE HAARAA", "📈 GABAASA BAL'AA", "🏆 BEEKAMTII", "🔍 BARBAADI", "🚪 BA'I"])
        st.write("<br><br>"*5, unsafe_allow_html=True)
        if st.button("🚪 LOG OUT"): st.session_state.logged_in = False; st.rerun()

    if menu == "📊 DASHBOARD":
        st.markdown("<h2 style='color: #1b5e20;'>📊 Dashboard Analysis</h2>", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='premium-card'><div class='stat-title'>Waliigala Galii</div><div class='stat-value'>{df['Kafaltii_Taj'].sum():,.2f}</div><p style='color: #b8860b;'>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='premium-card'><div class='stat-title'>Maamiltoota</div><div class='stat-value'>{len(df)}</div><p style='color: #b8860b;'>Person</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='premium-card'><div class='stat-title'>Ogeeyyii</div><div class='stat-value'>{df['Maqaa_Ogeessa'].nunique()}</div><p style='color: #b8860b;'>Active Staff</p></div>", unsafe_allow_html=True)
            
            st.markdown("<br>### 📉 Guddina Galii Ji'aan", unsafe_allow_html=True)
            chart_data = df.groupby('Ji\'a')['Kafaltii_Taj'].sum().reindex(MONTH_ORDER).fillna(0)
            st.line_chart(chart_data)
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 GALMEE HAARAA":
        st.markdown("<h2 style='color: #1b5e20;'>📝 Galmee Tajaajilaa</h2>", unsafe_allow_html=True)
        GATII_DICT = {
            "🏷 Gibira & Kaffaltii": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", "TOT (Turnover Tax)", "Jijjiirraa Maqaa"],
            "📜 Kaartaa & Qabiyyee": ["Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", "Sirreeffama Daangaa", "Kaartaa Haaromsuu"],
            "🏗 Pilaanii & Ijaarsa": ["Pilaanii Magaalaa", "Itti Fayyadama Lafaa", "Humna Mahandisummaa", "Hayyama Ijaarsaa"],
            "⚖️ Dhimma Seeraa": ["Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Dhimma Dhala (Inheritance)"],
            "📂 Tajaajila Biroo": ["Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Xalayaa Deeggarsaa"]
        }
        
        sel_main = st.multiselect("🟢 Gosa Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees = [], {}
        
        if sel_main:
            for g in sel_main:
                subs = st.multiselect(f"Tajaajila {g}:", GATII_DICT[g], key=f"s_{g}")
                for s in subs:
                    details.append(f"{g}-{s}")
                    d_fees[f"{g}_{s}"] = st.number_input(f"Kafaltii {s}", min_value=0.0, key=f"v_{g}_{s}")

        with st.form("main_form"):
            c1, c2 = st.columns(2)
            maqaa_f = c1.text_input("Maqaa Maamilaa")
            ara_f = c2.text_input("Araddaa")
            qax_f = c1.text_input("Qaxana")
            ogeessa = st.text_input("Maqaa Ogeessaa")
            
            if st.form_submit_button("💾 GALMEESSI DATA"):
                if maqaa_f and details and ogeessa:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), maqaa_f, ara_f, qax_f, ", ".join(details), ogeessa, sum(d_fees.values())]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df); st.success("✅ Galmeeffameera!"); st.rerun()
                else: st.warning("Maaloo hunda guuti!")

    elif menu == "📈 GABAASA BAL'AA":
        st.markdown("<h2 style='color: #1b5e20;'>📈 Gabaasa Galii Waliigalaa</h2>", unsafe_allow_html=True)
        if not df.empty:
            st.dataframe(df[COL_NAMES].style.highlight_max(axis=0, color='#e8f5e9'), use_container_width=True)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df[COL_NAMES].to_excel(wr, index=False)
            st.download_button("📥 Excel Buufadhu", buf.getvalue(), "Gabaasa_Dadar.xlsx")
        else: st.info("Data'n hin jiru.")

    elif menu == "🚪 BA'I":
        st.session_state.logged_in = False; st.rerun()

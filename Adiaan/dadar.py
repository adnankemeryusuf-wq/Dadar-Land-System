import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

# Custom CSS for High-End, Attractive & Professional UI
st.markdown("""
    <style>
    /* 1. Background: Mesh Gradient softer look with subtle color */
    .stApp {
        background-color: #f8fbf9;
        background-image: radial-gradient(at 0% 0%, rgba(0, 168, 107, 0.05) 0px, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(212, 175, 55, 0.05) 0px, transparent 50%);
    }
    
    /* 2. Sidebar: Ultra-Glass with Glowing Border */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(20px);
        border-right: 2px solid rgba(0, 168, 107, 0.3);
        box-shadow: 10px 0 30px rgba(0,0,0,0.02);
    }
    
    /* 3. Sidebar Radio Buttons: Premium Capsule Style */
    div[data-testid="stSidebarUserContent"] .stRadio > div {
        background: transparent;
        border: none;
        padding: 5px;
    }
    
    div[data-testid="stSidebarUserContent"] .stRadio label {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 12px 20px !important;
        margin-bottom: 8px;
        border: 1px solid #eee;
        transition: 0.3s all ease;
    }
    
    /* Hover effect for Sidebar labels */
    div[data-testid="stSidebarUserContent"] .stRadio label:hover {
        background: rgba(0, 168, 107, 0.1);
        border-color: #00a86b;
        transform: translateX(5px);
    }

    /* 4. Dashboard Cards: Luxury "Glass" Elevation */
    div[data-testid="stMetricWidget"], .metric-card {
        background: white !important;
        border-radius: 28px !important;
        padding: 30px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid #f0f0f0 !important;
        border-top: 5px solid #00a86b !important; /* Luxury top border */
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    
    div[data-testid="stMetricWidget"]:hover {
        transform: translateY(-12px);
        box-shadow: 0 30px 60px rgba(0, 168, 107, 0.12) !important;
        border-top: 5px solid #d4af37 !important; /* Gold flip on hover */
    }
    
    .metric-val { 
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #00a86b, #004d32);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 42px !important;
        font-weight: 900 !important;
    }

    /* 5. Buttons: Radiant Emerald with Shine Effect */
    .stButton>button {
        background: linear-gradient(135deg, #00a86b 0%, #006b44 100%) !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 15px 40px !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
        box-shadow: 0 10px 25px rgba(0, 168, 107, 0.25) !important;
        transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #00c37c 0%, #00a86b 100%) !important;
        box-shadow: 0 15px 30px rgba(0, 168, 107, 0.4) !important;
        transform: translateY(-3px) scale(1.02);
    }

    /* 6. Form/Input Refinement: Ultra Soft */
    .stTextInput input {
        border-radius: 12px !important;
        background-color: #ffffff !important;
        border: 1px solid #e0e6ed !important;
        padding: 14px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .stTextInput input:focus {
        border-color: #00a86b !important;
        box-shadow: 0 0 0 3px rgba(0, 168, 107, 0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)
# ================= 2. DATA MANAGEMENT =================
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

# ================= 3. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # 1. LOGO ON LOGIN
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        
        with st.form("login_form"):
            st.markdown("<h2 style='text-align: center;'>Admin Login</h2>", unsafe_allow_html=True)
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SEENI", use_container_width=True):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Ragaan galchaa sirrii miti!")

# --- AUTHENTICATED APP ---
else:
    df = load_data()
    
    # 2. LOGO ON SIDEBAR
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
        st.markdown("<h3 style='text-align:center;'>WAJJIRA LAFAA</h3>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🚪 Ba'i"])

    if menu == "📊 Dashboard":
        # 3. LOGO ON DASHBOARD HEADER
        head_l, head_r = st.columns([0.1, 0.9])
        with head_l:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=70)
        with head_r:
            st.title("Dadar Land Analytics Overview")
        
        st.markdown("---")
        
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>Galii Waliigalaa</div><div class='metric-val'>{df['Kafaltii_Taj'].sum():,.2f}</div><p>ETB</p></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>Tajaajilamtoota</div><div class='metric-val'>{len(df)}</div><p>Total Customers</p></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>Ogeeyyii</div><div class='metric-val'>{df['Maqaa_Ogeessa'].nunique()}</div><p>Active Staff</p></div>", unsafe_allow_html=True)
        else:
            st.info("Hanga ammaatti data'n galmaa'e hin jiru.")

    # ... (Rest of your sections: Galmee Tajaajilaa & Gabaasa Galii)

    # ... (Koodiin biroo itti fufa)
    elif menu == "📝 Galmee Tajaajilaa":
        st.markdown("<h2 style='color: #1a2a29;'>📝 Galmee Haaraa Galchi</h2>", unsafe_allow_html=True)
        GATII_DICT = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "Gibira Milkii (Stamp Duty)", "TOT (Turnover Tax)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Jijjiirraa Maqaa (Gift/Sale)", "Sirreeffama Daangaa", "Ganda Irraa gara Magaalaatti"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Hayyama Ijaarsaa", "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Mirkaneessa Sertifikeeta Ijaarsaa", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu"],

    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo", "Tajaajila Koppii (Photocopy)"
    ]
}

        
        sel_main = st.multiselect("🟢 Ramaddii Tajaajilaa Filadhu", list(GATII_DICT.keys()))
        details, d_fees, is_tot = [], {}, False
        
        if sel_main:
            for g in sel_main:
                st.markdown(f"**🔹 {g}**")
                subs = st.multiselect(f"Filadhu ({g}):", GATII_DICT[g], key=f"s_{g}")
                if subs:
                    sub_cols = st.columns(len(subs))
                    for idx, s in enumerate(subs):
                        with sub_cols[idx]:
                            fee = st.number_input(f"Gatii {s}", min_value=0.0, key=f"v_{idx}_{s}")
                            details.append(s)
                            d_fees[f"{idx}_{s}"] = fee
                            if "Jijjiirraa" in s or "TOT" in s: is_tot = True

        with st.form("main_form"):
            c1, c2 = st.columns(2)
            if is_tot:
                name_f = f"G: {c1.text_input('Maqaa Gurguraa')} / B: {c2.text_input('Maqaa Bitataa')}"
                ara_f = f"G: {c1.text_input('Araddaa G')} / B: {c2.text_input('Araddaa B')}"
            else:
                name_f, ara_f = c1.text_input("Maqaa Maamilaa"), c2.text_input("Araddaa")
            
            qax_f = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa")
            
            total_sum = sum(d_fees.values())
            st.markdown(f"### 💰 Waliigala Kaffaltii: <span style='color:#00a86b;'>{total_sum:,.2f} ETB</span>", unsafe_allow_html=True)
            
            if st.form_submit_button("💾 GALMEESSI FI NAGAHEE UUMI"):
                if name_f and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name_f, ara_f, qax_f, ", ".join(details), ogeessa, total_sum]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Maamilli milkiin galmeeffameera!")
                    receipt = create_receipt_pdf(new_row)
                    st.download_button("📥 Nagahee (PDF) Buufadhu", receipt, f"Nagahee_{name_f}.pdf", "application/pdf")
                else: st.warning("Maaloo odeeffannoo guuti!")

    elif menu == "📈 Gabaasa Galii":
        st.markdown("<h2 style='color: #1a2a23;'>📈 Gabaasa Waliigalaa</h2>", unsafe_allow_html=True)
        st.dataframe(df.style.highlight_max(axis=0, color='#d1e7dd'), use_container_width=True)
        
        # Excel Export
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
            df.to_excel(wr, index=False)
        st.download_button("📥 Gabaasa (Excel) Buufadhu", buf.getvalue(), "Gabaasa_Dadar.xlsx")

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False
        st.rerun()


















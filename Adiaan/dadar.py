import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF

# ================= 1. PREMIUM STYLE & COLORS =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"

st.set_page_config(page_title="Dadar Land Admin Premium", layout="wide", page_icon="🏢")

# Custom CSS for Professional Emerald & Glassmorphism Look
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    
    /* Sidebar Style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1a14 0%, #1a2a23 100%) !important;
    }
    
    /* Logo styling */
    .logo-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        border-radius: 50%;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        background: white;
        padding: 5px;
    }

    /* Glassmorphism Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        text-align: center;
    }
    
    .metric-val { 
        color: #00a86b;
        font-size: 38px; 
        font-weight: 900; 
    }

    .stButton>button {
        background: linear-gradient(135deg, #00a86b 0%, #007d51 100%);
        color: white !important;
        border-radius: 15px;
        font-weight: 700;
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

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- 1. LOGO ON LOGIN PAGE ---
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        
        st.markdown("""
            <div style='background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-top: 5px solid #00a86b;'>
                <h2 style='text-align: center; color: #1a2a23;'>Seenaa (Login)</h2>
            </div>
        """, unsafe_allow_html=True)
        
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI", use_container_width=True):
            if u == "admin" and p == "123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Dogoggora!")

else:
    df = load_data()
    
    # --- 2. LOGO ON SIDEBAR ---
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=120)
        st.markdown("<h3 style='text-align: center; color: white;'>Waajjira Lafaa</h3>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🚪 Ba'i"])

    if menu == "📊 Dashboard":
        # --- 3. LOGO ON DASHBOARD TOP ---
        c1, c2 = st.columns([0.15, 0.85])
        with c1:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=80)
        with c2:
            st.markdown("<h1 style='color: #1a2a23;'>Dadar Land Admin Analytics</h1>", unsafe_allow_html=True)
        
        st.markdown("---")
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='metric-card'><p class='metric-label'>Galii Waliigalaa</p><p class='metric-val'>{df['Kafaltii_Taj'].sum():,.2f} ETB</p></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-card'><p class='metric-label'>Tajaajilamtoota</p><p class='metric-val'>{len(df)}</p></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='metric-card'><p class='metric-label'>Ogeeyyii</p><p class='metric-val'>{df['Maqaa_Ogeessa'].nunique()}</p></div>", unsafe_allow_html=True)
        else:
            st.info("Data'n hin jiru.")

    # ... (Koodiin biroo itti fufa)
    elif menu == "📝 Galmee Tajaajilaa":
        st.markdown("<h2 style='color: #1a2a23;'>📝 Galmee Haaraa Galchi</h2>", unsafe_allow_html=True)
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




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

# Custom CSS for Waajjira Lafaa Professional UI
st.markdown("""
    <style>
    /* 1. Background Waliigalaa: Halluu laafaa ija hin naafisne */
    .stApp {
        background-color: #f4f7f6;
        background-image: linear-gradient(315deg, #f4f7f6 0%, #e9eeee 74%);
    }
    
    /* 2. Sidebar: Halluu Dukkanaa'aa (Deep Professional Forest) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a261a 0%, #143d2c 100%) !important;
        border-right: 3px solid #d4af37; /* Sarara Warqee */
    }

    /* 3. Barreeffama Sidebar: Adii qulqulluu */
    [data-testid="stSidebarUserContent"] .stRadio label {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        transition: 0.3s all ease;
    }

    /* Active & Hover: Gara halluu Warqeetti (Gold) jijjiirama */
    div[data-testid="stSidebarUserContent"] .stRadio label:hover {
        background: #d4af37 !important;
        color: #0a261a !important;
        transform: scale(1.02);
    }

    /* 4. Dashboard Cards: Bifa Galmee (Document Card) */
    div[data-testid="stMetricWidget"], .metric-card {
        background: #ffffff !important;
        border-radius: 15px !important;
        padding: 25px !important;
        border-left: 10px solid #143d2c !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        transition: 0.4s;
    }

    div[data-testid="stMetricWidget"]:hover {
        box-shadow: 0 10px 25px rgba(20, 61, 44, 0.1) !important;
        border-left: 10px solid #d4af37 !important;
    }

    /* 5. Buttons: Halluu Pirofeeshinaala */
    .stButton>button {
        background: #143d2c !important;
        color: #d4af37 !important;
        border: 2px solid #d4af37 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        padding: 10px 25px !important;
    }

    .stButton>button:hover {
        background: #d4af37 !important;
        color: #143d2c !important;
    }

    /* Header Styling */
    h1, h2, h3 {
        color: #143d2c !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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























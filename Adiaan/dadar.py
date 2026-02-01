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
    /* 1. Global Background - Halluu Soft */
    .stApp { 
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
    }
    
    /* 2. Sidebar Premium Style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1a14 0%, #1a2a23 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; font-weight: 500; }

    /* 3. Glassmorphism Dashboard Cards - Baay'ee Miidhagaa */
    .metric-card {
        background: rgba(255, 255, 255, 0.7); /* Translucent white */
        backdrop-filter: blur(10px); /* Blur effect like glass */
        -webkit-backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-card:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 15px 45px rgba(0, 168, 107, 0.15);
        border: 1px solid #00a86b;
    }
    .metric-val { 
        background: -webkit-linear-gradient(#1a2a23, #00a86b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 38px; 
        font-weight: 900; 
    }
    .metric-label { color: #555; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }

    /* 4. Glassmorphism Form & Containers */
    div[data-testid="stForm"], .login-box {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(15px);
        border-radius: 30px !important;
        padding: 45px !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1) !important;
    }

    /* 5. Animated Buttons - Pro Touch */
    .stButton>button {
        background: linear-gradient(135deg, #00a86b 0%, #007d51 100%);
        color: white !important;
        border-radius: 15px;
        border: none;
        padding: 15px 25px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s all ease;
    }
    .stButton>button:hover {
        box-shadow: 0 10px 20px rgba(0, 168, 107, 0.4);
        transform: scale(1.02);
        filter: brightness(1.1);
    }
    
    /* Input fields refinement */
    .stTextInput>div>div>input {
        border-radius: 12px !important;
        background-color: rgba(255,255,255,0.5) !important;
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

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_receipt_pdf(data):
    pdf = FPDF(orientation='P', unit='mm', format='A5')
    pdf.add_page()
    pdf.set_draw_color(0, 168, 107)
    pdf.rect(5, 5, 138, 200)
    pdf.set_y(15); pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "NAGAHEE TAJAAJILAA", ln=True, align='C')
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, "Waajjira Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 10)
    fields = [("Maqaa:", data[1]), ("Araddaa:", data[2]), ("Tajaajila:", data[4]), ("Ogeessa:", data[5]), ("Kaffaltii:", f"{data[6]:,.2f} ETB")]
    for label, val in fields:
        pdf.cell(30, 8, label); pdf.set_font('Arial', ''); pdf.cell(0, 8, str(val), ln=True); pdf.set_font('Arial', 'B')
    pdf.set_y(185); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ================= 3. MAIN APP LOGIC =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class='login-box'>
                <h1 style='text-align: center; color: #1a2a23;'>🏢 DADAR LAND</h1>
                <p style='text-align: center; color: #666;'>Bulchiinsa Lafaa Magaalaa Dadar</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            u = st.text_input("👤 Username", placeholder="Maqaa kee galchi...")
            p = st.text_input("🔑 Password", type="password", placeholder="Password galchi...")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 SEENI (LOGIN)", use_container_width=True):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Username ykn Password sirrii miti!")

else:
    df = load_data()
    with st.sidebar:
        if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=120)
        st.markdown("### 🛠 NAVIGATION")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Tajaajilaa", "📈 Gabaasa Galii", "🚪 Ba'i"])

    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #1a2a23;'>📊 Analytics Overview</h2>", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Galii Waliigalaa</div><div class='metric-val'>{df['Kafaltii_Taj'].sum():,.2f}</div><p>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Maamiltoota</div><div class='metric-val'>{len(df)}</div><p>Total Customers</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Ogeeyyii</div><div class='metric-val'>{df['Maqaa_Ogeessa'].nunique()}</div><p>Active Staff</p></div>", unsafe_allow_html=True)
            
            # Simple Chart
            st.markdown("### 📈 Trendii Galii")
            chart_data = df.tail(10)
            st.line_chart(chart_data.set_index('Guyyaa')['Kafaltii_Taj'])
        else:
            st.info("Data'n galmeeffame hin jiru.")

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



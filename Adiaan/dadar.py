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

# Custom CSS for Professional & Luxury Look
st.markdown("""
    <style>
    /* 1. Background qulqulluu fi ijaaf mijataa */
    .stApp { 
        background: linear-gradient(to right, #f8f9fa, #e9ecef); 
    }
    
    /* 2. Sidebar: Halluu Dukkanaa'aa fi Kabajamaa (Deep Forest) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #041e12 0%, #062c1a 100%) !important;
        border-right: 3px solid #b8860b; /* Halluu Warqee (Gold) */
    }
    [data-testid="stSidebar"] * { color: #fdfdfd !important; }

    /* 3. Cards Dashboard: Akka Glassmorphism miidhagu */
    .metric-card {
        background: #ffffff;
        padding: 25px;
        border-radius: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        border-left: 6px solid #b8860b; /* Gold accent */
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(11, 102, 35, 0.2);
    }
    .metric-val { color: #0b6623; font-size: 32px; font-weight: 800; }
    .metric-label { color: #444; font-size: 15px; font-weight: bold; text-transform: uppercase; }

    /* 4. Buttons: Professional Gradient */
    .stButton>button {
        background: linear-gradient(135deg, #0b6623 0%, #1a4a2e 100%);
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 2rem;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #b8860b 0%, #8e6a06 100%) !important;
        box-shadow: 0 6px 15px rgba(184, 134, 11, 0.4);
        transform: scale(1.02);
    }
    
    /* 5. Forms: Box Miidhagaa */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 40px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
    }

    /* 6. Text inputs focus effects */
    input {
        border-radius: 8px !important;
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
    pdf.set_draw_color(11, 102, 35)
    pdf.rect(5, 5, 138, 200)
    pdf.set_y(15); pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "NAGAHEE TAJAAJILAA", ln=True, align='C')
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, "Waajjira Lafaa Magaalaa Dadar", ln=True, align='C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 10)
    fields = [("Maqaa:", data[1]), ("Araddaa:", data[2]), ("Tajaajila:", data[4]), ("Ogeessa:", data[5]), ("Kaffaltii:", f"{data[6]:,.2f} ETB")]
    for label, val in fields:
        pdf.cell(30, 8, label); pdf.set_font('Arial', ''); pdf.cell(0, 8, str(val), ln=True); pdf.set_font('Arial', 'B')
    return pdf.output(dest='S').encode('latin-1')
# ================= 3. MAIN APP (BEAUTIFIED LOGIN) =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Page Layout
    _, col, _ = st.columns([1, 1.5, 1])
    
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # Login Card Container
        st.markdown("""
            <div style='background: white; padding: 40px; border-radius: 25px; 
                        box-shadow: 0 15px 35px rgba(0,0,0,0.1); border-top: 8px solid #00a86b;'>
                <h1 style='text-align: center; color: #1a2a23; margin-bottom: 5px;'>🏢 DADAR LAND</h1>
                <p style='text-align: center; color: #666; font-size: 14px;'>Admin Portal - Login to Continue</p>
                <hr style='border: 0.5px solid #eee;'>
            </div>
        """, unsafe_allow_html=True)
        
        # Form fields inside a clean container
        with st.container():
            u = st.text_input("👤 Username", placeholder="Maqaa kee galchi...")
            p = st.text_input("🔑 Password", type="password", placeholder="Password kee galchi...")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 SEENI (LOGIN SYSTEM)", use_container_width=True):
                if u == "admin" and p == "123":
                    st.session_state.logged_in = True
                    st.success("Milkiin seenteetta!")
                    st.rerun()
                else:
                    st.error("Dogoggora! Username ykn Password sirrii miti.")
        
        st.markdown("<p style='text-align: center; color: #aaa; font-size: 12px; margin-top: 20px;'>© 2026 Dadar Land Administration System</p>", unsafe_allow_html=True)

else:
    # ... (Rest of the code for Sidebar and Menu)

    if menu == "📊 Dashboard":
        st.markdown("<h2 style='color: #0b6623;'>📊 Analytics Overview</h2>", unsafe_allow_html=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Galii Waliigalaa</div><div class='metric-val'>{df['Kafaltii_Taj'].sum():,.2f}</div><p>ETB</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Maamiltoota</div><div class='metric-val'>{len(df)}</div><p>Customers</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Ogeeyyii</div><div class='metric-val'>{df['Maqaa_Ogeessa'].nunique()}</div><p>Staff</p></div>", unsafe_allow_html=True)
        else: st.info("Data'n hin jiru.")

    elif menu == "📝 Galmee Tajaajilaa":
        st.markdown("<h2 style='color: #0b6623;'>📝 Galmee Haaraa</h2>", unsafe_allow_html=True)
        GATII_DICT ={
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
            st.markdown(f"### 💰 Waliigala: <span style='color:#0b6623;'>{total_sum:,.2f} ETB</span>", unsafe_allow_html=True)
            
            if st.form_submit_button("💾 GALMEESSI"):
                if name_f and details:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name_f, ara_f, qax_f, ", ".join(details), ogeessa, total_sum]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("✅ Galmeeffameera!")
                    receipt = create_receipt_pdf(new_row)
                    st.download_button("📥 Nagahee (PDF) Buufadhu", receipt, f"Nagahee_{name_f}.pdf", "application/pdf")
                else: st.warning("Maaloo odeeffannoo guuti!")

    elif menu == "📈 Gabaasa Galii":
        st.markdown("<h2 style='color: #0b6623;'>📈 Gabaasa Waliigalaa</h2>", unsafe_allow_html=True)
        st.dataframe(df.style.highlight_max(axis=0, color='#d1e7dd'), use_container_width=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
            df.to_excel(wr, index=False)
        st.download_button("📥 Excel Download", buf.getvalue(), "Gabaasa_Dadar.xlsx")

    elif menu == "🚪 Ba'i":
        st.session_state.logged_in = False; st.rerun()







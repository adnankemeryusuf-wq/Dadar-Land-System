import streamlit as st
import pandas as pd
import os, io, requests
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
DATA_FILE = "dadar_final_report.txt"
CLR_FILE = "clearance_history.txt"
BOT_TOKEN = "8357193631:AAHCuSnXzjZTQaglkmcS0gq-EvqnkIQLDBI"
CHAT_ID_MANAGER = "7329587700"
COL_NAMES = ['Guyyaa', 'Maqaa', 'Araddaa', 'Qaxana', 'Tajaajila', 'Ogeessa', 'Kafaltii']

st.set_page_config(
    page_title="Dadar Land Administration System", 
    page_icon="🏢", 
    layout="wide"
)

# Custom CSS for Modern Look
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    h1, h2 { color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. SERVICE LIST =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax)", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Sirreeffama Daangaa", "Kaartaa Lafa Qonnaa"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Ragaa (Clearance)", "Deebii Iyyannoo"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", "Adabbii Faallaa Pilaanii"
    ],
}

# ================= 3. FUNCTIONS =================
def load_data(f, cols):
    if not os.path.exists(f) or os.stat(f).st_size == 0:
        return pd.DataFrame(columns=cols)
    return pd.read_csv(f, sep="|", names=cols, header=None, encoding='utf-8')

def save_data(df, f):
    df.to_csv(f, sep="|", index=False, header=False, encoding="utf-8")

def create_itemized_receipt(data, items):
    pdf = FPDF(unit='mm', format=(100, 150))
    pdf.add_page()
    pdf.rect(5, 5, 90, 140)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "NAGAHEE KAFFALTII", ln=True, align='C')
    pdf.set_font('Arial', '', 9); pdf.cell(0, 6, f"Maqaa: {data['maqaa']}", ln=True)
    pdf.cell(0, 6, f"Guyyaa: {data['guyyaa']}", ln=True); pdf.ln(5)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(55, 8, " Tajaajila", 1, 0, 'L', True); pdf.cell(25, 8, " ETB", 1, 1, 'R', True)
    for k, v in items.items():
        pdf.cell(55, 8, f" {k[:25]}", 1); pdf.cell(25, 8, f" {v:,.2f}", 1, 1, 'R')
    pdf.set_font('Arial', 'B', 10); pdf.cell(55, 10, " Waliigala", 1, 0, 'R', True); pdf.cell(25, 10, f" {data['total']:,.2f}", 1, 1, 'R', True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. MAIN APP =================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'pdf_ready' not in st.session_state: st.session_state.pdf_ready = None

if not st.session_state.auth:
    st.title("🔐 Login - Dadar Land System")
    with st.form("login_form"):
        u, p = st.text_input("Username"), st.text_input("Password", type="password")
        if st.form_submit_button("Seeni"):
            if u == "admin" and p == "123":
                st.session_state.auth = True; st.rerun()
            else: st.error("Username ykn Password dogoggora!")

else:
    menu = st.sidebar.radio("📋 MENU", ["📊 Dashboard", "📝 Galmee & Nagahee", "🔍 Barbaadi/Manage"])

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard & Analytics")
        df = load_data(DATA_FILE, COL_NAMES)
        if not df.empty:
            df['Kafaltii'] = pd.to_numeric(df['Kafaltii'], errors='coerce').fillna(0)
            c1, c2 = st.columns(2)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Galmee", len(df))
            top5 = df.groupby('Tajaajila')['Kafaltii'].sum().sort_values(ascending=False).head(5).reset_index()
            st.plotly_chart(px.bar(top5, x='Kafaltii', y='Tajaajila', orientation='h', title="Tajaajiloota Galii Olaanaa"))
            st.dataframe(df, use_container_width=True)

    # --- REGISTRATION (FIXED ERROR) ---
    elif menu == "📝 Galmee & Nagahee":
        st.header("📝 Galmee Maamilaa Haaraa")
        
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            m_maqaa = col1.text_input("👤 Maqaa Maamilaa")
            m_ara = col1.text_input("📍 Araddaa")
            m_qax = col2.text_input("🧭 Qaxana")
            m_og = col2.text_input("👷 Maqaa Ogeessaa")
            
            st.markdown("---")
            gosa = st.selectbox("📂 Gosa Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
            taj = st.selectbox("🎯 Tajaajila Tarreeffamaa", SERVICE_STRUCTURE[gosa])
            fee = st.number_input("💸 Kaffaltii (ETB)", min_value=0.0)
            
            submitted = st.form_submit_button("💾 GALMEESSI")
            
            if submitted:
                if m_maqaa:
                    d_now = datetime.now().strftime('%d/%m/%Y')
                    new_rec = [d_now, m_maqaa, m_ara, m_qax, taj, m_og, fee]
                    df = load_data(DATA_FILE, COL_NAMES)
                    df = pd.concat([df, pd.DataFrame([new_rec], columns=COL_NAMES)], ignore_index=True)
                    save_data(df, DATA_FILE)
                    
                    # Store PDF in session state to avoid Form Error
                    pdf_out = create_itemized_receipt({"maqaa":m_maqaa, "guyyaa":d_now, "total":fee}, {taj: fee})
                    st.session_state.pdf_ready = {"data": pdf_out, "name": f"Nagahee_{m_maqaa}.pdf"}
                    st.success(f"Galmeen {m_maqaa} milkaayinaan raawwatameera!")
                else: st.error("Maaloo maqaa galchi!")

        # Nagahee form-icha ala fiduu (Error malee)
        if st.session_state.pdf_ready:
            st.download_button(
                label="📥 Nagahee PDF Buufadhu",
                data=st.session_state.pdf_ready["data"],
                file_name=st.session_state.pdf_ready["name"],
                mime="application/pdf"
            )

    # --- MANAGE / SEARCH ---
    elif menu == "🔍 Barbaadi/Manage":
        st.header("🔍 Barbaadi fi Sirreessi")
        df_m = load_data(DATA_FILE, COL_NAMES)
        if not df_m.empty:
            s_name = st.text_input("Maqaa maamilaa barreessi...")
            if s_name: df_m = df_m[df_m['Maqaa'].str.contains(s_name, case=False)]
            st.dataframe(df_m, use_container_width=True)
            
            row_id = st.number_input("Index galmee haqamuuf jiru", min_value=0, max_value=len(df_m)-1 if len(df_m)>0 else 0)
            if st.button("❌ GALMEE HAQI"):
                full_df = load_data(DATA_FILE, COL_NAMES)
                full_df = full_df.drop(full_df.index[row_id])
                save_data(full_df, DATA_FILE)
                st.success("Haqameera!"); st.rerun()

    # --- TELEGRAM REPORT ---
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Gabaasa Telegram (Excel)"):
        df_all = load_data(DATA_FILE, COL_NAMES)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as wr: df_all.to_excel(wr, index=False)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={'chat_id': CHAT_ID_MANAGER}, files={'document': ("Report.xlsx", out.getvalue())})
        st.sidebar.success("Ergameera!")

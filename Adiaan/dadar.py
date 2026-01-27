import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & DIRECTORIES =================
LOGO_PATH = "Adiaan/logo.png"  # Logo kee bakka kanatti kaayi
NAGAHEE_DIR = "nagahee_scan"
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# ================= 2. SERVICE STRUCTURE =================
SERVICE_STRUCTURE = {
    "🏷 Gibira & Kaffaltii": [
        "Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Kaffaltii Liizii Waggaa", 
        "Kaffaltii Liizii Duraa", "TOT (Turnover Tax) 2%", "Kaffaltii Jijjiirraa Maqaa (Gift/Sale)"
    ],
    "📜 Kaartaa & Qabiyyee": [
        "Kaartaa Haaraa", "Kaartaa Bakka Bu'aa", "Kaartaa Kadastaaraa", 
        "Sirreeffama Daangaa", "Kaartaa Lafa Qonnaa", "Waraqaa Ragaa Qabiyyee"
    ],
    "🏗 Pilaanii & Ijaarsa": [
        "Pilaanii Magaalaa", "Itti Fayyadama Lafaa (Land Use)", 
        "Hayyama Ijaarsaa", "Humna Mahandisummaa"
    ],
    "⚖️ Dhimma Seeraa": [
        "Ugura Mana Murtii", "Ugura Kaasuu", "Waliigaltee Liqii Baankii", 
        "Waliigaltee Hiikuu", "Dhimma Dhala (Inheritance)"
    ],
    "📂 Tajaajila Biroo": [
        "Waraqaa Qulqullummaa (Clearance)", "Deebii Iyyannoo", "Waraqaa Eenyummaa Lafa"
    ],
    "⚖️ Adabbii & Seeressuu": [
        "Adabbii Ijaarsa Seeraan Alaa", "Kaffaltii Seeressuu (Regularization)", "Adabbii Faallaa Pilaanii"
    ],
}

# ================= 3. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_pdf_cert(name, count, rank, logo_left=None, logo_right=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(0, 100, 0)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    
    if logo_left:
        with open("tmp_l.png", "wb") as f: f.write(logo_left.getbuffer())
        pdf.image("tmp_l.png", 20, 15, 30)
    if logo_right:
        with open("tmp_r.png", "wb") as f: f.write(logo_right.getbuffer())
        pdf.image("tmp_r.png", 230, 15, 30)

    pdf.set_y(60)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 10, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 25, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 14)
    pdf.multi_cell(0, 10, f"Waggaa 2026 keessatti maamiltoota {count} tajaajiluun\nsadarkaa {rank}ffaa argataniiru.", align='C')
    
    pdf.line(110, 175, 180, 175)
    pdf.set_xy(110, 177)
    pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 4. UI SETUP =================
st.set_page_config(page_title="Dadar Land Admin", page_icon="🏢", layout="wide")

# CSS for Centered Login and Styling
st.markdown("""
    <style>
    .stApp { background: #f4f7f9; }
    div.stForm { background: white; border-radius: 12px; padding: 25px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .login-container { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 50px; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 5. LOGIN SESSION =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Centered Login UI
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=120)
        st.title("🏢 Dadar Land Admin")
        st.subheader("Customer Registration System")
        
        with st.form("Login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni / Login", use_container_width=True):
                if u == "admin" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # ================= 6. MAIN SYSTEM =================
    df = load_data()
    
    # Sidebar with Logo
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, width=100)
    st.sidebar.title("Dadar Land Admin")
    menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi", "Logout"])

    if menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD ---
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Baay'ina Maamiltootaa", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            
            fig = px.bar(df.groupby('Gosa_Tajajjilaa')['Kafaltii_Taj'].sum().reset_index(), 
                         x='Gosa_Tajajjilaa', y='Kafaltii_Taj', color='Gosa_Tajajjilaa', title="Galii Gosa Tajaajilaan")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ragaan galmeeffame hin jiru.")

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.title("📝 Galmee Tajaajilaa Haaraa")
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Abbaa Dhimmaa")
            ara = col1.text_input("Araddaa")
            qax = col2.text_input("Qaxana")
            og = col2.text_input("Maqaa Ogeessaa")
            
            st.markdown("---")
            cat_choice = st.selectbox("Ramaddii Tajaajilaa", list(SERVICE_STRUCTURE.keys()))
            serv_choice = st.selectbox("Gosa Tajaajilaa", SERVICE_STRUCTURE[cat_choice])
            
            fee_input = st.number_input("Gatii/Kaffaltii (ETB)", min_value=0.0)
            final_fee = fee_input
            if "TOT" in serv_choice:
                final_fee = fee_input * 0.02
                st.caption(f"Hubachiisa: Kaffaltii TOT (2%) ofumaan herregameera: {final_fee:,.2f} ETB")

            if st.form_submit_button("💾 GALMEESSI", use_container_width=True):
                if name and og:
                    new_row = [datetime.now().strftime('%d/%m/%Y'), name, ara, qax, serv_choice, og, final_fee]
                    df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success(f"✅ Galmeeffameera! Kaffaltii: {final_fee:,.2f} ETB")
                else:
                    st.error("Maaloo odeeffannoo guutuu galchi!")

    # --- REPORT ---
    elif menu == "📈 Gabaasa":
        st.title("📈 Gabaasa Waliigalaa")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Excel/CSV gabaasa buufadhu", csv, "gabaasa_dadar.csv", "text/csv")
        else:
            st.warning("Data'n hin jiru.")

    # --- AWARDS ---
    elif menu == "🏆 Badhaasa":
        st.title("🏆 Sartiifiikeeta Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            l_img = st.file_uploader("Logo Bita", type=['png','jpg'])
            r_img = st.file_uploader("Logo Mirga", type=['png','jpg'])
            
            cols = st.columns(len(top_3))
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    st.markdown(f"<div class='card'><h3>Sadarkaa {i+1}ffaa</h3><h4>{name}</h4><p>{count} Customers</p></div>", unsafe_allow_html=True)
                    pdf_b = create_pdf_cert(name, count, i+1, l_img, r_img)
                    st.download_button(f"📥 PDF Download", pdf_b, f"Cert_{name}.pdf", key=f"btn_{i}")

    # --- SEARCH & EDIT ---
    elif menu == "🔍 Barbaadi":
        st.title("🔍 Barbaadi / Haqii")
        q = st.text_input("Maqaa Abbaa Dhimmaa Barbaadi...")
        if q:
            results = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            if not results.empty:
                st.dataframe(results)
                idx_to_del = st.selectbox("Haquuf ID filadhu:", results.index)
                if st.button("🗑 Haqii"):
                    df = df.drop(idx_to_del)
                    save_data(df)
                    st.success("Haqameera!")
                    st.rerun()

import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION & STYLE =================
LOGO_PATH = "Adiaan/logo.png"
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_kuusaa"

# Folder nagahee uumuu
if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide")

# Background miidhagaa fi Style
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to right, #f1f8e9, #ffffff); }
    div.stMetric { 
        background-color: white; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
        border-top: 5px solid #2e7d32;
    }
    .stForm { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .stButton>button { border-radius: 20px; background-color: #2e7d32; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    columns = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Nagahee_Path']
    
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=columns)
    
    try:
        # Fayila dubbisi
        df = pd.read_csv(DATA_FILE, sep="|", encoding='utf-8')
        
        # Yoo column 'Guyyaa' hin jirre, columns irra deebii mirkaneessi
        if 'Guyyaa' not in df.columns:
            df = pd.read_csv(DATA_FILE, sep="|", names=columns, header=None, encoding='utf-8')
        
        # Gara yerootti jijjiiri (Dogoggora sirreessuuf)
        df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
        
        # Kurmaana adda baasuu (Q1-Q4)
        df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: (x-1)//3 + 1 if pd.notnull(x) else 1)
        return df
    except Exception as e:
        st.error(f"Data dubbisuu irratti dogoggora: {e}")
        return pd.DataFrame(columns=columns)

def save_data(df):
    # Column kaffaltii qofa file keessatti kuusuuf
    cols_to_save = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Nagahee_Path']
    df[cols_to_save].to_csv(DATA_FILE, sep="|", index=False, encoding="utf-8")

def create_certificate(name, count, quarter, sig_img=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_draw_color(46, 125, 50); pdf.set_line_width(2); pdf.rect(10, 10, 277, 190)
    
    pdf.set_y(40); pdf.set_font('Arial', 'B', 30); pdf.cell(0, 15, "SARTIIFIKEETA BEEKAMTII KURMAANAA", 0, 1, 'C')
    pdf.set_font('Arial', '', 20); pdf.cell(0, 15, f"Kurmaana {quarter}ffaa - 2026", 0, 1, 'C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 25); pdf.cell(0, 15, f"Obbo/Adde: {name}", 0, 1, 'C')
    
    pdf.set_font('Arial', '', 16)
    msg = f"Tajaajilamtoota {count} saffisaa fi qulqullinaan tajaajiluun hojii boonsaa waan raawwataniif sartiifikeetiin kun kennameef."
    pdf.multi_cell(0, 10, msg, align='C')
    
    if sig_img:
        with open("temp_sig.png", "wb") as f: f.write(sig_img.getbuffer())
        pdf.image("temp_sig.png", 125, 160, 40)
    
    pdf.set_y(175); pdf.set_font('Arial', 'I', 12); pdf.cell(0, 10, "Mallattoo Itti Gaafatamaa", 0, 0, 'C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP =================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏢 Dadar Land Admin Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Seeni"):
        if u == "DAD" and p == "2026": 
            st.session_state.logged_in = True; st.rerun()
else:
    df = load_data()
    menu = st.sidebar.radio("MENU", ["📊 Dashboard Modern", "📝 Galmee & Nagahee", "🏆 Badhaasa Kurmaanaa", "🔍 Barbaadi"])

    # --- DASHBOARD MODERN ---
    if menu == "📊 Dashboard Modern":
        st.title("📊 Dashboard Xiinxala Hojii")
        if not df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💰 Galii Waliigalaa", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
            c2.metric("👥 Maamiltoota", len(df))
            c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
            c4.metric("📅 Kurmaana", f"Q-{datetime.now().month // 4 + 1}")

            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.subheader("📈 Trendii Galii")
                fig_area = px.area(df.sort_values('Date_Obj'), x='Guyyaa', y='Kafaltii_Taj', color_discrete_sequence=['#2e7d32'])
                st.plotly_chart(fig_area, use_container_width=True)
            with col_b:
                st.subheader("🥧 Raawwii Ogeeyyii")
                fig_pie = px.pie(df, names='Maqaa_Ogeessa', hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
                st.plotly_chart(fig_pie, use_container_width=True)
        else: st.info("Data'n hin jiru. Maaloo jalqaba galmee irratti data galchi.")

    # --- REGISTRATION WITH NAGAHEE ---
    elif menu == "📝 Galmee & Nagahee":
        st.header("📝 Galmee Haaraa fi Nagahee Scan")
        with st.form("reg_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Maqaa Maamilaa")
            ara = col2.text_input("Araddaa")
            gosa = col1.selectbox("Gosa Tajaajilaa", ["Kaartaa Haaraa", "Jijjiirraa Maqaa", "Liizii", "Gibira", "TOT", "Kaffaltii Biroo"])
            ogeessa = col2.text_input("Maqaa Ogeessaa")
            kaffaltii = col1.number_input("Kaffaltii (ETB)", min_value=0.0)
            nagahee_file = st.file_uploader("Nagahee Scan Upload", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("💾 Galmeessi"):
                n_path = "Miri"
                if nagahee_file:
                    n_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%H%M%S')}.jpg")
                    with open(n_path, "wb") as f: f.write(nagahee_file.getbuffer())
                
                new_data = pd.DataFrame([[datetime.now().strftime('%d/%m/%Y'), name, ara, "-", gosa, ogeessa, kaffaltii, n_path]], columns=df.columns[:8])
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df); st.success("✅ Galmeeffameera!")

    # --- QUARTERLY CERTIFICATE ---
    elif menu == "🏆 Badhaasa Kurmaanaa":
        st.header("🏆 Sartiifikeeta Kurmaanaa")
        q_sel = st.selectbox("Kurmaana Filadhu", [1, 2, 3, 4])
        sig = st.file_uploader("Mallattoo (PNG)", type=['png'])
        
        q_df = df[df['Kurmaana'] == q_sel]
        if not q_df.empty:
            top = q_df['Maqaa_Ogeessa'].value_counts().head(3)
            for n, c in top.items():
                st.write(f"⭐ **{n}** (Tajaajila {c} kenne)")
                pdf = create_certificate(n, c, q_sel, sig)
                st.download_button(f"📥 Sartiifikeeta {n} Buusi", pdf, f"Cert_{n}.pdf")
        else: st.warning("Kurmaana kanaan data'n hin jiru.")

    # --- BARBAADI ---
    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi fi Edit")
        query = st.text_input("Maqaa Maamilaa")
        if query:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(query, case=False, na=False)]
            st.dataframe(res)

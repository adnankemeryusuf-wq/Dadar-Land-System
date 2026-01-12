import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from ethiopian_date import EthiopianDateConverter

# --- 1. QINDAA'INA (CONFIG) ---
st.set_page_config(page_title="Dadar Land System", layout="wide", page_icon="🏢")

USER_NAME = "Lafa2026"
PASS_WORD = "Dadar@2026"
DATA_FILE = "dadar_final_report.txt"

# Logo yoo hin jirre akka hin dhowwanneef
LOGO_PATH = next((p for p in ["logo.png", "Adiaan/logo.png"] if os.path.exists(p)), None)

# --- 2. CSS CUSTOM STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header-box { 
        text-align: center; padding: 40px; 
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
        color: white; border-radius: 25px; margin-bottom: 30px;
        box-shadow: 0 10px 20px rgba(30, 58, 138, 0.2);
    }
    .metric-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-top: 5px solid #15803d;
        text-align: center;
    }
    .metric-card h4 { color: #64748b; margin-bottom: 5px; font-size: 1rem; }
    .metric-card h2 { color: #1e3a8a; font-size: 2rem; font-weight: 800; }
    .login-card { 
        max-width: 450px; margin: auto; padding: 40px; 
        background: white; border-radius: 25px; 
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKSHIINIIWWAN (HELPERS) ---

def to_ethiopian(dt):
    try:
        ey, em, ed = EthiopianDateConverter.to_ethiopian(dt.year, dt.month, dt.day)
        return f"{ed}/{em}/{ey} E.C"
    except:
        return dt.strftime("%Y-%m-%d")

def generate_certificate(name, rank, year):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # Border
    pdf.set_draw_color(30, 58, 138) 
    pdf.set_line_width(3)
    pdf.rect(10, 10, 277, 190)
    
    pdf.ln(40)
    pdf.set_font('Arial', 'B', 35)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, 'SARTIFIKETII KABAJAA', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Badhaasni kun ogeessa gahumsa qabuuf kenname:', ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 30)
    pdf.set_text_color(184, 134, 11)
    pdf.cell(0, 20, name.upper(), ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 15)
    content = f"Waggaa {year} keessa tajaajila gaarii fi gahumsa qabuun hojjechuun badhaasa sadarkaa {rank} waan ta'aniif qophaa'e."
    pdf.multi_cell(0, 10, content, align='C')
    
    pdf.set_xy(180, 160)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(80, 7, "_______________________", ln=True, align='C')
    pdf.set_x(180)
    pdf.cell(80, 7, "Obbo Aqiil Abdujaliil", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SEENSA (AUTHENTICATION) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<br><br>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_PATH: st.image(LOGO_PATH, width=100)
        st.header("Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("SEENI / LOGIN"):
            if u == USER_NAME and p == PASS_WORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username ykn Password dogoggora!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- 5. MAIN UI ---
    with st.sidebar:
        if LOGO_PATH: st.image(LOGO_PATH, use_container_width=True)
        st.title("Dadar Land")
        menu = ["🏠 Dashboard", "📝 Galmee Haaraa", "📊 Gabaasa & Sartifiketii", "🚪 Logout"]
        choice = st.selectbox("Menu", menu)
        st.divider()
        st.info(f"📅 {to_ethiopian(datetime.now())}")

    st.markdown(f"""
        <div class="header-box">
            <h1 style='margin:0;'>Waajjira Lafaa Magaalaa Dadar</h1>
            <p style='font-size:1.2rem; opacity:0.8;'>Sistama Bulchiinsa Ragaa Ammayyaa</p>
        </div>
        """, unsafe_allow_html=True)

    if choice == "🏠 Dashboard":
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE, sep="|", header=None)
            # Sirreeffama: Kafaltiin lakkofsa ta'uu qaba
            df[12] = pd.to_numeric(df[12], errors='coerce').fillna(0)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><h4>👥 Abbootii Dhimmaa</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            with c2:
                total_income = df[12].sum()
                st.markdown(f'<div class="metric-card"><h4>💰 Galii Waligalaa</h4><h2>{total_income:,.2f} ETB</h2></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="metric-card"><h4>✅ Status</h4><h2>Active</h2></div>', unsafe_allow_html=True)
            
            st.markdown("### 🕒 Galmeewwan Dhiyoo")
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.warning("Hanga yoonaa ragaan galmaa'e hin jiru.")

    elif choice == "📝 Galmee Haaraa":
        with st.form("galmee_form", clear_on_submit=True):
            st.subheader("Ragaa Abbaa Dhimmaa Galmeessi")
            cl1, cl2 = st.columns(2)
            with cl1:
                ad = st.text_input("👤 Maqaa Abbaa Dhimmaa")
                ar = st.text_input("📍 Araddaa")
                wi = st.text_input("🏢 Wirtuu")
            with cl2:
                gs = st.selectbox("🛠️ Gosa Tajaajilaa", ["Kartaa", "Jij_Maqaa", "Lizi", "TOT", "Gibira"])
                og = st.text_input("👨‍💼 Maqaa Ogeessaa")
                k_wal = st.number_input("💵 Kafaltii", min_value=0.0, format="%.2f")
            
            if st.form_submit_button("✅ GALMEE MIRKANEEESSI"):
                if ad and ar:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Toora data file keessatti galu (column 13)
                    line = f"{now}|{ad}|{ar}|{wi}|-|{gs}|{og}|-|Hardha|0|0|0|{k_wal}\n"
                    with open(DATA_FILE, "a", encoding="utf-8") as f:
                        f.write(line)
                    st.success(f"Ragaan '{ad}' galmaa'era!")
                    st.balloons()
                else:
                    st.error("Maaloo maqaa fi araddaa guuti!")

    elif choice == "📊 Gabaasa & Sartifiketii":
        tab1, tab2 = st.tabs(["📄 Gabaasa Ragaa", "🎓 Sartifiketii Badhaasaa"])
        
        with tab1:
            if os.path.exists(DATA_FILE):
                df_view = pd.read_csv(DATA_FILE, sep="|", header=None)
                st.dataframe(df_view)
                csv = df_view.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Excel/CSV Buufadhu", csv, "gabaasa_dadar.csv", "text/csv")
            else:
                st.info("Ragaan buufatamu hin jiru.")
        
        with tab2:
            st.subheader("Sartifiketii Miidhagaa Uumi")
            c_name = st.text_input("Maqaa Ogeessaa")
            c_rank = st.selectbox("Sadarkaa", ["1ffaa", "2ffaa", "3ffaa"])
            c_year = st.text_input("Waggaa (E.C)", "2017")
            if st.button("🎨 GENERATE PDF"):
                if c_name:
                    try:
                        pdf_out = generate_certificate(c_name, c_rank, c_year)
                        st.download_button("📥 Buufadhu (PDF)", pdf_out, f"{c_name}_Award.pdf", "application/pdf")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Maaloo maqaa galchi!")

    elif choice == "🚪 Logout":
        st.session_state.logged_in = False
        st.rerun()

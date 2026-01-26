import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
# Page config si'a tokko qofa gubbaatti waamama
st.set_page_config(
    page_title="Dadar Land Admin System", 
    page_icon="🏢", 
    layout="wide"
)

DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_scan"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

# CSS Customization
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    .card { 
        background: white; padding: 20px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; 
        border-top: 5px solid #2e7d32; margin-bottom: 10px; 
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Kafaltii_Taj'] = pd.to_numeric(df['Kafaltii_Taj'], errors='coerce').fillna(0)
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

def create_simple_pdf(name, count, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(46, 125, 50) # Green
    pdf.cell(0, 40, "SARTIIFIKEETA BEEKAMTII", ln=True, align='C')
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 20, f"Ogeessa: {name}", ln=True, align='C')
    pdf.cell(0, 20, f"Sadarkaa: {rank} | Hojii Raawwatame: {count}", ln=True, align='C')
    pdf.rect(10, 10, 277, 190)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. NAVIGATION & LOGIN =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.markdown("<h2 style='text-align:center;'>🏢 Dadar Login</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Seeni"):
                if u == "DAD" and p == "2026":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Username/Password dogoggora!")
else:
    df = load_data()
    
    with st.sidebar:
        st.title("Dadar Land Admin")
        menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa", "🏆 Badhaasa", "🔍 Barbaadi"])
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header("Dashboard Waliigalaa")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='card'><p>💰 Galii</p><p class='metric-value'>{df['Kafaltii_Taj'].sum():,.2f}</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='card'><p>👥 Maamiltoota</p><p class='metric-value'>{len(df)}</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='card'><p>👷 Ogeeyyii</p><p class='metric-value'>{df['Maqaa_Ogeessa'].nunique() if not df.empty else 0}</p></div>", unsafe_allow_html=True)
        
        if not df.empty:
            st.subheader("Trendii Hojii Ogeeyyii")
            fig = px.bar(df['Maqaa_Ogeessa'].value_counts(), labels={'value':'Baay\'ina', 'index':'Ogeessa'})
            st.plotly_chart(fig, use_container_width=True)

    # --- REGISTRATION ---
    elif menu == "📝 Galmee Haaraa":
        st.header("📝 Galmee Tajaajilaa")
        GATII_DICT = {
            "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa"],
            "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa"],
            "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara"]
        }
        
        with st.form("entry_form"):
            c1, c2 = st.columns(2)
            maqaa = c1.text_input("Maqaa Abbaa Dhimmaa *")
            ara = c2.text_input("Araddaa *")
            qax = c1.text_input("Qaxana")
            ogeessa = c2.text_input("Maqaa Ogeessaa *")
            
            gosa = st.selectbox("Gosa Tajaajilaa", ["Gibira", "Liizii", "Kaartaa"])
            sub_gosa = st.multiselect("Tajaajila Detayilii", GATII_DICT[gosa])
            kafaltii = st.number_input("Kafaltii Waliigalaa (ETB)", min_value=0.0)
            
            if st.form_submit_button("💾 Galmeessi"):
                if maqaa and ogeessa:
                    new_data = [datetime.now().strftime('%d/%m/%Y'), maqaa, ara, qax, ", ".join(sub_gosa), ogeessa, kafaltii]
                    df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
                    save_data(df)
                    st.success("Galmeen milkaa'inaan raawwatameera!")
                else:
                    st.error("Maaloo maqaafi ogeessa guuti!")

    # --- GABAASA ---
    elif menu == "📈 Gabaasa":
        st.header("📈 Gabaasa fi Excel")
        st.dataframe(df, use_container_width=True)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Excel Buusi", output.getvalue(), "Gabaasa_Dadar.xlsx")

    # --- BADHAASA ---
    elif menu == "🏆 Badhaasa":
        st.header("🏆 Beekamtii Ogeeyyii")
        if not df.empty:
            top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
            cols = st.columns(len(top_3))
            for i, (name, count) in enumerate(top_3.items()):
                with cols[i]:
                    rank = i + 1
                    st.markdown(f"<div class='card'><h3>{rank}FFAA</h3><h4>{name}</h4><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                    cert = create_simple_pdf(name, count, rank)
                    st.download_button(f"📥 Sartiifiketa {name}", cert, f"Cert_{name}.pdf")
        else:
            st.info("Data'n hin jiru.")

    # --- BARBAADI ---
    elif menu == "🔍 Barbaadi":
        st.header("🔍 Barbaadi")
        q = st.text_input("Maqaa Abbaa Dhimmaa barreessi...")
        if q:
            res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(q, case=False, na=False)]
            st.table(res)
    

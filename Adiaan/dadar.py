import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. SETTINGS & STYLE =================
DATA_FILE = "dadar_final_report.txt"
NAGAHEE_DIR = "nagahee_kuusaa" # Folder nagaheen itti kuufamu

if not os.path.exists(NAGAHEE_DIR):
    os.makedirs(NAGAHEE_DIR)

st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide")

# Background fi Style bifa namatti toluun
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #e8f5e9, #ffffff);
    }
    div.stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #2e7d32;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. CORE FUNCTIONS =================
def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj', 'Nagahee_Path'])
    df = pd.read_csv(DATA_FILE, sep="|", encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    # Kurmaana (Quarter) adda baasuu
    df['Kurmaana'] = df['Date_Obj'].dt.month.apply(lambda x: (x-1)//3 + 1)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, sep="|", index=False, encoding="utf-8")

def create_certificate(name, count, quarter, sig_img=None):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    # Border miidhagaa
    pdf.set_draw_color(46, 125, 50) # Green
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    
    pdf.set_y(40)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 15, "SARTIIFIKEETA BEEKAMTII KURMAANAA", 0, 1, 'C')
    
    pdf.set_font('Arial', '', 20)
    pdf.ln(10)
    pdf.cell(0, 10, f"Kurmaana {quarter}ffaa Waggaa 2026", 0, 1, 'C')
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 15, f"Obbo/Adde: {name}", 0, 1, 'C')
    
    pdf.set_font('Arial', '', 16)
    pdf.multi_cell(0, 10, f"Maamiltoota {count} saffisaa fi qulqullinaan tajaajiluun hojii boonsaa waan raawwataniif sartiifikeetiin kun kennameef.", align='C')
    
    if sig_img:
        with open("temp_sig.png", "wb") as f: f.write(sig_img.getbuffer())
        pdf.image("temp_sig.png", 120, 160, 40)
        
    pdf.set_y(175)
    pdf.cell(0, 10, "Mallattoo Itti Gaafatamaa", 0, 0, 'C')
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP =================
df = load_data()
menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard Modern", "📝 Galmee & Nagahee", "🏆 Badhaasa Kurmaanaa"])

# --- DASHBOARD MODERN ---
if menu == "📊 Dashboard Modern":
    st.title("📊 Dashboard Xiinxala Hojii")
    
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("👥 Maamiltoota", len(df))
        c3.metric("👷 Ogeeyyii", df['Maqaa_Ogeessa'].nunique())
        c4.metric("📅 Kurmaana Ammaa", f"{datetime.now().month // 4 + 1}")

        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📈 Trendii Galii")
            fig_area = px.area(df.sort_values('Date_Obj'), x='Guyyaa', y='Kafaltii_Taj', color_discrete_sequence=['#2e7d32'])
            st.plotly_chart(fig_area, use_container_width=True)

        with col_right:
            st.subheader("🥧 Raawwii Ogeeyyii")
            fig_pie = px.pie(df, names='Maqaa_Ogeessa', hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.subheader("📋 Galmeewwan dhiyoo")
        st.dataframe(df[['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Gosa_Tajajjilaa', 'Kafaltii_Taj']].tail(5), use_container_width=True)
    else:
        st.info("Data'n hin jiru.")

# --- REGISTRATION WITH RECEIPT SCAN ---
elif menu == "📝 Galmee & Nagahee":
    st.header("📝 Galmee Haaraa fi Nagahee Scan")
    
    with st.form("reg_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Maqaa Maamilaa")
        ara = col2.text_input("Araddaa")
        gosa = col1.selectbox("Gosa Tajaajilaa", ["Kaartaa Haaraa", "Jijjiirraa Maqaa", "Liizii", "Gibira", "TOT", "Kaffaltii Biroo"])
        ogeessa = col2.text_input("Maqaa Ogeessaa")
        kaffaltii = col1.number_input("Kaffaltii (ETB)", min_value=0.0)
        nagahee_file = st.file_uploader("Nagahee Scan (Image)", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("💾 Galmeessi"):
            nagahee_path = "Miri"
            if nagahee_file:
                nagahee_path = os.path.join(NAGAHEE_DIR, f"{name}_{datetime.now().strftime('%Y%H%M%S')}.jpg")
                with open(nagahee_path, "wb") as f:
                    f.write(nagahee_file.getbuffer())
            
            new_row = {'Guyyaa': datetime.now().strftime('%d/%m/%Y'), 'Maqaa_Abbaa_Dhimmaa': name, 
                       'Araddaa': ara, 'Qaxana': "-", 'Gosa_Tajajjilaa': gosa, 
                       'Maqaa_Ogeessa': ogeessa, 'Kafaltii_Taj': kaffaltii, 'Nagahee_Path': nagahee_path}
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("✅ Galmeeffameera! Nagaheen kuusaa keetti ol-ka'eera.")

# --- QUARTERLY CERTIFICATE ---
elif menu == "🏆 Badhaasa Kurmaanaa":
    st.header("🏆 Sartiifikeeta Kurmaanaa")
    q_sel = st.selectbox("Kurmaana Filadhu", [1, 2, 3, 4])
    sig = st.file_uploader("Mallattoo Itti Gaafatamaa (PNG)", type=['png'])
    
    q_df = df[df['Kurmaana'] == q_sel]
    
    if not q_df.empty:
        top_ogeessa = q_df['Maqaa_Ogeessa'].value_counts().head(3)
        for name, count in top_ogeessa.items():
            st.write(f"🌟 **{name}** - Kurmaana kana keessa maamila {count} tajaajile.")
            cert_pdf = create_certificate(name, count, q_sel, sig)
            st.download_button(f"📥 Sartiifikeeta {name} Buusi", cert_pdf, f"Cert_{name}_Q{q_sel}.pdf")
    else:
        st.warning("Kurmaana kanaan data'n hin jiru.")

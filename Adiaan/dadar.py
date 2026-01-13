import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from PIL import Image
from fpdf import FPDF

# ================= 1. CONFIGURATION & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f9fff9 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #2e7d32; }
    .stButton>button { background: linear-gradient(90deg, #4caf50, #2e7d32); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA MANAGEMENT =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

GATII_DICT = {
    "Gibira": ["Gibira Baaxii Gooroo", "Gibira Lafa Qonnaa", "Gibira Manaa"],
    "Liizii": ["Liizii Waggaa", "Jijjiirraa Maqaa", "Kafaltii Liizii Duraa", "TOT"],
    "Kaartaa": ["Kaartaa Manaa", "Kaartaa Kadastaara", "Kaartaa Haaromsuu"],
    "Ittii Fayyaddam": ["Hayyama Itti Fayyadama Lafaa", "Humna Mahandiisaa"]
}

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    df['Date_Obj'] = pd.to_datetime(df['Guyyaa'], format='%d/%m/%Y', errors='coerce')
    df['Ji\'a'] = df['Date_Obj'].dt.month
    df['Waggaa'] = df['Date_Obj'].dt.year
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF CERTIFICATE ENGINE =================
class CertificatePDF(FPDF):
    def header(self): pass
    def footer(self): pass

def create_advanced_pdf(name, count, rank, logo_file=None):
    pdf = CertificatePDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluuwwan Rank (1st=Gold, 2nd=Silver, 3rd=Bronze)
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    # --- 1. Background Magariisa Salphaa ---
    pdf.set_fill_color(240, 255, 240) 
    pdf.rect(12, 12, 273, 186, 'F')

    # --- 2. Border ---
    pdf.set_line_width(4); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(1); pdf.rect(14, 14, 269, 182)

    # --- 3. Logo Bitaa fi Mirga ---
    if logo_file:
        img = Image.open(logo_file)
        img_path = "temp_logo.png"
        img.save(img_path)
        pdf.image(img_path, x=25, y=20, w=30)  # Left
        pdf.image(img_path, x=242, y=20, w=30) # Right

    # --- 4. Content ---
    pdf.set_y(35); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_text_color(30, 70, 30); pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(15); pdf.set_text_color(50, 50, 50); pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    
    pdf.ln(5); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 32)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_text_color(40, 40, 40); pdf.set_font('Arial', '', 15)
    msg = (f"Waggaa 2026 keessatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een\n"
           f"Abbootii Dhimmaa {count} tajaajiluun bu'aa qabeessa ta'anii waan argamaniif\n"
           f"beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')

    # --- 5. Signature ---
    pdf.ln(25); curr_y = pdf.get_y()
    pdf.set_draw_color(0, 0, 0); pdf.line(40, curr_y, 110, curr_y)
    pdf.set_xy(40, curr_y + 2); pdf.cell(70, 10, "Itti Gaafatamaa Waajjiraa", align='C')
    pdf.line(180, curr_y, 250, curr_y)
    pdf.set_xy(180, curr_y + 2); pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN APP =================
df = load_data()

with st.sidebar:
    st.title("🏢 DADAR LAND")
    menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])

if menu == "📊 Dashboard":
    st.header("📊 Dashboard Waliigalaa")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Tajaajilamtoota", len(df))
        c3.metric("Ogeeyyii", len(df['Maqaa_Ogeessa'].unique()))
        st.area_chart(df.groupby('Guyyaa')['Kafaltii_Taj'].sum())
    else:
        st.info("Data'n hin jiru.")

elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa")
    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        maqaa = c1.text_input("Maqaa Abbaa Dhimmaa")
        ogeessa = c2.text_input("Maqaa Ogeessaa")
        araddaa = c1.text_input("Araddaa")
        qaxana = c2.text_input("Qaxana")
        gosa = st.selectbox("Gosa Tajaajilaa", ["Kaartaa", "Gibira", "Liizii", "Ittii Fayyaddam"])
        kafaltii = st.number_input("Kafaltii (ETB)", min_value=0.0)
        
        if st.form_submit_button("💾 Galmeessi"):
            new_data = [datetime.now().strftime('%d/%m/%Y'), maqaa, araddaa, qaxana, gosa, ogeessa, kafaltii]
            df = pd.concat([df, pd.DataFrame([new_data], columns=COL_NAMES)], ignore_index=True)
            save_data(df); st.success("Galmeeffameera!")

elif menu == "📈 Gabaasa Bal'aa":
    st.header("📈 Gabaasa Waliigalaa")
    st.dataframe(df[COL_NAMES], use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Excel/CSV Download", csv, "gabaasa.csv", "text/csv")

elif menu == "🏆 Badhaasa Ogeeyyii":
    st.header("🏆 Badhaasa Ogeessa Cimaa (PDF)")
    u_logo = st.file_uploader("Logo Sartiifiikeetaa Filadhu (Bitaa fi Mirga)", type=["png", "jpg", "jpeg"])
    if not df.empty:
        top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        cols = st.columns(3)
        for i, (name, count) in enumerate(top_3.items(), 1):
            with cols[i-1]:
                st.markdown(f"<div class='card'><h3>{i}FFAA</h3><h4>{name}</h4><p>Tajaajile: {count}</p></div>", unsafe_allow_html=True)
                pdf_bytes = create_advanced_pdf(name, count, i, u_logo)
                st.download_button(f"📥 Download PDF {i}ffaa", pdf_bytes, f"Cert_{name}.pdf", "application/pdf")

elif menu == "🔍 Barbaadi/Edit":
    st.header("🔍 Barbaadi ykn Edit Godhi")
    search = st.text_input("Maqaa Abbaa Dhimmaa Barreessi")
    if search:
        res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search, case=False, na=False)]
        st.write(f"Bu'aa {len(res)} argaman:")
        st.dataframe(res)

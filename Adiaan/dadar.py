import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from PIL import Image
from fpdf import FPDF

# ================= 1. SETUP & STYLING =================
st.set_page_config(page_title="Dadar Land Admin Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f4; }
    [data-testid="stSidebar"] { background-color: #1b5e20 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .card { 
        background: white; padding: 20px; border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; 
        border-top: 5px solid #2e7d32; 
    }
    .stButton>button { 
        background: linear-gradient(90deg, #4caf50, #2e7d32); 
        color: white; border-radius: 8px; font-weight: bold; width: 100%; 
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 2. DATA ENGINE =================
DATA_FILE = "dadar_final_report.txt"
COL_NAMES = ['Guyyaa', 'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj']

def load_data():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return pd.DataFrame(columns=COL_NAMES)
    df = pd.read_csv(DATA_FILE, sep="|", names=COL_NAMES, header=None, encoding='utf-8')
    return df

def save_data(df_to_save):
    df_to_save[COL_NAMES].to_csv(DATA_FILE, sep="|", index=False, header=False, encoding="utf-8")

# ================= 3. PDF GENERATOR (DUAL LOGO) =================
class CertificatePDF(FPDF):
    def header(self): pass
    def footer(self): pass

def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    pdf = CertificatePDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Colors based on rank
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    # 1. Background Light Green
    pdf.set_fill_color(245, 255, 245) 
    pdf.rect(12, 12, 273, 186, 'F')

    # 2. Borders
    pdf.set_line_width(4); pdf.set_draw_color(r, g, b); pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(1); pdf.rect(14, 14, 269, 182)

    # 3. Dual Logos (Size Fixed at 35mm)
    logo_size = 35
    if logo_left:
        left_p = "left_temp.png"
        Image.open(logo_left).save(left_p)
        pdf.image(left_p, x=22, y=20, w=logo_size)
    if logo_right:
        right_p = "right_temp.png"
        Image.open(logo_right).save(right_p)
        pdf.image(right_p, x=240, y=20, w=logo_size)

    # 4. Content
    pdf.set_y(40); pdf.set_text_color(r, g, b); pdf.set_font('Arial', 'B', 35)
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

    # 5. Signatures
    pdf.ln(25); curr_y = pdf.get_y()
    pdf.set_draw_color(0, 0, 0); pdf.line(40, curr_y, 110, curr_y)
    pdf.set_xy(40, curr_y + 2); pdf.cell(70, 10, "Itti Gaafatamaa Waajjiraa", align='C')
    pdf.line(180, curr_y, 250, curr_y)
    pdf.set_xy(180, curr_y + 2); pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 4. MAIN INTERFACE =================
df = load_data()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=100)
    st.title("DADAR LAND")
    menu = st.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "📈 Gabaasa Bal'aa", "🏆 Badhaasa Ogeeyyii", "🔍 Barbaadi/Edit"])

if menu == "📊 Dashboard":
    st.header("📊 Dashboard Gabaasaa")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
        c2.metric("Tajaajilamtoota", len(df))
        c3.metric("Ogeeyyii", len(df['Maqaa_Ogeessa'].unique()))
        st.line_chart(df.groupby('Guyyaa')['Kafaltii_Taj'].sum())
    else: st.info("Data'n galmeeffame hin jiru.")

elif menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa Haaraa")
    with st.form("galmee_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_abbaa = c1.text_input("Maqaa Abbaa Dhimmaa")
        ogeessa = c2.text_input("Maqaa Ogeessaa")
        araddaa = c1.text_input("Araddaa")
        qaxana = c2.text_input("Qaxana")
        gosa = st.selectbox("Gosa Tajaajilaa", ["Kaartaa", "Gibira", "Liizii", "Ittii Fayyaddam"])
        kafaltii = st.number_input("Kafaltii (ETB)", min_value=0.0)
        if st.form_submit_button("💾 Galmeessi"):
            new_row = [datetime.now().strftime('%d/%m/%Y'), m_abbaa, araddaa, qaxana, gosa, ogeessa, kafaltii]
            df = pd.concat([df, pd.DataFrame([new_row], columns=COL_NAMES)], ignore_index=True)
            save_data(df); st.success("Galmee Keessan Milkaa'inaan Ol-ka'eera!")

elif menu == "📈 Gabaasa Bal'aa":
    st.header("📈 Gabaasa Tajaajilaa")
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Gabaasa CSV Buufadhu", df.to_csv(index=False).encode('utf-8'), "gabaasa_dadar.csv", "text/csv")

elif menu == "🏆 Badhaasa Ogeeyyii":
    st.header("🏆 Badhaasa & Sartiifiikeeta")
    col_l, col_r = st.columns(2)
    logo_l = col_l.file_uploader("Logo Bitaa (Government)", type=['png', 'jpg'])
    logo_r = col_r.file_uploader("Logo Mirgaa (Office)", type=['png', 'jpg'])
    
    if not df.empty:
        top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        cols = st.columns(3)
        for i, (name, count) in enumerate(top_3.items(), 1):
            with cols[i-1]:
                st.markdown(f"<div class='card'><h3>{i}FFAA</h3><h4>{name}</h4><p>Hojii: {count}</p></div>", unsafe_allow_html=True)
                pdf_bytes = create_advanced_pdf(name, count, i, logo_l, logo_r)
                st.download_button(f"📥 Buufadhu PDF {i}", pdf_bytes, f"Sartifiketa_{name}.pdf", "application/pdf")

elif menu == "🔍 Barbaadi/Edit":
    st.header("🔍 Barbaadi ykn Edit Godhi")
    search_q = st.text_input("Maqaa Barbaadi...")
    if search_q:
        res = df[df['Maqaa_Abbaa_Dhimmaa'].str.contains(search_q, case=False, na=False)]
        st.dataframe(res)
        if not res.empty:
            if st.button("🗑 Haqama (Hunda Filtarii)"):
                df = df[~df['Maqaa_Abbaa_Dhimmaa'].str.contains(search_q, case=False, na=False)]
                save_data(df); st.rerun()

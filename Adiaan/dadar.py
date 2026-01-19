import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# ================= 1. CONFIGURATION =================
DATA_FILE = "dadar_land_data.csv"
NAGAHEE_DIR = "nagahee_scan"
if not os.path.exists(NAGAHEE_DIR): os.makedirs(NAGAHEE_DIR)

# Columns hunda haala bareedaan qindeeffame
COL_NAMES = [
    'Guyyaa', 'Torbee', 'Ji\'a', 'Kurmaana', 'Waggaa', 
    'Maqaa_Abbaa_Dhimmaa', 'Araddaa', 'Qaxana', 
    'Gosa_Tajajjilaa', 'Maqaa_Ogeessa', 'Kafaltii_Taj'
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COL_NAMES)
    return pd.read_csv(DATA_FILE)

# ================= 2. CERTIFICATE (BADHAASA) =================
def create_certificate(name, count, rank, logo_l, logo_r, sig):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border bareedaa
    pdf.set_draw_color(0, 80, 0); pdf.set_line_width(3); pdf.rect(10, 10, 277, 190)
    pdf.set_draw_color(200, 150, 0); pdf.set_line_width(1); pdf.rect(13, 13, 271, 184)

    # Logos (Bitaa fi Mirga)
    if logo_l:
        pdf.image(io.BytesIO(logo_l.read()), 20, 20, 35)
    if logo_r:
        pdf.image(io.BytesIO(logo_r.read()), 240, 20, 35)

    # Text
    pdf.set_y(60)
    pdf.set_font('Arial', 'B', 35); pdf.cell(0, 15, "SARTIIFIKEETA BEEKAMTII", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 20); pdf.cell(0, 10, "Badhaasa Ogeessa Onnee", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 25); pdf.cell(0, 15, f"Obbo/Adde: {name}", 0, 1, 'C')
    pdf.set_font('Arial', '', 16); pdf.multi_cell(0, 10, 
        f"Waggaa {datetime.now().year} keessatti tajaajila qulqulluu maamiltoota {count} \n"
        f"kennuun sadarkaa {rank}ffaa argataniiru.", align='C')

    # Signature
    if sig:
        pdf.image(io.BytesIO(sig.read()), 120, 160, 40)
    pdf.line(110, 185, 180, 185)
    pdf.set_xy(110, 186); pdf.set_font('Arial', 'B', 12); pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ================= 3. MAIN APP =================
st.set_page_config(layout="wide")
df = load_data()

menu = st.sidebar.radio("FILANNOO", ["📊 Dashboard", "📝 Galmee Haaraa", "🏆 Badhaasa", "📈 Gabaasa"])

# --- GALMEE HAARAA ---
if menu == "📝 Galmee Haaraa":
    st.header("📝 Galmee Tajaajilaa")
    with st.form("reg_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Maqaa Abbaa Dhimmaa")
        ara = c2.selectbox("Araddaa", ["01", "02", "03", "04"])
        qax = c1.selectbox("Qaxana", [str(i) for i in range(1, 11)])
        ogeessa = c2.text_input("Maqaa Ogeessaa")
        taj = c1.text_input("Gosa Tajaajilaa")
        fee = c2.number_input("Kaffaltii (ETB)", min_value=0.0)
        
        if st.form_submit_button("💾 Galmeessi"):
            now = datetime.now()
            # Yeroo addaan baasuu
            week_no = (now.day - 1) // 7 + 1
            quarter = (now.month - 1) // 3 + 1
            
            new_data = {
                'Guyyaa': now.strftime('%A'), # Wixata, Kibxata...
                'Torbee': f"Torbee {week_no}",
                'Ji\'a': now.strftime('%B'), # January, February...
                'Kurmaana': f"Kurmaana {quarter}",
                'Waggaa': now.year,
                'Maqaa_Abbaa_Dhimmaa': name, 'Araddaa': ara, 'Qaxana': qax,
                'Gosa_Tajajjilaa': taj, 'Maqaa_Ogeessa': ogeessa, 'Kafaltii_Taj': fee
            }
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ Galmeeffameera!")

# --- DASHBOARD (Gabaasa Guyyaa/Ji'aa) ---
elif menu == "📊 Dashboard":
    st.header("📊 Xiinxala Gabaasaa")
    col1, col2, col3 = st.columns(3)
    col1.metric("Waliigala Galii", f"{df['Kafaltii_Taj'].sum():,.2f} ETB")
    col2.metric("Maamiltoota", len(df))
    col3.metric("Kurmaana Ammaa", f"K-{ (datetime.now().month-1)//3 + 1 }")

    # Chart Kurmaanaa ykn Ji'aa
    fig = px.bar(df, x='Ji\'a', y='Kafaltii_Taj', color='Kurmaana', title="Galii Ji'aa fi Kurmaanaan")
    st.plotly_chart(fig, use_container_width=True)

# --- BADHAASA (Logoo Bitaa fi Mirgaa) ---
elif menu == "🏆 Badhaasa":
    st.header("🏆 Qopheessaa Sartii fikeetaa")
    l_l = st.file_uploader("Logoo Bitaa", type=['png', 'jpg'])
    l_r = st.file_uploader("Logoo Mirgaa", type=['png', 'jpg'])
    sig = st.file_uploader("Mallattoo", type=['png', 'jpg'])
    
    if not df.empty:
        ogeeyyii = df['Maqaa_Ogeessa'].value_counts()
        for i, (n, c) in enumerate(ogeeyyii.items(), 1):
            st.write(f"{i}. {n} - {c} Tajaajila")
            cert_pdf = create_certificate(n, c, i, l_l, l_r, sig)
            st.download_button(f"📥 Buusi: {n}", cert_pdf, f"Badhaasa_{n}.pdf")

# --- GABAASA EXCEL ---
elif menu == "📈 Gabaasa":
    st.header("📈 Gabaasa Guutuu (Excel)")
    # Filter yeroo
    f_period = st.selectbox("Yeroo Filadhu", ["Hunda", "Guyyaa", "Torbee", "Ji'a", "Kurmaana"])
    
    filtered_df = df.copy()
    st.dataframe(filtered_df, use_container_width=True)
    
    # Excel Download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Gabaasa_Dadar')
    st.download_button("📥 Gabaasa Excel Buusi", output.getvalue(), "Gabaasa_Dadar_Lafa.xlsx")

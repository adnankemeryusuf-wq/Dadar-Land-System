import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# ================= 1. PDF GENERATOR FUNCTION =================
class CertificatePDF(FPDF):
    def header(self): pass
    def footer(self): pass

def create_advanced_pdf(name, count, rank, logo_file=None):
    # A4 Landscape (297x210 mm)
    pdf = CertificatePDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Halluuwwan Rank
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    # --- 1. Background Magariisa Salphaa (Light Green) ---
    pdf.set_fill_color(245, 255, 245) # Halluu magariisa baay'ee qallaa
    pdf.rect(15, 15, 267, 180, 'F')

    # --- 2. Border Double ---
    pdf.set_line_width(4)
    pdf.set_draw_color(r, g, b)
    pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(1)
    pdf.rect(13, 13, 271, 184)

    # --- 3. Logo Bitaa fi Mirga ---
    if logo_file:
        # Logo bifa bifa PNG/JPG temp keessa suuraa kaa'uun
        logo_img = Image.open(logo_file)
        logo_path = "temp_logo.png"
        logo_img.save(logo_path)
        
        # Bitaa (Left Logo)
        pdf.image(logo_path, x=25, y=20, w=30)
        # Mirga (Right Logo)
        pdf.image(logo_path, x=242, y=20, w=30)

    # --- 4. Barreeffama ---
    pdf.set_y(30)
    pdf.set_text_color(r, g, b)
    pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_text_color(30, 70, 30) # Dark Green for text
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(15)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_text_color(r, g, b)
    pdf.set_font('Arial', 'B', 32)
    pdf.cell(0, 20, f"Obbo/Adde: {name.upper()}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font('Arial', '', 15)
    msg = (f"Waggaa 2026 keessatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een\n"
           f"Abbootii Dhimmaa {count} tajaajiluun bu'aa qabeessa ta'anii waan argamaniif\n"
           f"beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')

    # --- 5. Mallattoo ---
    pdf.ln(25)
    curr_y = pdf.get_y()
    pdf.set_draw_color(0, 0, 0)
    pdf.line(40, curr_y, 110, curr_y)
    pdf.set_xy(40, curr_y + 2)
    pdf.cell(70, 10, "Itti Gaafatamaa Waajjiraa", align='C')
    
    pdf.line(180, curr_y, 250, curr_y)
    pdf.set_xy(180, curr_y + 2)
    pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= 2. STREAMLIT UI =================
st.title("🎓 Dadar Land Admin - Professional PDF")

# Data fe'uu (load data)
if os.path.exists("dadar_final_report.txt"):
    df = pd.read_csv("dadar_final_report.txt", sep="|", names=['Guyyaa', 'M_Abbaa', 'Araddaa', 'Qaxana', 'Gosa', 'Ogeessa', 'Kafaltii'], header=None)
    
    st.subheader("🏆 Badhaasa Ogeeyyii Cimaa")
    u_logo = st.file_uploader("Logo/Imeejii Sartiifiikeetaa Filadhu", type=["png", "jpg", "jpeg"])
    
    top_performers = df['Ogeessa'].value_counts().head(3)
    cols = st.columns(3)
    
    for i, (name, count) in enumerate(top_performers.items(), 1):
        with cols[i-1]:
            st.info(f"Tartiiba {i}ffaa: {name}")
            if st.button(f"PDF Hojjedhu ({i}ffaa)"):
                pdf_bytes = create_advanced_pdf(name, count, i, u_logo)
                st.download_button(
                    label=f"📥 Download PDF {i}ffaa",
                    data=pdf_bytes,
                    file_name=f"Sartifiketa_{name}.pdf",
                    mime="application/pdf"
                )
else:
    st.warning("Data'n hin jiru.")

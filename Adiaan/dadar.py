def create_advanced_pdf(name, count, rank, logo_left=None, logo_right=None):
    # Orientation 'L' (Landscape), Unit 'mm'
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Rank colors
    rank_colors = {1: (212, 175, 55), 2: (192, 192, 192), 3: (205, 127, 50)}
    r, g, b = rank_colors.get(rank, (27, 94, 32))

    # Background and Border
    pdf.set_fill_color(245, 255, 245)
    pdf.rect(12, 12, 273, 186, 'F')
    pdf.set_line_width(4)
    pdf.set_draw_color(r, g, b)
    pdf.rect(10, 10, 277, 190)

    # --- HANDLING LOGOS (Kutaa Imeejii) ---
    # Logo Bitaa
    if logo_left:
        with open("temp_logo_l.png", "wb") as f:
            f.write(logo_left.getvalue())
        pdf.image("temp_logo_l.png", x=20, y=15, w=35) # x fi y sirreeffameera
    
    # Logo Mirgaa
    if logo_right:
        with open("temp_logo_r.png", "wb") as f:
            f.write(logo_right.getvalue())
        pdf.image("temp_logo_r.png", x=240, y=15, w=35)

    # --- TEXT CONTENT ---
    pdf.set_y(45)
    pdf.set_text_color(r, g, b)
    pdf.set_font('Arial', 'B', 35)
    pdf.cell(0, 25, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_text_color(30, 70, 30)
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(15)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, "Sartiifiketiin Gootummaa Hojii kun kan kennameef:", ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_text_color(r, g, b)
    pdf.set_font('Arial', 'B', 32)
    pdf.cell(0, 20, f"{name.upper()}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font('Arial', '', 15)
    msg = (f"Waggaa 2026 keessatti tajaajila saffisaa fi amannamaa ta'een\n"
           f"Abbootii Dhimmaa {count} tajaajiluun beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    
    # Signatures
    pdf.ln(20)
    curr_y = pdf.get_y()
    pdf.line(40, curr_y, 110, curr_y)
    pdf.set_xy(40, curr_y + 2)
    pdf.cell(70, 10, "Itti Gaafatamaa", align='C')
    
    pdf.line(180, curr_y, 250, curr_y)
    pdf.set_xy(180, curr_y + 2)
    pdf.cell(70, 10, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    # Output as bytes
    return pdf.output(dest='S').encode('latin-1', 'replace') # 'replace' filannoo gaariidha

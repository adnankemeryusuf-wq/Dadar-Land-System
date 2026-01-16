# ================= PDF GENERATION WITH LOGO =================
def create_advanced_pdf(name, count, rank, logo_left_path=None, logo_right_path=None):
    # Orientation 'L' (Landscape), A4
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # --- Halluuwwan Sadarkaa ---
    if rank == 1:
        rank_color, rank_text = (255, 215, 0), "1FFAA" # Gold
    elif rank == 2:
        rank_color, rank_text = (192, 192, 192), "2FFAA" # Silver
    else:
        rank_color, rank_text = (205, 127, 50), "3FFAA" # Bronze

    deep_green = (0, 80, 0)

    # --- 1. Background fi Borders ---
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(10, 10, 277, 190, 'F')
    
    # Border Magariisa
    pdf.set_draw_color(*deep_green)
    pdf.set_line_width(3.0)
    pdf.rect(10, 10, 277, 190)
    
    # Border Halluu Sadarkaa (Inner)
    pdf.set_draw_color(*rank_color)
    pdf.set_line_width(1.5)
    pdf.rect(13, 13, 271, 184)

    # --- 2. Logo Itti Dabaluu ---
    # Logo Bitaa
    if logo_left_path and os.path.exists(logo_left_path):
        pdf.image(logo_left_path, x=20, y=18, w=25)
    
    # Logo Mirgaa (Logo kee isa folder keessa jiru fayyadamna)
    if logo_right_path and os.path.exists(logo_right_path):
        pdf.image(logo_right_path, x=250, y=18, w=25)

    # --- 3. Barreeffama Sartiifiketaa ---
    pdf.set_y(45)
    pdf.set_text_color(*rank_color)
    pdf.set_font('Arial', 'B', 35) 
    pdf.cell(0, 15, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.set_y(62)
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 22)
    pdf.cell(0, 12, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')

    pdf.set_y(90)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font('Arial', 'I', 18)
    pdf.cell(0, 10, f"Badhaasa Sadarkaa {rank_text} Waggaa 2026", ln=True, align='C')

    pdf.set_y(110)
    pdf.set_text_color(*deep_green)
    pdf.set_font('Arial', 'B', 30) 
    pdf.cell(0, 25, f"Obbo/Adde: {name.upper()}", ln=True, align='C')

    pdf.set_y(140)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font('Arial', '', 14)
    msg = f"Tajaajilamtoota {count} saffisaa fi qulqullinaan tajaajiluun gumaacha guddaa waan gumaachaniif badhaasa kanaan galateeffamaniiru."
    pdf.multi_cell(0, 10, msg, align='C')

    # Mallattoo
    pdf.set_y(175)
    pdf.set_draw_color(*deep_green)
    pdf.line(40, 175, 100, 175)
    pdf.set_xy(40, 177); pdf.set_font('Arial', 'B', 12)
    pdf.cell(60, 8, "Mallattoo Itti Gaafatamaa", align='C')

    pdf.line(190, 175, 250, 175)
    pdf.set_xy(190, 177); pdf.cell(60, 8, f"Guyyaa: {datetime.now().strftime('%d/%m/%Y')}", align='C')

    return pdf.output(dest='S').encode('latin-1')

# ================= KUTAA BADHAASA OGEEYYII =================
# Amma kutaa "🏆 Badhaasa Ogeeyyii" keessatti logo path ergi
elif menu == "🏆 Badhaasa Ogeeyyii":
    st.markdown("<h3 style='text-align:center;'>🏆 Sadarkaa fi Badhaasa Ogeeyyii</h3>", unsafe_allow_html=True)
    
    if not df.empty:
        top_3 = df['Maqaa_Ogeessa'].value_counts().head(3)
        cols = st.columns(3)
        colors = ["#FFD700", "#C0C0C0", "#CD7F32"] 
        labels = ["1FFAA", "2FFAA", "3FFAA"]

        for i, (name, count) in enumerate(top_3.items()):
            with cols[i]:
                st.markdown(f"""
                    <div class='card' style='border-top: 8px solid {colors[i]};'>
                        <h1 style='color: {colors[i]};'>{labels[i]}</h1>
                        <h3>{name}</h3>
                        <p>Hojii: <b>{count}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # PDF uumuuf LOGO_PATH (Adiaan/logo.png) ni ergine
                try:
                    pdf_file = create_advanced_pdf(name, count, i+1, logo_left_path=LOGO_PATH, logo_right_path=LOGO_PATH)
                    st.download_button(
                        label=f"📥 Sartiifiketa {labels[i]}",
                        data=pdf_file,
                        file_name=f"Sadarkaa_{i+1}_{name}.pdf",
                        mime="application/pdf",
                        key=f"cert_{i}"
                    )
                except Exception as e:
                    st.error(f"Dogoggora: {e}")

from PIL import Image, ImageDraw, ImageOps

# --- 3. SARTIIFIKETA (Professional, Circular Logo & Center) ---
def generate_certificate(expert_name):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border (Navy Blue & Gold)
    pdf.set_line_width(2); pdf.set_draw_color(184, 134, 11)
    pdf.rect(5, 5, 287, 200) 
    
    # --- LOGOO CHAACHOO (CIRCULAR LOGO) JIDDUU ---
    if LOGO_PATH and os.path.exists(LOGO_PATH):
        try:
            img = Image.open(LOGO_PATH).convert("RGBA")
            # Akka chaachoo gochuuf
            size = (max(img.size), max(img.size))
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img.size, fill=255)
            output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            
            # Gara RGB-tti deebisnee PDF irratti fe'uuf
            final_img = Image.new("RGB", output.size, (255, 255, 255))
            final_img.paste(output, mask=output.split()[3])
            
            # X=131 (Gubbaa jidduu)
            pdf.image(final_img, x=131, y=10, w=35)
        except Exception as e:
            pass

    pdf.ln(35)
    pdf.set_font('Times', 'B', 40); pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 20, "SARTIIFIKETA BEEKAMTII", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Arial', 'I', 16); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Waajjira Lafaa Bulchiinsa Magaalaa Dadar", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 20)
    pdf.cell(0, 10, "Gootummaa Hojii Waggaa kan kennameef:", ln=True, align='C')
    
    pdf.ln(5); pdf.set_font('Times', 'B', 32); pdf.set_text_color(21, 128, 61)
    pdf.cell(0, 15, f"Obbo/Adde: {expert_name.upper()}", ln=True, align='C')
    
    pdf.ln(10); pdf.set_font('Arial', '', 14); pdf.set_text_color(60, 60, 60)
    # Lakkoofsa tajaajilaman irraa haqameera
    msg = ("Waggaa kanatti tajaajila saffisaa, iftoomina qabuu fi amannamaa ta'een "
            "hojii gaarii hojjettanii waan argamtaniif beekamtii kanaan badhaafamaniiru.")
    pdf.multi_cell(0, 10, msg, align='C')
    
    pdf.set_y(172)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 8, "__________________________", ln=0, align='C')
    pdf.cell(87, 8, "", ln=0)
    pdf.cell(100, 8, "__________________________", ln=1, align='C')
    pdf.cell(100, 5, "Aqiil Abdujaaliil", ln=0, align='C')
    pdf.cell(87, 5, "", ln=0)
    pdf.cell(100, 5, datetime.now().strftime("%d/%m/%Y"), ln=1, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. PAGE: SEARCH & EDIT (SIRREEFFAME) ---
elif choice == "🔍 Barbaaduu & Sirreessu":
    st.header("🔍 Barbaadi fi Sirreessi")
    query = st.text_input("Maqaa abbaa dhimmaa barreessi...")
    
    if not df.empty:
        results = df[df['Maqaa'].str.contains(query, case=False, na=False)]
        
        if not results.empty:
            st.dataframe(results, use_container_width=True)
            selected_name = st.selectbox("Nama sirreessuuf filadhu:", results['Maqaa'].unique())
            
            # Data nama filatamee fiduu
            idx = df[df['Maqaa'] == selected_name].index[0]
            
            with st.form("edit_form"):
                st.subheader(f"Sirreeffama Galmee: {selected_name}")
                col1, col2 = st.columns(2)
                new_maqaa = col1.text_input("Maqaa", value=df.at[idx, 'Maqaa'])
                new_araddaa = col2.text_input("Araddaa", value=df.at[idx, 'Araddaa'])
                new_gosa = col1.selectbox("Gosa Tajaajilaa", ["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"], 
                                         index=["Ittii Fayyaddam", "Kartaa", "Jijjirra Maqaa", "Dangaa", "Mana Murttii", "Liqii Bankii"].index(df.at[idx, 'Gosa']))
                new_ogeessa = col2.text_input("Ogeessa", value=df.at[idx, 'Ogeessa'])
                new_kafaltii = col1.number_input("Kafaltii", value=float(df.at[idx, 'Kafaltii_Wal']))
                
                c1, c2 = st.columns(2)
                if c1.form_submit_button("💾 FOOYYEESSI"):
                    df.at[idx, 'Maqaa'] = new_maqaa
                    df.at[idx, 'Araddaa'] = new_araddaa
                    df.at[idx, 'Gosa'] = new_gosa
                    df.at[idx, 'Ogeessa'] = new_ogeessa
                    df.at[idx, 'Kafaltii_Wal'] = new_kafaltii
                    save_data(df)
                    st.success("Galmeen milkaa'inaan fooyya'eera!")
                    st.rerun()
                
                if c2.form_submit_button("🗑️ HAQI", type="primary"):
                    df = df.drop(idx)
                    save_data(df)
                    st.warning("Galmeen haqameera!")
                    st.rerun()
        else:
            st.info("Maqaa kanaan ragaan argame hin jiru.")

# --- 5. PAGE: CERTIFICATE PAGE (Update) ---
elif choice == "🏆 Sartiifiketa":
    st.header("🏆 Beekamtii Ogeessaa")
    if not df.empty:
        best_og = df['Ogeessa'].value_counts().idxmax()
        st.success(f"Ogeessa Beekamtii Argatu: **{best_og}**")
        
        if st.button("📜 SARTIIFIKETA QOPHEESSI"):
            # 'count' irraa haqameera
            cert = generate_certificate(best_og)
            st.download_button("📥 PDF Buufadhu", cert, f"Certificate_{best_og}.pdf")
